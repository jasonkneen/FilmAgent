import os

from fastapi import APIRouter, HTTPException

from api.dependencies import workflow_engine
from config import settings

router = APIRouter(tags=["Sessions"])


@router.get("/api/sessions")
async def list_sessions():
    return {"sessions": workflow_engine.list_saved_sessions()}


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """直接删除历史记录（无密码控制）"""
    deleted = workflow_engine.delete_session(session_id)
    if not deleted:
        raise HTTPException(404, "Session not found")
    return {"status": "deleted", "session_id": session_id}


@router.delete("/api/sessions")
async def cleanup_orphan_files():
    """清理孤立的结果文件（无密码控制）"""
    # 获取所有 session ID
    session_ids = set()
    for f in os.listdir(workflow_engine._session_dir):
        if f.endswith('.json'):
            session_ids.add(f.replace('.json', ''))

    # 清理孤立文件
    cleaned = {"scripts": [], "images": [], "videos": []}
    result_base = settings.RESULT_DIR

    # 清理孤立剧本
    script_dir = os.path.join(result_base, 'script')
    for f in os.listdir(script_dir):
        if f.startswith('script_') and f.endswith('.json'):
            sid = f.replace('script_', '').replace('.json', '')
            if sid not in session_ids:
                os.remove(os.path.join(script_dir, f))
                cleaned["scripts"].append(sid)

    # 清理孤立图片
    image_dir = os.path.join(result_base, 'image')
    for d in os.listdir(image_dir):
        if d != 'test_avail' and d not in session_ids:
            import shutil
            shutil.rmtree(os.path.join(image_dir, d))
            cleaned["images"].append(d)

    # 清理孤立视频
    video_dir = os.path.join(result_base, 'video')
    for d in os.listdir(video_dir):
        if d != 'test_avail' and d not in session_ids:
            import shutil
            shutil.rmtree(os.path.join(video_dir, d))
            cleaned["videos"].append(d)

    return {"status": "cleaned", "cleaned": cleaned}

