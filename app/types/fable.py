from typing import List, Optional
from pydantic import BaseModel

class FableRequest(BaseModel):
    """
    Request model for fable generation.
    """
    world_description: str
    main_character: str
    age: int
    num_images: Optional[int] = 2

    class Config:
        json_schema_extra = {
            "example": {
                "world_description": "A magical forest with talking trees and sparkling streams",
                "main_character": "A wise old owl named Professor Hoot",
                "age": 8,
                "num_images": 2
            }
        }

class IllustrationResponse(BaseModel):
    prompt: str
    image: str

class FableResponse(BaseModel):
    """
    Response model for generated fable.
    """
    fable: str
    moral: str
    illustrations: List[IllustrationResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "fable": "Once upon a time in a magical forest...",
                "moral": "Always be kind to others",
                "illustrations": [
                    {"prompt": "A wise owl sitting on a branch in a magical forest at sunset", "image": "<base64string1>"},
                    {"prompt": "A wise owl speaking to a group of children in a classroom", "image": "<base64string2>"}
                ]
            }
        }
