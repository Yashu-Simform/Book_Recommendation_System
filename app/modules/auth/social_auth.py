# auth_router.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import httpx
from app.core.config import settings

router = APIRouter(tags=["Auth"])

# @router.get("/google")
# def login_google():
#     params = {
#         "client_id": GOOGLE_CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": GOOGLE_REDIRECT_URI,
#         "scope": "openid email profile",
#         "access_type": "offline",
#         "prompt": "consent",
#     }
#     return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")

# @router.get("/google/callback")
# async def google_callback(code: str):
    # async with httpx.AsyncClient() as client:
    #     token_res = await client.post(
    #         GOOGLE_TOKEN_URL,
    #         data={
    #             "client_id": GOOGLE_CLIENT_ID,
    #             "client_secret": GOOGLE_CLIENT_SECRET,
    #             "code": code,
    #             "grant_type": "authorization_code",
    #             "redirect_uri": GOOGLE_REDIRECT_URI,
    #         },
    #         headers={"Content-Type": "application/x-www-form-urlencoded"},
    #     )
    #     if token_res.status_code != 200:
    #         raise HTTPException(status_code=400, detail="Google token exchange failed")

    #     access_token = token_res.json().get("access_token")

    #     userinfo_res = await client.get(
    #         GOOGLE_USERINFO_URL,
    #         headers={"Authorization": f"Bearer {access_token}"},
    #     )
    #     userinfo = userinfo_res.json()

    #     return {
    #         "provider": "google",
    #         "email": userinfo.get("email"),
    #         "first_name": userinfo.get("given_name"),
    #         "last_name": userinfo.get("family_name"),
    #         "picture": userinfo.get("picture"),
    #     }

@router.get("/github")
def login_github():
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "scope": "read:user user:email",
    }
    return RedirectResponse(f"{settings.github_auth_url}?{urlencode(params)}")

@router.get("/github/callback")
async def github_callback(code: str):
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            settings.github_token_url,
            headers=headers,
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub token exchange failed")

        access_token = token_res.json().get("access_token")

        userinfo_res = await client.get(
            settings.github_userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo = userinfo_res.json()

        return {
            "provider": "github",
            "username": userinfo.get("login"),
            "name": userinfo.get("name"),
            "email": userinfo.get("email"),
            "avatar": userinfo.get("avatar_url"),
        }
