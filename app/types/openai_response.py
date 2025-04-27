from pydantic import BaseModel
from typing import List

class OpenAiResponse(BaseModel):
    title: str
    fable: str
    moral: str
    image_prompts: List[str] 