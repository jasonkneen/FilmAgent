import copy
import json
import os
import time
from datetime import datetime
from types import SimpleNamespace

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from api.dependencies import workflow_engine
from api.routers.files import merge_uploaded_file_into_idea
from api.schemas.project import InterventionRequest, ProjectStartRequest
from api.services.project_helpers import (
    inject_user_selections,
    make_cancellation,
    make_progress_channel,
    stream_workflow_task,
)
from config import settings

router = APIRouter(tags=["Workflow"])

REQUIRED_MODEL_FIELDS = (
    "llm_model",
    "vlm_model",
    "image_t2i_model",
    "image_it2i_model",
    "video_model",
)


def _require_model_fields(values: dict) -> None:
    missing = [field for field in REQUIRED_MODEL_FIELDS if not values.get(field)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required model configuration: {', '.join(missing)}",
        )


@router.post("/api/project/start")
async def start_project(req: ProjectStartRequest):
    final_idea = merge_uploaded_file_into_idea(req.idea, req.file_path)
    _require_model_fields(req.model_dump())

    session_id = str(int(time.time() * 1000))
    state = workflow_engine.get_or_create_state(session_id)
    meta = {
        "idea": final_idea,
        "user_textbox_input": req.idea,
        "style": req.style or getattr(settings, "STYLE", None) or "realistic",
        "video_ratio": req.video_ratio or "9:16",
        "video_resolution": req.video_resolution or "720P",
        "expand_idea": req.expand_idea if req.expand_idea is not None else True,
        "llm_model": req.llm_model,
        "vlm_model": req.vlm_model,
        "image_t2i_model": req.image_t2i_model,
        "image_it2i_model": req.image_it2i_model,
        "video_model": req.video_model,
        "enable_concurrency": req.enable_concurrency if req.enable_concurrency is not None else True,
        "web_search": req.web_search if req.web_search is not None else False,
        "episodes": req.episodes if req.episodes is not None else 4,
    }
    with workflow_engine._state_lock:
        state.started_at = datetime.now()
        if not isinstance(state.status, dict):
            state.status = {}
        state.status[state.current_stage.value] = "completed"
        state.meta = meta
        workflow_engine.save_session_to_disk(session_id, meta)

    return {
        "session_id": session_id,
        "status": copy.deepcopy(state.status),
        "params": {
            "idea": final_idea,
            "file_path": req.file_path,
            "style": req.style,
            "llm_model": meta["llm_model"],
            "vlm_model": meta["vlm_model"],
            "image_t2i_model": meta["image_t2i_model"],
            "image_it2i_model": meta["image_it2i_model"],
            "video_model": meta["video_model"],
            "episodes": meta["episodes"],
            "video_ratio": meta["video_ratio"],
            "video_resolution": meta["video_resolution"],
        }
    }


@router.post("/api/project/{session_id}/execute/{stage}")
async def execute_stage(session_id: str, stage: str, request: Request):
    state = workflow_engine.get_or_create_state(session_id)

    try:
        body = await request.json()
    except Exception:
        body = {}

    body["session_id"] = session_id
    with workflow_engine._state_lock:
        meta_snapshot = copy.deepcopy(state.meta)
        artifact_snapshot = copy.deepcopy(state.artifacts)
    if meta_snapshot:
        for k, v in meta_snapshot.items():
            if v is not None and (k not in body or not body[k]):
                body[k] = v
    _require_model_fields(body)

    state_for_input = SimpleNamespace(artifacts=artifact_snapshot)
    inject_user_selections(state_for_input, stage, body)
    cancellation_check, on_disconnect = make_cancellation(workflow_engine, session_id)
    progress_events, event_trigger, progress_callback = make_progress_channel()

    return StreamingResponse(
        stream_workflow_task(
            request=request,
            workflow_engine=workflow_engine,
            state=state,
            stage=stage,
            input_data=body,
            cancellation_check=cancellation_check,
            progress_callback=progress_callback,
            progress_events=progress_events,
            event_trigger=event_trigger,
            include_payload_summary=True,
            on_disconnect=on_disconnect,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/api/project/{session_id}/status")
async def get_project_status(session_id: str):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    with workflow_engine._state_lock:
        return state.to_dict()


@router.get("/api/project/{session_id}/status/from_disk")
async def get_project_status_from_disk(session_id: str):
    # 兼容旧前端路由名；实际读取统一走 WorkflowEngine 的内存状态入口。
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    with workflow_engine._state_lock:
        return state.to_dict()


@router.get("/api/project/{session_id}/artifact/{stage}")
async def get_artifact(session_id: str, stage: str):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")

    with workflow_engine._state_lock:
        artifact = copy.deepcopy(state.artifacts.get(stage))
    if artifact is not None:
        return {"stage": stage, "artifact": artifact}

    raise HTTPException(404, f"Artifact for stage '{stage}' not found")


@router.patch("/api/project/{session_id}/models")
async def update_models(session_id: str, request: Request):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    body = await request.json()
    allowed_keys = ("llm_model", "vlm_model", "image_t2i_model", "image_it2i_model", "video_model", "video_ratio", "video_resolution", "style", "enable_concurrency")
    with workflow_engine._state_lock:
        if not state.meta:
            state.meta = {}
        for k in allowed_keys:
            if k in body:
                state.meta[k] = body[k]
        workflow_engine.save_session_to_disk(session_id)
    return {"status": "ok"}


@router.post("/api/project/{session_id}/artifact/{stage}/upload_image")
async def upload_artifact_image(
    session_id: str,
    stage: str,
    item_type: str = Form(...),
    item_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a user-provided image into a stage artifact and persist the session."""
    try:
        return workflow_engine.upload_artifact_image(
            session_id=session_id,
            stage=stage,
            item_type=item_type,
            item_id=item_id,
            file_obj=file.file,
            filename=file.filename or "",
        )
    except KeyError:
        raise HTTPException(404, "Session not found")
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(500, detail=str(exc)) from exc


@router.patch("/api/project/{session_id}/artifact/{stage}")
async def update_artifact(session_id: str, stage: str, request: Request):
    """保存用户在某阶段的选择/修改，同时更新内存状态和磁盘快照。"""
    body = await request.json()
    try:
        return workflow_engine.update_artifact(session_id, stage, body if isinstance(body, dict) else {})
    except KeyError:
        raise HTTPException(404, "Session not found")




@router.post("/api/project/{session_id}/intervene")
async def intervene(session_id: str, req: InterventionRequest, request: Request):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")

    cancellation_check, on_disconnect = make_cancellation(workflow_engine, session_id)
    progress_events, event_trigger, progress_callback = make_progress_channel()

    with workflow_engine._state_lock:
        current_artifact = copy.deepcopy(state.artifacts.get(req.stage, {}))
        meta_snapshot = copy.deepcopy(state.meta)
        artifact_snapshot = copy.deepcopy(state.artifacts)
    input_data = current_artifact if isinstance(current_artifact, dict) else {}
    input_data["session_id"] = session_id
    if meta_snapshot:
        for k, v in meta_snapshot.items():
            if v is not None and k not in input_data:
                input_data[k] = v
    state_for_input = SimpleNamespace(artifacts=artifact_snapshot)
    inject_user_selections(state_for_input, req.stage, input_data)
    input_data.update(req.modifications)

    return StreamingResponse(
        stream_workflow_task(
            request=request,
            workflow_engine=workflow_engine,
            state=state,
            stage=req.stage,
            input_data=input_data,
            cancellation_check=cancellation_check,
            progress_callback=progress_callback,
            progress_events=progress_events,
            event_trigger=event_trigger,
            intervention=req.modifications,
            on_disconnect=on_disconnect,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/api/project/{session_id}/continue")
async def continue_workflow(session_id: str):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    return await workflow_engine.continue_workflow(session_id)


@router.post("/api/project/{session_id}/stop")
async def stop_project(session_id: str):
    workflow_engine.stop_session(session_id)
    return {"status": "stopped", "session_id": session_id}


@router.get("/api/project/{session_id}/scene/{scene_number}/assets")
async def check_scene_assets(session_id: str, scene_number: int):
    state = workflow_engine.get_state(session_id)
    with workflow_engine._state_lock:
        artifacts_snapshot = copy.deepcopy(state.artifacts) if state else {}
    result_file = os.path.join(settings.RESULT_DIR, 'script', f'{session_id}.json')
    if not os.path.exists(result_file):
        return {"scene_number": scene_number, "reference_images": 0, "videos": 0}

    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    if isinstance(results, dict):
        script_data = results.get(session_id, results) if results.get(session_id) else results
    else:
        script_data = next((item for item in results if isinstance(item, dict) and item.get("session_id") == session_id), {})

    storyboard = script_data.get('storyboard', {})
    if not storyboard:
        storyboard = results.get('storyboard', {}) if isinstance(results, dict) else {}

    shots = storyboard.get('shots', [])
    scene_shots = [s for s in shots if s.get('scene_number') == scene_number]
    shot_ids = [s.get('shot_id') for s in scene_shots if s.get('shot_id')]

    ref_artifact = script_data.get('reference_generation', {})
    if not ref_artifact:
        ref_artifact = artifacts_snapshot.get('reference_generation', {})

    ref_scenes = ref_artifact.get('scenes', []) if isinstance(ref_artifact, dict) else []
    ref_image_count = 0
    for sc in ref_scenes:
        if sc.get('id') in shot_ids:
            selected = sc.get('selected')
            if selected and os.path.exists(os.path.join(settings.CODE_DIR, selected.lstrip('/'))):
                ref_image_count += 1
            versions = sc.get('versions', [])
            for v in versions:
                if v and os.path.exists(os.path.join(settings.CODE_DIR, v.lstrip('/'))):
                    ref_image_count += 1

    video_artifact = script_data.get('video_generation', {})
    if not video_artifact:
        video_artifact = artifacts_snapshot.get('video_generation', {})

    video_clips = video_artifact.get('clips', []) if isinstance(video_artifact, dict) else []
    video_count = 0
    for vc in video_clips:
        if vc.get('id') in shot_ids:
            selected = vc.get('selected')
            if selected and os.path.exists(os.path.join(settings.CODE_DIR, selected.lstrip('/'))):
                video_count += 1

    return {
        "scene_number": scene_number,
        "reference_images": ref_image_count,
        "videos": video_count,
        "shot_count": len(scene_shots),
    }
