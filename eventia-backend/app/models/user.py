from odmantic import Document, Field
from pydantic import EmailStr

class User(Document):
    """Model for users."""
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

