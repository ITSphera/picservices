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
        username: The username of the user who uploaded the image.
    """

    service: str
    target_type: str
    username: str

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

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not v:
            raise ValueError("Username is required")
        return v

    @cached_property
    def target_info(self) -> Dict[str, Any]:
        """
        Get information about the target.

        Returns:
            A dictionary containing the directory and width of the target.
        """
        base_info = SERVICES[self.service][self.target_type]
        directory_template = base_info["dir"]
        username = self.username if self.username else "default"
        directory = directory_template.format(username=username)
        return {"dir": directory, "width": base_info["width"]}
