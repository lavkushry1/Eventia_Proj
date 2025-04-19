from pydantic import BaseModel, Field
from typing import Optional

class TeamInfo(BaseModel):
    name: str
    code: str
    color: Optional[str] = None
    secondary_color: Optional[str] = None
    home_ground: Optional[str] = None
    logo: Optional[str] = None

# Keep the original TeamSchema for backward compatibility
class TeamSchema(BaseModel):
    name: str = Field(...)
    code: str = Field(...)
    logo_url: str = Field(...)