from datetime import timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

from .authentication import get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from .models import User
from src.database.database import get_db_eng_for_app, get_session

from sqlmodel import select

from .routes import oauth

router = APIRouter(
    prefix="/auth"
)


@router.get('/redirect')
async def satosa_callback(request: Request):

    app = request.session['app']
    print("APP:", app)

    if not app:
        return HTMLResponse("<h1>OAuth session missing</h1>", status_code=400)

    db_engine = get_db_eng_for_app(app)
    db_session = get_session(db_engine)

    try:
        token = await oauth.satosa.authorize_access_token(request)
    except OAuthError as error:
        print("OAUTH ERROR:", error)
        return HTMLResponse(f'<h1>{error.error}</h1>')
    userinfo = await oauth.satosa.userinfo(token=token)

    user = db_session.exec(
        select(User).where(User.name == userinfo["name"])
    ).first()

    if not user:
        user = User(
            name=userinfo["name"],
            password_hash=get_password_hash("random"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    access_token = create_access_token(
        data={"sub": user.name},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_access_token(
        data={"sub": user.name},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )


    request.session['user'] = dict(userinfo)

    react_url = f"http://localhost:5173/redirect?token={access_token}&refresh={refresh_token}"
    response = RedirectResponse(url=react_url)
    return response

