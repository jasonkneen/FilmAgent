from typing import Any, Dict, Optional

from pydantic import BaseModel


class ProjectStartRequest(BaseModel):
    idea: str
    file_path: Optional[str] = None
    style: Optional[str] = "realistic"
    video_ratio: Optional[str] = "9:16"
    expand_idea: Optional[bool] = True
    llm_model: Optional[str] = None
    vlm_model: Optional[str] = None
    image_t2i_model: Optional[str] = None
    image_it2i_model: Optional[str] = None
    video_model: Optional[str] = None
    enable_concurrency: Optional[bool] = True
    web_search: Optional[bool] = False
    episodes: Optional[int] = 4


class InterventionRequest(BaseModel):
    stage: str
    modifications: Dict[str, Any]
