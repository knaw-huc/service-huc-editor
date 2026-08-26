from fastapi import APIRouter, Depends, HTTPException
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError


router = APIRouter(
    prefix="/auth"
)


client_id = os.getenv("CLIENT_NAME")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
well_known_url = os.getenv("WELL_KNOWN_URL")
session_secret = os.urandom(24)


oauth = OAuth()

oauth.register(
    name="satosa",
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=well_known_url,
    client_kwargs={'scope': 'openid profile email'},

)


@router.get('/redirect')
async def satosa_callback(request: Request):
    print("......welcome to the redirect.........")
    try:
        token = await oauth.satosa.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    print(f"user..........{user}")

    return HTMLResponse(f"callback endpoint works, printing user.....{user} ")
#     if user:
#         request.session['user'] = dict(user)
#     return RedirectResponse(url='/')


