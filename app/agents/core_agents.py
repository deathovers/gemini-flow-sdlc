from app.utils.gemini_client import GeminiClient
from app.models import ProjectState, ArchitectureSpec
import json

class BaseAgent:
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.client = GeminiClient(model_name=model_name)

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("Analyst", "gemini-1.5-pro")

    async def process(self, state: ProjectState) -> ProjectState:
        print(f"[{self.name}] Analyzing PRD...")
        prompt = f"Transform the following PRD into a structured TRD (Technical Requirement Document) in Markdown format:\n\n{state.raw_prd}"
        state.trd = await self.client.generate(prompt)
        state.status = "ARCHITECTING"
        return state

class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("Architect", "gemini-1.5-pro")

    async def process(self, state: ProjectState) -> ProjectState:
        print(f"[{self.name}] Designing Architecture...")
        prompt = f"""Based on the following TRD, produce a system design in JSON format that matches this schema:
        {{
            "tech_stack": ["list of strings"],
            "file_structure": ["list of paths"],
            "api_definitions": [{{ "path": "...", "method": "...", "description": "..." }}],
            "data_models": [{{ "name": "...", "fields": {{}} }}],
            "logic_requirements": "string"
        }}
        
        TRD:
        {state.trd}
        """
        response = await self.client.generate(prompt)
        # Basic JSON extraction (assuming Gemini returns clean JSON or markdown block)
        clean_json = response.strip().replace("```json", "").replace("```", "")
        state.architecture_spec = ArchitectureSpec.parse_raw(clean_json)
        state.status = "DEVELOPING"
        return state

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__("Developer", "gemini-1.5-flash")

    async def process(self, state: ProjectState) -> ProjectState:
        print(f"[{self.name}] Generating Code...")
        codebase = {}
        for file_path in state.architecture_spec.file_structure:
            prompt = f"""Write the code for the file '{file_path}' based on the following architecture:
            Tech Stack: {state.architecture_spec.tech_stack}
            API Definitions: {state.architecture_spec.api_definitions}
            Data Models: {state.architecture_spec.data_models}
            Logic: {state.architecture_spec.logic_requirements}
            
            Return ONLY the code for this specific file.
            """
            code = await self.client.generate(prompt)
            codebase[file_path] = code
        
        state.codebase = codebase
        state.status = "REVIEWING"
        return state

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reviewer", "gemini-1.5-flash")

    async def process(self, state: ProjectState) -> ProjectState:
        print(f"[{self.name}] Reviewing Code...")
        # Pass the entire context
        context = f"TRD: {state.trd}\n\nArchitecture: {state.architecture_spec.json()}\n\nCodebase: {json.dumps(state.codebase)}"
        prompt = f"Review the following codebase against the TRD and Architecture. Provide a list of comments or 'PASSED'.\n\n{context}"
        
        review = await self.client.generate(prompt)
        state.review_comments = [review]
        state.status = "COMPLETED"
        return state
