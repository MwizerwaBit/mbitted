"""Shared Pydantic base: enables reading attributes off ORM objects."""

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
