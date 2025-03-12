from functools import cached_property
from typing import Any
from typing import Dict

from pydantic import BaseModel
from pydantic import model_validator

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

    @model_validator(mode="before")
    @classmethod
    def validate_service_and_target(
        cls, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate the service and target type fields

        Args:
            data: The data to validate.

        Returns:
            The validated data.

        Raises:
            ValueError: If the service or target type is not found.
        """

        service = data.get("service")
        target_type = data.get("target_type")
        if service not in SERVICES:
            raise ValueError(f"Service '{service}' not found")
        if target_type not in SERVICES[service]:
            raise ValueError(
                f"Target type '{target_type}' not found for service '{service}'"
            )
        return data

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
