from uuid import uuid4
from io import BytesIO
from pathlib import Path

from PIL import Image


def image_handler(file: bytes, directory: str, image_width: int) -> Path:
    """
    Process an image file from bytes and save it as a WEBP file with a specified width.

    Args:
        file (bytes): The image file in bytes.
        directory (str): The directory where the image will be saved.
        image_width (int): The width of the resized image.

    Returns:
        Path: The file path of the saved image.
    """

    # Open image
    image = Image.open(BytesIO(file))

    # Calculate the new height maintaining the aspect ratio
    aspect_ratio = image.height / image.width
    new_height = int(image_width * aspect_ratio)

    # Resize image
    image = image.resize((image_width, new_height), resample=Image.LANCZOS)

    # Generate unique file name
    file_name = f"PIL-{uuid4()}.webp"

    # Prepare output path
    output_dir = Path(f"src/media/{directory}")
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    output_path = output_dir / file_name

    # Save image with default quality settings for better performance
    image.save(output_path, "WEBP", quality=100)

    # Return file path
    return output_path


if __name__ == "__main__":
    image = bytes(open(input("Image path: "), "rb").read())
    width = 1000
    image_handler(image, width)
