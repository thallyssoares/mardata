
import os
import yaml
import asyncio
from typing import Any, Dict, List
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from crewai.tasks.task_output import TaskOutput

from ..lib.websocket_manager import manager
from ..lib.llm_models import llm_llama_70b, llm_qwen_coder, llm_gemini_flash

load_dotenv()

# --- Tools ---
class PandasTool(BaseTool):
    name: str = "Pandas Dataframe Tool"
    description: str = "A tool to run pandas operations on a dataframe."

    def _run(self, command: str) -> str:
        # This is a placeholder. In a real scenario, you would have a secure
        # way to execute pandas commands on the loaded dataframe.
        return "Pandas command executed successfully. (Simulated)"

pandas_tool = PandasTool()

# --- Config Loading ---
with open("backend/src/config/agents.yaml", "r", encoding="utf-8") as f:
    agents_config = yaml.safe_load(f)

with open("backend/src/config/tasks.yaml", "r", encoding="utf-8") as f:
    tasks_config = yaml.safe_load(f)

# --- Mappings ---
llm_map = {
    "llm_llama_70b": llm_llama_70b,
    "llm_qwen_coder": llm_qwen_coder,
    "llm_gemini_flash": llm_gemini_flash,
}
tools_map = {"pandas_tool": pandas_tool}

# --- WebSocket Callback Handler ---
class WebSocketCallbackHandler:
    def __init__(self, notebook_id: str):
        self.notebook_id = notebook_id
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def _send_message_sync(self, message: Dict[str, Any]):
        """Sends a message to the WebSocket from a synchronous context."""
        future = asyncio.run_coroutine_threadsafe(
            manager.send_json(self.notebook_id, message), self.loop
        )
        try:
            future.result(timeout=5)
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")

    def on_task_start(self, task: Task):
        self._send_message_sync({
            "type": "progress",
            "agent": task.agent.role,
            "status": f"Iniciando tarefa: {task.description}",
        })

    def on_task_end(self, task: Task, output: TaskOutput):
        self._send_message_sync({
            "type": "progress",
            "agent": task.agent.role,
            "status": "Tarefa finalizada.",
        })

# --- Agent and Task Initialization ---
agents = {}
for agent_name, agent_def in agents_config.items():
    agent_def["llm"] = llm_map[agent_def["llm"]]
    if "tools" in agent_def:
        agent_def["tools"] = [tools_map[tool] for tool in agent_def["tools"]]
    agents[agent_name] = Agent(**agent_def)

# --- Main Analysis Function ---
async def run_analysis(user_prompt: str, statistical_summary: str, notebook_id: str):
    """
    Runs the CrewAI analysis and streams progress over WebSocket.
    """
    callback_handler = WebSocketCallbackHandler(notebook_id=notebook_id)
    
    tasks = {}
    for task_name, task_def in tasks_config.items():
        agent = agents[task_def["agent"]]
        context_tasks = [tasks[ctx] for ctx in task_def.get("context", [])]
        
        formatted_description = task_def["description"].format(
            user_prompt=user_prompt, 
            statistical_summary=statistical_summary
        )
        
        new_task = Task(
            description=formatted_description,
            expected_output=task_def["expected_output"],
            agent=agent,
            context=context_tasks,
            callbacks=[callback_handler] # Attach the handler to the task
        )
        tasks[task_name] = new_task

    mardata_crew = Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=True,
        max_tokens=10000, # Set a conservative token limit for testing
    )

    # Run the crew kickoff in a separate thread to avoid blocking
    result = await mardata_crew.kickoff_async()
    raw_output = result.raw if result else "A análise não gerou um resultado final."

    # Send the final completion message
    final_message = {
        "type": "complete",
        "final_insight": raw_output
    }
    await manager.send_json(notebook_id, final_message)
    
    return raw_output
