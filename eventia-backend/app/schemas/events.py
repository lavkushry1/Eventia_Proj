from pydantic import BaseModel
from datetime import datetime
class EventSchema(BaseModel):
    title: str
    date: datetime
    venue: str
    description: str
    team_1: str
    team_2: str
    price: int
