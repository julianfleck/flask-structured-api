from sqlmodel import SQLModel


class BaseResponseModel(SQLModel):
    """Base model for API responses"""
    class Config:
        from_attributes = True


class BaseAIValidationModel(SQLModel):
    """Base model for AI response validation"""
    class Config:
        extra = "forbid"
        strict = True
