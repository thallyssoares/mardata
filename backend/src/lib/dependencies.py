"""Authentication dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from gotrue.errors import AuthApiError

from ..lib.supabase_client import get_supabase_client
from ..models.user import User

# Scheme for bearer token authentication
bearer_scheme = HTTPBearer()

async def get_current_user(
    token: str = Depends(bearer_scheme),
    supabase = Depends(get_supabase_client)
) -> User:
    """
    Dependency to get the current user from a Supabase JWT.

    Args:
        token: The bearer token from the Authorization header.
        supabase: The Supabase client instance.

    Returns:
        The authenticated user's data.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        # get_user will validate the token and return the user
        user_response = supabase.auth.get_user(token.credentials)
        user_data = user_response.user
        
        # Adapt Supabase user object to our Pydantic model
        return User(id=user_data.id, email=user_data.email)

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e.message}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during authentication: {e}",
        )
