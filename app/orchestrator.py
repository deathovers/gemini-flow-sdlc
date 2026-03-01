import asyncio
from typing import Dict
from app.models import ProjectState
from app.agents.core_agents import AnalystAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent

class Orchestrator:
    def __init__(self):
        self.analyst = AnalystAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()
        self.reviewer = ReviewerAgent()
        self.jobs: Dict[str, ProjectState] = {}

    async def run_pipeline(self, project_id: str):
        state = self.jobs.get(project_id)
        if not state:
            return

        try:
            # Analyst Phase
            state.status = "ANALYZING"
            state = await self.analyst.process(state)
            
            # Architect Phase
            state = await self.architect.process(state)
            
            # Developer Phase
            state = await self.developer.process(state)
            
            # Reviewer Phase
            state = await self.reviewer.process(state)
            
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            print(f"Pipeline failed for {project_id}: {e}")

    def start_job(self, state: ProjectState):
        self.jobs[state.project_id] = state
        asyncio.create_task(self.run_pipeline(state.project_id))
        return state.project_id

    def get_status(self, project_id: str) -> ProjectState:
        return self.jobs.get(project_id)
