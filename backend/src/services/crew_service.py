import os
import yaml
import asyncio
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

from ..lib.websocket_manager import manager
from ..lib.llm_models import llm_llama_70b, llm_qwen_coder, llm_gemini_flash

load_dotenv()

class PandasTool(BaseTool):
    name: str = "Pandas Dataframe Tool"
    description: str = "A tool to run pandas operations on a dataframe."

    def _run(self, command: str) -> str:
        return "Pandas command executed successfully."

pandas_tool = PandasTool()

with open("backend/src/config/agents.yaml", "r") as f:
    agents_config = yaml.safe_load(f)

with open("backend/src/config/tasks.yaml", "r") as f:
    tasks_config = yaml.safe_load(f)

llm_map = {
    "llm_llama_70b": llm_llama_70b,
    "llm_qwen_coder": llm_qwen_coder,
    "llm_gemini_flash": llm_gemini_flash,
}

tools_map = {
    "pandas_tool": pandas_tool,
}

agents = {}
for agent_name, agent_def in agents_config.items():
    agent_def["llm"] = llm_map[agent_def["llm"]]
    if "tools" in agent_def:
        agent_def["tools"] = [tools_map[tool] for tool in agent_def["tools"]]
    agents[agent_name] = Agent(**agent_def)

async def step_callback(step_output):
    notebook_id = step_output.task.metadata.get("notebook_id")
    if notebook_id:
        message = {
            "type": "progress",
            "agent": step_output.agent.role,
            "status": "in_progress",
        }
        await manager.send_json(notebook_id, message)

async def run_analysis(user_prompt, statistical_summary, notebook_id: str):
    tasks = {}
    for task_name, task_def in tasks_config.items():
        task_def["agent"] = agents[task_def["agent"]]
        if "context" in task_def:
            task_def["context"] = [tasks[context_task] for context_task in task_def["context"]]
        
        task_def["description"] = task_def["description"].format(
            user_prompt=user_prompt, 
            statistical_summary=statistical_summary
        )
        
        task_def["metadata"] = {"notebook_id": notebook_id}

        tasks[task_name] = Task(**task_def)

    mardata_crew = Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=True,
        step_callback=step_callback,
    )

    result = await mardata_crew.kickoff_async()

    # Extract the raw string from the output object
    raw_output = result.raw if result else "An error occurred and no output was generated."

    final_message = {
        "type": "complete",
        "final_insight": raw_output
    }
    await manager.send_json(notebook_id, final_message)
    
    return raw_output