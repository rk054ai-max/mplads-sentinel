"""Canonical Pydantic models for MPLADS works."""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkStatus(str, Enum):
    """Normalized lifecycle status for an MPLADS work."""

    PROPOSED = "proposed"
    RECOMMENDED = "recommended"
    SANCTIONED = "sanctioned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class Work(BaseModel):
    """Canonical normalized representation of one MPLADS work."""

    model_config = ConfigDict(extra="forbid")

    work_id: str = Field(description="Stable identifier for the work.")
    description: str | None = Field(
        default=None, description="Description of the proposed or executed work."
    )
    state: str | None = Field(default=None, description="Indian state containing the work.")
    district: str | None = Field(default=None, description="District containing the work.")
    constituency: str | None = Field(
        default=None, description="Parliamentary constituency associated with the work."
    )
    latitude: float | None = Field(
        default=None, ge=-90, le=90, description="WGS84 latitude in decimal degrees."
    )
    longitude: float | None = Field(
        default=None, ge=-180, le=180, description="WGS84 longitude in decimal degrees."
    )
    work_type: str | None = Field(
        default=None, description="Normalized category or type of work."
    )
    recommended_amount: Decimal | None = Field(
        default=None, ge=Decimal("0"), description="Amount recommended for the work, in INR."
    )
    sanctioned_amount: Decimal | None = Field(
        default=None, ge=Decimal("0"), description="Amount sanctioned for the work, in INR."
    )
    expenditure: Decimal | None = Field(
        default=None, ge=Decimal("0"), description="Expenditure recorded for the work, in INR."
    )
    recommendation_date: date | None = Field(
        default=None, description="Date on which the work was recommended."
    )
    sanction_date: date | None = Field(
        default=None, description="Date on which the work was sanctioned."
    )
    start_date: date | None = Field(
        default=None, description="Date on which work execution started."
    )
    completion_date: date | None = Field(
        default=None, description="Date on which work execution was completed."
    )
    status: WorkStatus | None = Field(
        default=None, description="Normalized lifecycle status of the work."
    )
    implementing_agency: str | None = Field(
        default=None, description="Agency responsible for implementing the work."
    )


class WorkList(BaseModel):
    """Collection of canonical works returned by an API or processing step."""

    model_config = ConfigDict(extra="forbid")

    items: list[Work] = Field(description="Work records in this collection.")
    total: int = Field(ge=0, description="Total number of records represented by the collection.")


class ValidationError(BaseModel):
    """One field-level validation error suitable for an API response."""

    model_config = ConfigDict(extra="forbid")

    location: list[str | int] = Field(description="Path to the invalid value.")
    message: str = Field(description="Human-readable validation message.")
    error_type: str = Field(description="Stable validation error type identifier.")
    input: Any | None = Field(default=None, description="Rejected input value, when safe to return.")


class ValidationErrorResponse(BaseModel):
    """Structured response containing one or more validation errors."""

    model_config = ConfigDict(extra="forbid")

    detail: list[ValidationError] = Field(description="Validation errors returned to the client.")
