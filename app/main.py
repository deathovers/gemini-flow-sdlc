from fastapi import FastAPI, HTTPException, BackgroundTasks
from app.models import ProjectState
from app.orchestrator import Orchestrator
import uuid

app = FastAPI(title="Gemini-Flow SDLC API")
orchestrator = Orchestrator()

@app.post("/v1/pipeline/start")
async def start_pipeline(prd_content: str, project_name: str):
    project_id = str(uuid.uuid4())
    state = ProjectState(
        project_id=project_id,
        project_name=project_name,
        raw_prd=prd_content,
        status="PENDING"
    )
    orchestrator.start_job(state)
    return {"job_id": project_id}

@app.get("/v1/pipeline/status/{job_id}")
async def get_status(job_id: str):
    state = orchestrator.get_status(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": state.project_id,
        "status": state.status,
        "error": state.error
    }

@app.get("/v1/artifacts/{job_id}/{artifact_type}")
async def get_artifacts(job_id: str, artifact_type: str):
    state = orchestrator.get_status(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if artifact_type.upper() == "TRD":
        return {"content": state.trd}
    elif artifact_type.upper() == "ARCHITECTURE_SPEC":
        return {"content": state.architecture_spec}
    elif artifact_type.upper() == "CODE_BUNDLE":
        return {"content": state.codebase}
    elif artifact_type.upper() == "REVIEW":
        return {"content": state.review_comments}
    else:
        raise HTTPException(status_code=400, detail="Invalid artifact type")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
