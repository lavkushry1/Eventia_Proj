from pydantic import BaseModel, Field


class TeamSchema(BaseModel):
    name: str = Field(...)
    code: str = Field(...)
    logo_url: str = Field(...)