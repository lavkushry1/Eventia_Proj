from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class StadiumSectionBase(BaseModel):
    name: str
    capacity: int
    price: float
    view_image_url: Optional[str] = None

class StadiumSectionCreate(StadiumSectionBase):
    pass

class StadiumSectionUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    view_image_url: Optional[str] = None

class StadiumSectionResponse(StadiumSectionBase):
    id: str = Field(..., alias="_id")
    stadium_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class StadiumBase(BaseModel):
    name: str
    location: str
    capacity: int
    image_url: Optional[str] = None
    sections: List[StadiumSectionBase] = []

class StadiumCreate(StadiumBase):
    pass

class StadiumUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None
    sections: Optional[List[StadiumSectionUpdate]] = None

class StadiumResponse(StadiumBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    sections: List[StadiumSectionResponse]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class StadiumListResponse(BaseModel):
    items: List[StadiumResponse]
    total: int
    page: int
    size: int 