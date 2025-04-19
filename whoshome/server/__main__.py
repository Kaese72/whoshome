"""Script file for the test target provisioner"""

import dataclasses
import datetime
import logging
import os
import sys
from typing import Any

import ecs_logging
import flask_pydantic
import jwt
import urllib3
from flask import Flask, request

from whoshome.server.authentication import JWTClaims
from whoshome.server.models import Report


urllib3.disable_warnings()


@dataclasses.dataclass
class Config:
    """Config for the service"""

    jwt_secret: str


ROOT_LOGGER = logging.getLogger()
ROOT_HANDLER = logging.StreamHandler(sys.stdout)
ROOT_HANDLER.setFormatter(ecs_logging.StdlibFormatter())
# Ignore all logs from the atlassian module since they are pretty useless
ROOT_LOGGER.addHandler(ROOT_HANDLER)

APP = Flask(__name__)

CONFIG = Config(jwt_secret=os.environ["JWT_SECRET"])

CACHE: dict[str, list[tuple[datetime.datetime, Report]]] = {}


def token_required() -> tuple[str, int] | JWTClaims:
    if "Authorization" not in request.headers:
        return "Missing authentication", 401

    token = request.headers["Authorization"].removeprefix("bearer ")
    if not token:
        return "Authentication Token is missing!", 401

    try:
        return JWTClaims.validate(token=token, secret=CONFIG.jwt_secret)

    except jwt.InvalidSignatureError as exc:
        logging.info("Invalid signature on token", exc_info=exc)
        return "invalid token", 403

    except Exception as exc:
        logging.error("Exception when dealing with token", exc_info=exc)
        return "something went wrong", 500


@APP.route("/report", methods=["POST"])
@flask_pydantic.validate()
def report(body: Report) -> tuple[str, int]:
    """Reports being present at an IP"""
    claims = token_required()
    if isinstance(claims, tuple):
        return claims

    if claims.identifier not in CACHE:
        CACHE[claims.identifier] = []

    CACHE[claims.identifier].append(
        (
            datetime.datetime.now(tz=datetime.timezone.utc),
            body,
        )
    )
    if len(CACHE[claims.identifier]) > 3:
        CACHE[claims.identifier].pop(0)

    return ("", 200)


@APP.route("/token/<identifier>", methods=["GET"])
@flask_pydantic.validate()
def new_token(identifier: str) -> tuple[str, int]:
    """Print a token for a new reporter"""
    claims = token_required()
    if isinstance(claims, tuple):
        return claims

    if not claims.admin:
        return ("Forbidden", 403)

    token = JWTClaims(admin=False, identifier=identifier).token(CONFIG.jwt_secret)
    return token, 200


@APP.route("/list", methods=["GET"])
@flask_pydantic.validate()
def list_() -> tuple[Any, int]:
    """Lists all machines visible to this provisioner"""
    claims = token_required()
    if isinstance(claims, tuple):
        return claims

    if not claims.admin:
        return ("Forbidden", 403)

    converted: dict[str, list[list[Any]]] = {}
    for identifer, reports in CACHE.items():
        converted[identifer] = []
        for r_time, r_report in reports:
            converted[identifer].append([str(r_time), r_report.model_dump()])

    return (converted, 200)


if __name__ == "__main__":
    with open("admin.generated.token.txt", "w", encoding="utf-8") as file_handle:
        file_handle.write(
            JWTClaims(admin=True, identifier="root").token(secret=CONFIG.jwt_secret)
        )
    # Not recommended in Production, but we do not consider this to be Production
    APP.run(host="0.0.0.0", port=8000, threaded=True)
