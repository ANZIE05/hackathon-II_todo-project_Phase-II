from sqlmodel import SQLModel, Field
from typing import Any, Dict
import uuid
from datetime import datetime
from pydantic import BaseModel


class BaseSQLModel(SQLModel):
    """
    Base class for all SQLModels in the application.
    Provides common fields and functionality.
    """
    # Common fields that all models will inherit
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def dict(self, **kwargs) -> Dict[str, Any]:
        """
        Override the dict method to exclude certain fields if needed.

        Args:
            **kwargs: Additional arguments for the dict method

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        # Call the parent dict method
        result = super().dict(**kwargs)

        # Convert datetime objects to ISO format strings
        if "created_at" in result and isinstance(result["created_at"], datetime):
            result["created_at"] = result["created_at"].isoformat()
        if "updated_at" in result and isinstance(result["updated_at"], datetime):
            result["updated_at"] = result["updated_at"].isoformat()

        return result


class TimestampMixin:
    """
    Mixin class to add timestamp fields to models.
    """
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_timestamp(self) -> None:
        """
        Update the updated_at timestamp to the current time.
        """
        self.updated_at = datetime.utcnow()


class UUIDPrimaryKey:
    """
    Mixin class to add UUID primary key to models.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)