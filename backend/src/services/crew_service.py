import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI

load_dotenv()

# Configure LLMs from OpenRouter
llm_llama_70b = ChatOpenAI(
    model="openrouter/meta-llama/llama-3.3-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

llm_qwen_coder = ChatOpenAI(
    model="openrouter/qwen/qwen-2.5-coder-32b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

llm_gemini_flash = ChatOpenAI(
    model="openrouter/deepseek/deepseek-r1-distill-llama-70b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class PandasTool(BaseTool):
    name: str = "Pandas Dataframe Tool"
    description: str = "A tool to run pandas operations on a dataframe."

    def _run(self, command: str) -> str:
        # This is a placeholder for the actual implementation
        # In a real scenario, you would have a way to access and manipulate the dataframe
        return "Pandas command executed successfully."

pandas_tool = PandasTool()

# Load agent and task definitions from YAML files
with open("backend/src/config/agents.yaml", "r") as f:
    agents_config = yaml.safe_load(f)

with open("backend/src/config/tasks.yaml", "r") as f:
    tasks_config = yaml.safe_load(f)

# Create a mapping for LLMs and tools
llm_map = {
    "llm_llama_70b": llm_llama_70b,
    "llm_qwen_coder": llm_qwen_coder,
    "llm_gemini_flash": llm_gemini_flash,
}

tools_map = {
    "pandas_tool": pandas_tool,
}

# Create Agent objects
agents = {}
for agent_name, agent_def in agents_config.items():
    agent_def["llm"] = llm_map[agent_def["llm"]]
    if "tools" in agent_def:
        agent_def["tools"] = [tools_map[tool] for tool in agent_def["tools"]]
    agents[agent_name] = Agent(**agent_def)


def run_analysis(user_prompt, statistical_summary):
    # Create Task objects
    tasks = {}
    for task_name, task_def in tasks_config.items():
        task_def["agent"] = agents[task_def["agent"]]
        if "context" in task_def:
            task_def["context"] = [tasks[context_task] for context_task in task_def["context"]]
        
        # Format the description with the user prompt and statistical summary
        task_def["description"] = task_def["description"].format(
            user_prompt=user_prompt, 
            statistical_summary=statistical_summary
        )
        
        tasks[task_name] = Task(**task_def)

    # Create and run the crew
    mardata_crew = Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=True
    )

    result = mardata_crew.kickoff()
    
    return result.raw