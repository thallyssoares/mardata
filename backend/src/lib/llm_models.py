import os
from dotenv import load_dotenv
from .model_rotator import GroqModelRotator

load_dotenv()

# A list of general-purpose Groq models to rotate through
general_purpose_models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gpt-oss-120b",
]

# A list of models suitable for coding tasks
coding_models = [
    "llama-3.3-70b-versatile",
    "gpt-oss-120b",
    "gpt-oss-20b",
]

# Rotator for the Orchestrator and Synthesis agents
llm_llama_70b = GroqModelRotator(models=general_purpose_models, temperature=0.7)

# Rotator for the Data Analysis agent
llm_qwen_coder = GroqModelRotator(models=coding_models, temperature=0.5)

# Rotator for the RAG agent
llm_gemini_flash = GroqModelRotator(models=general_purpose_models, temperature=0.7)