# -*- coding: utf-8 -*-
"""
Cloud Run Proxy - simplified
"""

import base64
import httpx
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote

MARZBAN_PANEL = "https://ulinux.fastlinky.xyz:8000"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["subscription-userinfo", "profile-title", "content-disposition"],
)

client = httpx.AsyncClient(timeout=20.0, verify=False, follow_redirects=True)


def decode_token(token: str) -> str:
    try:
        return unquote(base64.urlsafe_b64decode(token + "==").decode("utf-8"))
    except Exception:
        return token


@app.get("/sub/{token}")
async def get_subscription(token: str, request: Request):
    decoded = decode_token(token)
    url = f"{MARZBAN_PANEL}/sub/{decoded}"

    try:
        r = await client.get(url, headers={"User-Agent": request.headers.get("user-agent", "")})
    except Exception as e:
        return Response(content=str(e), status_code=500)

    if r.status_code != 200:
        return Response(content="Error", status_code=r.status_code)

    return Response(
        content=r.content,
        status_code=200,
        media_type="text/plain; charset=utf-8",
        headers={
            "content-disposition": 'attachment; filename="subscription"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
