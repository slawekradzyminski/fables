from pydantic import BaseModel

class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    """
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy"
            }
        } 