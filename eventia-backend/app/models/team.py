from odmantic import Document, Field



class Team(Document):
    name: str = Field(...)
    code: str = Field(...)
    logo_url: str = Field(...)