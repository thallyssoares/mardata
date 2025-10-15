"""Authentication routes."""
from fastapi import APIRouter, Depends
from ..models.user import User
from ..lib.dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.
    """
    return current_user
