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

# Rotator for the Orchestrator and Synthesis agents
llm_llama_70b = GroqModelRotator(models=general_purpose_models, temperature=0.7)