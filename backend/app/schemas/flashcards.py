from pydantic import BaseModel

class FlashcardRequest(BaseModel):
    goal:str
    difficulty: str
    style: str

