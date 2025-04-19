"""Models for the test target provisioner API"""

from pydantic import BaseModel


class Report(BaseModel):
    """Model for request body to create a machine"""

    ipv4: str
    ipv6: str | None = None
