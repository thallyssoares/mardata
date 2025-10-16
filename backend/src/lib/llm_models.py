import os
from dotenv import load_dotenv
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
