from pydantic import BaseModel


class UploadData(BaseModel):
    service: str
    target_type: str
