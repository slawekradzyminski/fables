from pydantic import BaseModel
from typing import List

class OpenAiResponse(BaseModel):
    fable: str
    moral: str
    image_prompts: List[str] 