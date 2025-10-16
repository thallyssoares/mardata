"""Authentication dependencies."""
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from gotrue.errors import AuthApiError
from supabase import Client

from ..lib.supabase_client import get_supabase_client
from ..models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Scheme for bearer token authentication
bearer_scheme = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    supabase: Client = Depends(get_supabase_client), # Gets the service_role client
) -> User:
    """
    Dependency to get the current user from a JWT, validated by the service client.
    """
    logging.info("Attempting to get current user from token.")
    if not token or not token.credentials:
        logging.warning("No auth token found in request.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        # Use the service_role client to validate the user's JWT
        user_response = supabase.auth.get_user(token.credentials)
        logging.info(f"Supabase auth response: {user_response}")

        if not user_response or not user_response.user or not user_response.user.id:
            logging.warning("User not found in Supabase response. Token may be invalid or expired.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token.",
            )
        
        user_data = user_response.user
        logging.info(f"Successfully retrieved user ID: {user_data.id}")
        
        # Adapt Supabase user object to our Pydantic model
        return User(id=user_data.id, email=user_data.email)

    except AuthApiError as e:
        logging.error(f"AuthApiError in get_current_user: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e.message}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during authentication: {e}",
        )
