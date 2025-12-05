"""
Image processing service for format conversion and EXIF manipulation.
"""
from PIL import Image
import io
from typing import Tuple, Optional
import piexif
from .exif_handler import add_gps_to_image


class ImageProcessor:
    """Service for processing images - conversion and EXIF manipulation."""
    
    SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "webp"}
    FORMAT_MAPPING = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP"
    }
    
    def __init__(self):
        """Initialize the image processor."""
        pass
    
    def validate_format(self, format_str: str) -> str:
        """
        Validate and normalize output format.
        
        Args:
            format_str: Format string (jpeg, png, webp)
            
        Returns:
            Normalized format string
            
        Raises:
            ValueError: If format is not supported
        """
        format_lower = format_str.lower().strip()
        if format_lower not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format_str}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        return format_lower
    
    def process_image(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        output_format: str
    ) -> Tuple[bytes, str]:
        """
        Process image: convert format and add GPS EXIF data.
        
        Args:
            image_bytes: Original image bytes
            latitude: GPS latitude
            longitude: GPS longitude
            output_format: Desired output format (jpeg, png, webp)
            
        Returns:
            Tuple of (processed_image_bytes, mime_type)
            
        Raises:
            ValueError: If image cannot be processed or format is invalid
        """
        # Validate format
        output_format = self.validate_format(output_format)
        pil_format = self.FORMAT_MAPPING[output_format]
        
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Handle transparency for JPEG conversion
            if pil_format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode not in ("RGB", "L"):
                # Convert other modes to RGB
                if pil_format == "JPEG":
                    image = image.convert("RGB")
                elif pil_format in ("PNG", "WEBP"):
                    image = image.convert("RGBA")
            
            # Save image to bytes with new format
            output_buffer = io.BytesIO()
            
            # Prepare save parameters
            save_kwargs = {"format": pil_format}
            
            if pil_format == "JPEG":
                save_kwargs["quality"] = 95
                save_kwargs["optimize"] = True
            elif pil_format == "PNG":
                save_kwargs["optimize"] = True
            elif pil_format == "WEBP":
                save_kwargs["quality"] = 95
            
            # Save without EXIF first
            image.save(output_buffer, **save_kwargs)
            converted_bytes = output_buffer.getvalue()
            
            # Add GPS EXIF data (only for JPEG and WEBP)
            if pil_format in ("JPEG", "WEBP"):
                try:
                    exif_bytes = add_gps_to_image(converted_bytes, latitude, longitude)
                    
                    # Re-save with EXIF
                    output_buffer = io.BytesIO()
                    image.save(output_buffer, exif=exif_bytes, **save_kwargs)
                    final_bytes = output_buffer.getvalue()
                except Exception as e:
                    # If EXIF injection fails, return image without EXIF
                    print(f"Warning: Could not add EXIF data: {e}")
                    final_bytes = converted_bytes
            else:
                # PNG doesn't support EXIF in the same way
                # We'll skip EXIF for PNG
                final_bytes = converted_bytes
            
            # Determine MIME type
            mime_types = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "WEBP": "image/webp"
            }
            mime_type = mime_types.get(pil_format, "application/octet-stream")
            
            return final_bytes, mime_type
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def get_image_info(self, image_bytes: bytes) -> dict:
        """
        Get basic information about an image.
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            Dictionary with image information (format, size, mode)
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return {
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "width": image.size[0],
                "height": image.size[1]
            }
        except Exception as e:
            raise ValueError(f"Error reading image: {str(e)}")
