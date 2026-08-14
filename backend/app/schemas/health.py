from pydantic import BaseModel


class HealthLiveResponse(BaseModel):
    status: str
    service: str
    version: str


class HealthReadyResponse(BaseModel):
    status: str
    checks: dict[str, str]
