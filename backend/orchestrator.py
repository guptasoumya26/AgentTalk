from typing import List, Dict, Optional
from backend.agents import ChatGPTAgent, GeminiAgent, GroqAgent
from backend.config_loader import ConfigLoader

class Orchestrator:
    def __init__(self):
        self.config = ConfigLoader()
        self.agents = {}
        self.conversation_history = []
        self.project_state = {
            "phase": "planning",
            "artifacts": {}
        }
        self._initialize_agents()

    def _initialize_agents(self):
        if self.config.get('OPENAI_API_KEY'):
            self.agents['chatgpt'] = ChatGPTAgent(
                api_key=self.config.get('OPENAI_API_KEY'),
                model=self.config.get('OPENAI_MODEL')
            )

        if self.config.get('GOOGLE_API_KEY'):
            self.agents['gemini'] = GeminiAgent(
                api_key=self.config.get('GOOGLE_API_KEY'),
                model=self.config.get('GOOGLE_MODEL')
            )

        if self.config.get('GROQ_API_KEY'):
            self.agents['groq'] = GroqAgent(
                api_key=self.config.get('GROQ_API_KEY'),
                model=self.config.get('GROQ_MODEL')
            )

    def get_available_agents(self) -> List[str]:
        return list(self.agents.keys())

    def add_message(self, agent_name: str, message: str):
        self.conversation_history.append({
            "agent": agent_name,
            "role": self.agents.get(agent_name).role if agent_name in self.agents else "User",
            "message": message,
            "timestamp": self._get_timestamp()
        })

    def call_agent(self, agent_name: str, prompt: str) -> Dict:
        if agent_name not in self.agents:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not available. Available agents: {self.get_available_agents()}"
            }

        agent = self.agents[agent_name]

        response = agent.call(prompt, self.conversation_history)

        self.add_message(agent_name, response)

        return {
            "success": True,
            "agent": agent_name,
            "role": agent.role,
            "response": response,
            "conversation": self.conversation_history
        }

    def run_sequential_workflow(self, user_request: str) -> List[Dict]:
        workflow_steps = []

        self.add_message("User", user_request)

        agent_sequence = [
            ("chatgpt", f"As a Product Manager, analyze this request and create a detailed technical specification with key features and tech stack recommendations: {user_request}"),
            ("gemini", "As a Full-Stack Developer, based on the specification above, write actual code snippets for the key components. Include both frontend (HTML/JS) and backend (Python/Node.js) code. Keep each code block concise but functional."),
            ("groq", "As a QA Engineer, review the specification and code above. Suggest test cases, potential bugs to watch for, and quality improvements. Provide examples of unit tests if applicable.")
        ]

        for agent_name, task in agent_sequence:
            if agent_name in self.agents:
                result = self.call_agent(agent_name, task)
                workflow_steps.append(result)

        return workflow_steps

    def run_round_robin_discussion(self, topic: str, rounds: int = 2) -> List[Dict]:
        discussion_steps = []

        self.add_message("User", f"Discussion topic: {topic}")

        available = self.get_available_agents()

        for round_num in range(rounds):
            for agent_name in available:
                if round_num == 0:
                    prompt = f"Share your perspective on: {topic}"
                else:
                    prompt = f"Respond to the previous comments and add your thoughts."

                result = self.call_agent(agent_name, prompt)
                discussion_steps.append(result)

        return discussion_steps

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history

    def reset(self):
        self.conversation_history = []
        self.project_state = {
            "phase": "planning",
            "artifacts": {}
        }

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def get_status(self) -> Dict:
        return {
            "available_agents": [
                {
                    "name": name,
                    "role": agent.role,
                    "model": agent.model
                }
                for name, agent in self.agents.items()
            ],
            "conversation_length": len(self.conversation_history),
            "project_phase": self.project_state["phase"]
        }
