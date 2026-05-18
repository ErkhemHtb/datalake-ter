from __future__ import annotations

import os
from urllib.parse import urljoin, urlparse, urlunparse

import requests


DEFAULT_ATLAS_URL = "http://localhost:21000/api/atlas/v2"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
TIMEOUT_SECONDS = 60


def get_config_atlas() -> dict:
    api_url = os.getenv("ATLAS_URL", DEFAULT_ATLAS_URL).rstrip("/")
    parsed_url = urlparse(api_url)
    server_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))

    return {
        "api_url": api_url,
        "server_url": server_url,
        "username": os.getenv("ATLAS_USERNAME", DEFAULT_USERNAME),
        "password": os.getenv("ATLAS_PASSWORD", DEFAULT_PASSWORD),
    }


def _auth() -> tuple[str, str]:
    config = get_config_atlas()
    return config["username"], config["password"]


def _json_or_text(response: requests.Response):
    if not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        return response.text


def _url(endpoint: str) -> str:
    config = get_config_atlas()
    base_url = config["api_url"] + "/"
    return urljoin(base_url, endpoint.lstrip("/"))


def requete_get(endpoint: str, params: dict | None = None):
    try:
        response = requests.get(
            _url(endpoint),
            auth=_auth(),
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _json_or_text(response)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"erreur GET Atlas: {error}") from error


def requete_post(endpoint: str, data: dict | list | None = None):
    try:
        response = requests.post(
            _url(endpoint),
            auth=_auth(),
            json=data,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _json_or_text(response)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"erreur POST Atlas: {error}") from error


def requete_delete(endpoint: str):
    try:
        response = requests.delete(
            _url(endpoint),
            auth=_auth(),
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _json_or_text(response)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"erreur DELETE Atlas: {error}") from error


def verifier_connexion():
    config = get_config_atlas()
    version_url = f"{config['server_url']}/api/atlas/admin/version"

    try:
        response = requests.get(
            version_url,
            auth=(config["username"], config["password"]),
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _json_or_text(response)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"connexion Atlas impossible: {error}") from error
