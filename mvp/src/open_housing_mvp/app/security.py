"""Sécurité API par clé (US-15)."""

import os

from fastapi import Header, HTTPException, status

from .. import config


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get(config.API_KEY_ENV_VAR, "change-me")
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante (en-tête X-API-Key requis)",
        )
