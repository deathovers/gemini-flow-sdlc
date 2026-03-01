from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ArchitectureSpec(BaseModel):
    tech_stack: List[str]
    file_structure: List[str]
    api_definitions: List[Dict[str, Any]]
    data_models: List[Dict[str, Any]]
    logic_requirements: Optional[str] = None

class ProjectState(BaseModel):
    project_id: str
    project_name: str
    raw_prd: str
    trd: Optional[str] = None
    architecture_spec: Optional[ArchitectureSpec] = None
    codebase: Optional[Dict[str, str]] = {}  # Map of filepath: content
    review_comments: Optional[List[str]] = []
    status: str = "PENDING"
    error: Optional[str] = None
