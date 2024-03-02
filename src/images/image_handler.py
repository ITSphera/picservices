import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image


def image_handler(file: bytes, width: int) -> Path:
    """
    Image handler
    :param file:
    :param width:
    :return:
    """

    # Open image
    image = Image.open(BytesIO(file))

    # Resize image
    height = int(width * (image.height / image.width))
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    # Generate unique file name
    file_name = f"PIL-{uuid.uuid4()}.webp"

    # Save image to media/ folder in src/media directory
    output_path = f"../media/{file_name}"
    image.save(output_path, "WEBP", quality=100)

    # Return file path
    return Path(output_path)


if __name__ == "__main__":
    image = bytes(open(input("Image path: "), "rb").read())
    width = 1000
    image_handler(image, width)