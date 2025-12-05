"""
FastAPI backend for EXIF metadata editor.
Handles image upload, geocoding, format conversion, and EXIF injection.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import os
from dotenv import load_dotenv

from services.geocoding import GeocodingService
from services.image_processor import ImageProcessor
from services.exif_handler import read_gps_from_exif

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="EXIF Metadata Editor API",
    description="API for modifying image EXIF metadata (GPS location and format conversion)",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
geocoding_service = GeocodingService()
image_processor = ImageProcessor()


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "EXIF Metadata Editor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process-image")
async def process_image(
    file: UploadFile = File(..., description="Image file to process"),
    address: str = Form(..., description="Target address for GPS coordinates"),
    format: str = Form(..., description="Output format: jpeg, png, or webp")
):
    """
    Process an image: add GPS metadata and convert format.
    
    Args:
        file: Uploaded image file
        address: Address to convert to GPS coordinates
        format: Desired output format
        
    Returns:
        Processed image with GPS EXIF data
        
    Raises:
        400: Invalid input (bad format, empty address, etc.)
        422: Cannot geocode address
        500: Internal processing error
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded."
            )
        
        # Validate address
        if not address or not address.strip():
            raise HTTPException(
                status_code=400,
                detail="Address cannot be empty."
            )
        
        # Geocode address
        try:
            coordinates = geocoding_service.get_coordinates(address)
            if not coordinates:
                raise HTTPException(
                    status_code=422,
                    detail=f"Could not find coordinates for address: {address}"
                )
            latitude, longitude = coordinates
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Geocoding error: {str(e)}"
            )
        
        # Process image
        try:
            processed_bytes, mime_type = image_processor.process_image(
                image_bytes,
                latitude,
                longitude,
                format
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image processing error: {str(e)}"
            )
        
        # Determine filename
        original_name = file.filename or "image"
        name_without_ext = os.path.splitext(original_name)[0]
        output_filename = f"{name_without_ext}_gps.{format.lower()}"
        
        # Return processed image
        return Response(
            content=processed_bytes,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"',
                "X-GPS-Latitude": str(latitude),
                "X-GPS-Longitude": str(longitude),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@app.post("/get-coordinates")
async def get_coordinates(address: str = Form(...)):
    """
    Get GPS coordinates for an address without processing an image.
    Useful for preview/validation.
    
    Args:
        address: Address to geocode
        
    Returns:
        JSON with latitude and longitude
    """
    try:
        if not address or not address.strip():
            raise HTTPException(
                status_code=400,
                detail="Address cannot be empty."
            )
        
        coordinates = geocoding_service.get_coordinates(address)
        
        if not coordinates:
            raise HTTPException(
                status_code=422,
                detail=f"Could not find coordinates for address: {address}"
            )
        
        latitude, longitude = coordinates
        
        return {
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
