"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from supabase import Client
from gotrue.errors import AuthApiError

from ..models.user import User
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client



router = APIRouter()



class Token(BaseModel):

    access_token: str

    token_type: str

    refresh_token: str



@router.post("/token", response_model=Token)

async def login_for_access_token(

    form_data: OAuth2PasswordRequestForm = Depends(),

    supabase: Client = Depends(get_supabase_client) # Use service role client for login

):

    """

    Logs in a user with email and password, returns a session token.

    """

    try:

        response = supabase.auth.sign_in_with_password({

            "email": form_data.username,

            "password": form_data.password

        })

        return {

            "access_token": response.session.access_token,

            "token_type": "bearer",

            "refresh_token": response.session.refresh_token

        }

    except AuthApiError as e:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=e.message or "Incorrect email or password",

            headers={"WWW-Authenticate": "Bearer"},

        )



@router.post("/logout")

async def logout(

    supabase: Client = Depends(get_supabase_client) # Use service role client for logout

):

    """

    Logs out the current user by invalidating the session token.

    """

    try:

        supabase.auth.sign_out()

        return {"message": "Successfully logged out"}

    except AuthApiError as e:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=e.message or "Logout failed"

        )





@router.get("/me", response_model=User)

async def read_users_me(current_user: User = Depends(get_current_user)):

    """

    Get the current authenticated user.

    """

    return current_user