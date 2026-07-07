"""Canonical data models for restaurant data."""

from __future__ import annotations

import enum
from pydantic import BaseModel, Field, ConfigDict


class BudgetBand(str, enum.Enum):
    """Budget classification derived from approximate cost for two."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Restaurant(BaseModel):
    """Canonical restaurant record after normalisation."""

    model_config = ConfigDict(frozen=True)

    restaurant_id: int = Field(..., description="Unique identifier (row index)")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Neighbourhood / area")
    cuisines: list[str] = Field(default_factory=list, description="List of cuisines served")
    cost_raw: int = Field(default=0, description="Approx cost for two (raw int)")
    budget: BudgetBand = Field(default=BudgetBand.MEDIUM, description="Budget band")
    rating: float = Field(default=0.0, description="Aggregate rating [0.0–5.0]")
    votes: int = Field(default=0, description="Total votes")
    online_order: bool = Field(default=False, description="Accepts online orders")
    book_table: bool = Field(default=False, description="Allows table booking")
    rest_type: str = Field(default="", description="Restaurant type (Casual Dining, etc.)")
