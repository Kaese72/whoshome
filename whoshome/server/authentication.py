"""Helpers for JWT stuff"""

import dataclasses

import jwt


@dataclasses.dataclass
class JWTClaims:
    """Helper class for validating JWT tokens"""

    admin: bool
    identifier: str

    def token(self, secret: str) -> str:
        """Creates a token from the claims and a secret"""
        new_token = jwt.encode(
            payload={
                "admin": self.admin,
                "identifier": self.identifier,
            },
            key=secret,
            algorithm="HS256",
        )
        return new_token

    @classmethod
    def validate(cls, token: str, secret: str) -> "JWTClaims":
        """Validates a token given a secret"""
        decoded = jwt.decode(jwt=token, key=secret, algorithms=["HS256"])
        return cls(
            admin=decoded["admin"],
            identifier=decoded["identifier"],
        )
