"""Supabase client initialization."""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_ANON_KEY")

# Check if the credentials are set
if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and Key must be set in the environment variables.")

# Initialize the Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

def get_supabase_client() -> Client:
    """
    Returns the initialized Supabase client.

    Returns:
        Client: The Supabase client instance.
    """
    return supabase
