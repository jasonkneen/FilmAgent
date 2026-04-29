import json
import os
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
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


@router.post("/api/project/start")
async def start_project(req: ProjectStartRequest):
    final_idea = merge_uploaded_file_into_idea(req.idea, req.file_path)

    session_id = str(int(time.time() * 1000))
    state = workflow_engine.get_or_create_state(session_id)
    state.started_at = datetime.now()
    if not isinstance(state.status, dict):
        state.status = {}
    state.status[state.current_stage.value] = "completed"

    meta = {
        "idea": final_idea,
        "user_textbox_input": req.idea,
        "style": req.style or "realistic",
        "video_ratio": req.video_ratio or "9:16",
        "expand_idea": req.expand_idea if req.expand_idea is not None else True,
        "llm_model": req.llm_model or settings.LLM_MODEL,
        "vlm_model": req.vlm_model or settings.VLM_MODEL,
        "image_t2i_model": req.image_t2i_model or settings.IMAGE_T2I_MODEL,
        "image_it2i_model": req.image_it2i_model or settings.IMAGE_IT2I_MODEL,
        "video_model": req.video_model or settings.VIDEO_MODEL,
        "enable_concurrency": req.enable_concurrency if req.enable_concurrency is not None else True,
        "web_search": req.web_search if req.web_search is not None else False,
        "episodes": req.episodes if req.episodes is not None else 4,
    }
    state.meta = meta
    workflow_engine.save_session_to_disk(session_id, meta)

    return {
        "session_id": session_id,
        "status": state.status,
        "params": {
            "idea": final_idea,
            "file_path": req.file_path,
            "style": req.style,
            "llm_model": req.llm_model,
            "vlm_model": req.vlm_model,
            "episodes": req.episodes,
            "video_ratio": req.video_ratio,
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
    if state.meta:
        for k, v in state.meta.items():
            if v is not None and (k not in body or not body[k]):
                body[k] = v

    inject_user_selections(state, stage, body)
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
    return state.to_dict()


@router.get("/api/project/{session_id}/status/from_disk")
async def get_project_status_from_disk(session_id: str):
    session_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'code', 'data', 'sessions')
    session_file = os.path.join(session_dir, f"{session_id}.json")
    if not os.path.exists(session_file):
        raise HTTPException(404, "Session not found")
    with open(session_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.get("/api/project/{session_id}/artifact/{stage}")
async def get_artifact(session_id: str, stage: str):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    artifact = state.artifacts.get(stage)
    if artifact is None:
        raise HTTPException(404, f"Artifact for stage '{stage}' not found")
    return {"stage": stage, "artifact": artifact}


@router.patch("/api/project/{session_id}/models")
async def update_models(session_id: str, request: Request):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    body = await request.json()
    allowed_keys = ("llm_model", "vlm_model", "image_t2i_model", "image_it2i_model", "video_model", "video_ratio", "enable_concurrency")
    if not state.meta:
        state.meta = {}
    for k in allowed_keys:
        if k in body:
            state.meta[k] = body[k]
    workflow_engine.save_session_to_disk(session_id)
    return {"status": "ok"}


@router.patch("/api/project/{session_id}/artifact/{stage}")
async def update_artifact(session_id: str, stage: str, request: Request):
    """保存用户在某阶段的选择/修改

    数据存储策略：
    - 用户修改只保存到 sessions json（state.artifacts）
    - result/script json 只作为 LLM 初始生成，不接受用户修改

    按阶段分类处理：
    - 第二阶段(character_design): 修改 characters[]/settings[] 的 description
    - 第三阶段(storyboard): 修改 shots[] 的 duration/plot/visual_prompt
    - 第四阶段(reference_generation): 修改 scenes[] 的 description（视觉提示词）
    - 第五阶段(video_generation): 修改 clips[] 的 duration/description
    """
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    body = await request.json()

    # ══════════════════════════════════════════════════════════════
    # 第二阶段：角色/背景描述修改
    # 修改 characters[].description 或 settings[].description
    # 不涉及跨阶段同步
    # ══════════════════════════════════════════════════════════════
    if stage == "character_design":
        # 直接更新 body，由后续逻辑合并到 artifact
        pass

    # ══════════════════════════════════════════════════════════════
    # 第三阶段：分镜修改
    # 修改 payload.shots[].duration / payload.shots[].plot / payload.shots[].visual_prompt
    # 同步到：video_generation.clips[].duration, video_generation.clips[].description
    # ══════════════════════════════════════════════════════════════
    elif stage == "storyboard" and "shots" in body:
        # 清除 is_new 标记（确认新分镜）
        for shot in body['shots']:
            if 'is_new' in shot:
                shot['is_new'] = False

        # 从 body['segments'] 提取同步信息（修改后的逻辑按 segment 同步）
        seg_info_list = []
        for seg in body.get('segments', []):
            seg_id = seg.get('segment_id')
            if not seg_id: continue
            
            shots = seg.get('shots', [])
            desc_video = " ".join([sh.get("plot") or sh.get("content") or "" for sh in shots]).strip()
            total_dur = seg.get("total_duration") or sum([sh.get("duration", 0) for sh in shots]) or 10
            
            seg_info_list.append({
                "segment_id": seg_id,
                "desc": desc_video,
                "duration": total_dur
            })

        # 同步到 video_generation
        video_art = state.artifacts.get('video_generation', {})
        if isinstance(video_art, dict) and 'clips' in video_art:
            for clip in video_art['clips']:
                c_id = clip.get('id')
                # 匹配 segment_id
                target = next((item for item in seg_info_list if item["segment_id"] == c_id), None)
                if target:
                    clip['duration'] = target['duration']
                    clip['description'] = target['desc']

        # 移除 segments，避免覆盖 storyboard artifact
        body = {k: v for k, v in body.items() if k != "segments"}

        # 清除 new_shot_ids 标记
        if "new_shot_ids" in body:
            del body['new_shot_ids']

    # ══════════════════════════════════════════════════════════════
    # 第四阶段：参考图提示词修改
    # 修改 scenes[].description（视觉提示词）
    # 同步到：storyboard.shots[].visual_prompt
    # ══════════════════════════════════════════════════════════════
    elif stage == "reference_generation":
        if "segments" in body:
            # 修改视觉提示词 → 同步到 storyboard
            # body.segments 是 [{segment_id: "...", visual_prompt: "..."}]
            seg_id_to_prompt = {s['segment_id']: s.get('visual_prompt', '')
                                for s in body['segments'] if 'segment_id' in s}

            storyboard_art = state.artifacts.get('storyboard', {})
            # storyboard 结构: {episodes: [{segments: [...]}]}
            if isinstance(storyboard_art, dict):
                episodes = storyboard_art.get('episodes', [])
                for ep in episodes:
                    if isinstance(ep, dict):
                        for seg in ep.get('segments', []):
                            if isinstance(seg, dict):
                                seg_id = seg.get('segment_id')
                                if seg_id in seg_id_to_prompt:
                                    seg['visual_prompt'] = seg_id_to_prompt[seg_id]

            # 同步到 reference_generation.scenes 的 description
            ref_art = state.artifacts.get('reference_generation', {})
            if isinstance(ref_art, dict):
                scenes = ref_art.get('scenes', [])
                for scene in scenes:
                    if isinstance(scene, dict):
                        scene_id = scene.get('id')
                        if scene_id in seg_id_to_prompt:
                            scene['description'] = seg_id_to_prompt[scene_id]

            # 移除 segments，避免覆盖 reference_generation artifact
            body = {k: v for k, v in body.items() if k != "segments"}

        # 处理图片版本选择 {sceneId: path}
        ref_art = state.artifacts.get('reference_generation', {})
        if isinstance(ref_art, dict):
            scenes = ref_art.get('scenes', [])
            is_selection_format = any(
                isinstance(k, str) and not isinstance(v, (list, dict))
                for k, v in body.items()
            )
            if is_selection_format and scenes:
                for scene in scenes:
                    scene_id = scene.get('id')
                    if scene_id and scene_id in body:
                        scene['selected'] = body[scene_id]
                body = {}

    # ══════════════════════════════════════════════════════════════
    # 第五阶段：视频片段修改
    # 修改 clips[].duration / clips[].description
    # 同步到：storyboard.shots[].duration / storyboard.shots[].plot
    # ══════════════════════════════════════════════════════════════
    elif stage == "video_generation":
        # 收集 clips 的修改
        clip_id_to_duration = {}
        clip_id_to_description = {}

        for clip_id, value in body.items():
            if isinstance(value, dict):
                if 'duration' in value:
                    clip_id_to_duration[clip_id] = value['duration']
                if 'description' in value:
                    clip_id_to_description[clip_id] = value['description']

        # 同步到 storyboard 和 video_generation.clips
        if clip_id_to_duration or clip_id_to_description:
            storyboard_art = state.artifacts.get('storyboard', {})
            # storyboard 结构: 从 shots 变更为了 episodes -> segments
            if isinstance(storyboard_art, dict):
                episodes = storyboard_art.get('episodes', [])
                for ep in episodes:
                    if isinstance(ep, dict):
                        for seg in ep.get('segments', []):
                            if isinstance(seg, dict):
                                seg_id = seg.get('segment_id')
                                if seg_id in clip_id_to_duration:
                                    seg['total_duration'] = clip_id_to_duration[seg_id]

            # 更新 video_generation.clips 的 duration 和 description
            vid_art = state.artifacts.get('video_generation', {})
            if isinstance(vid_art, dict):
                clips = vid_art.get('clips', [])
                for clip in clips:
                    if isinstance(clip, dict):
                        clip_id = clip.get('id')
                        if clip_id in clip_id_to_duration:
                            clip['duration'] = clip_id_to_duration[clip_id]
                        if clip_id in clip_id_to_description:
                            clip['description'] = clip_id_to_description[clip_id]

        # 处理视频版本选择 {clipId: path}
        vid_art = state.artifacts.get('video_generation', {})
        if isinstance(vid_art, dict):
            clips = vid_art.get('clips', [])
            is_selection_format = any(
                isinstance(k, str) and not isinstance(v, (list, dict))
                for k, v in body.items()
            )
            if is_selection_format and clips:
                for clip in clips:
                    clip_id = clip.get('id')
                    if clip_id and clip_id in body:
                        clip['selected'] = body[clip_id]
                body = {}

    # 更新 state.artifacts 并保存到 sessions json
    current = state.artifacts.get(stage)
    if current is None:
        state.artifacts[stage] = body
    elif isinstance(current, dict):
        current.update(body)
    else:
        state.artifacts[stage] = body

    workflow_engine.save_session_to_disk(session_id)

    return {"status": "ok"}




@router.post("/api/project/{session_id}/intervene")
async def intervene(session_id: str, req: InterventionRequest, request: Request):
    state = workflow_engine.get_state(session_id)
    if not state:
        raise HTTPException(404, "Session not found")

    cancellation_check, on_disconnect = make_cancellation(workflow_engine, session_id)
    progress_events, event_trigger, progress_callback = make_progress_channel()

    current_artifact = state.artifacts.get(req.stage, {})
    input_data = current_artifact if isinstance(current_artifact, dict) else {}
    input_data["session_id"] = session_id
    if state.meta:
        for k, v in state.meta.items():
            if v is not None and k not in input_data:
                input_data[k] = v
    inject_user_selections(state, req.stage, input_data)
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
    result_file = os.path.join(settings.RESULT_DIR, 'script', f'script_{session_id}.json')
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
    if not ref_artifact and state:
        ref_artifact = state.artifacts.get('reference_generation', {})

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
    if not video_artifact and state:
        video_artifact = state.artifacts.get('video_generation', {})

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
