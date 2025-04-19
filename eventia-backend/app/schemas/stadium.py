from pydantic import BaseModel


class StadiumSchema(BaseModel):
    """Stadium schema for data validation."""

    name: str
    location: str
    capacity: int
    image_url: str

from pydantic import BaseModel
    
    
    