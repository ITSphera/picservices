from functools import cached_property
from typing import Any
from typing import Dict

from pydantic import BaseModel
from pydantic import field_validator

from src.config import SERVICES


class UploadData(BaseModel):
    """
    Class for validating image upload data

    Args:
        service: The service for image processing.
        target_type: The target type for image processing.
    """

    service: str
    target_type: str

    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str):
        if v not in SERVICES:
            raise ValueError(f"Service '{v}' not found")
        return v

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str, info):
        service = info.data.get("service")
        if service and v not in SERVICES[service]:
            raise ValueError(
                f"Target type '{v}' not found for service '{service}'"
            )
        return v

    @cached_property
    def target_info(self) -> Dict[str, Any]:
        """
        Get information about the target.

        Returns:
            A dictionary containing the directory and width of the target.
        """
        return {
            "dir": SERVICES[self.service][self.target_type]["dir"],
            "width": SERVICES[self.service][self.target_type]["width"],
        }
