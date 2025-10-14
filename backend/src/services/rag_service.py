
import os
from pathlib import Path

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"

def retrieve_knowledge(query: str) -> str:
    """
    (Simulated RAG) Retrieves context from the knowledge base.

    Scans the knowledge_base directory for files whose names are mentioned
    in the user's query and returns their content.

    Args:
        query: The user's business problem or question.

    Returns:
        A string containing the concatenated content of relevant articles.
    """
    retrieved_docs = []
    query_lower = query.lower()

    if not KNOWLEDGE_BASE_DIR.exists():
        return "Knowledge base not found."

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        # Check if the file name (without extension) is in the query
        article_name = Path(filename).stem
        if article_name in query_lower:
            try:
                with open(KNOWLEDGE_BASE_DIR / filename, 'r') as f:
                    content = f.read()
                    retrieved_docs.append(f"--- Context on {article_name.upper()} ---\n{content}")
            except Exception as e:
                print(f"Error reading knowledge base file {filename}: {e}")
    
    return "\n\n".join(retrieved_docs)
