from typing import Dict

# In-memory store for analysis sessions.
# This is imported by other modules to share state.
sessions: Dict[str, Dict] = {}
