"""
EXIF metadata handler for reading and writing GPS data to images.
"""
import piexif
from typing import Tuple, Dict, Any, Optional
from fractions import Fraction


def decimal_to_dms(decimal: float, is_latitude: bool = True) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], str]:
    """
    Convert decimal degrees to degrees, minutes, seconds format.
    
    Args:
        decimal: Decimal degrees value
        is_latitude: True for latitude, False for longitude
        
    Returns:
        Tuple of (degrees, minutes, seconds, direction)
        Each component is a tuple of (numerator, denominator) for EXIF rational format
    """
    # Determine direction (N/S for latitude, E/W for longitude)
    if is_latitude:
        direction = 'N' if decimal >= 0 else 'S'
    else:
        direction = 'E' if decimal >= 0 else 'W'
    
    # Work with absolute value
    decimal = abs(decimal)
    
    # Extract degrees, minutes, seconds
    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    # Convert to rational format (numerator, denominator)
    # Using Fraction to get exact rational representation
    degrees_rational = (degrees, 1)
    minutes_rational = (minutes, 1)
    
    # For seconds, use higher precision (multiply by 10000 and divide)
    seconds_rational = (int(seconds * 10000), 10000)
    
    return (degrees_rational, minutes_rational, seconds_rational, direction)


def create_gps_ifd(latitude: float, longitude: float) -> Dict[int, Any]:
    """
    Create GPS IFD (Image File Directory) for EXIF data.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        
    Returns:
        Dictionary containing GPS EXIF tags
    """
    # Convert coordinates to DMS format
    lat_deg, lat_min, lat_sec, lat_ref = decimal_to_dms(latitude, is_latitude=True)
    lon_deg, lon_min, lon_sec, lon_ref = decimal_to_dms(longitude, is_latitude=False)
    
    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
        piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode('ascii'),
        piexif.GPSIFD.GPSLatitude: (lat_deg, lat_min, lat_sec),
        piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode('ascii'),
        piexif.GPSIFD.GPSLongitude: (lon_deg, lon_min, lon_sec),
    }
    
    return gps_ifd


def add_gps_to_image(image_bytes: bytes, latitude: float, longitude: float) -> bytes:
    """
    Add GPS coordinates to image EXIF data.
    
    Args:
        image_bytes: Original image bytes
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        
    Returns:
        Image bytes with GPS EXIF data
    """
    try:
        # Try to load existing EXIF data
        exif_dict = piexif.load(image_bytes)
    except Exception:
        # If no EXIF exists, create new empty structure
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    # Create and add GPS IFD
    gps_ifd = create_gps_ifd(latitude, longitude)
    exif_dict["GPS"] = gps_ifd
    
    # Convert to bytes
    exif_bytes = piexif.dump(exif_dict)
    
    return exif_bytes


def read_gps_from_exif(image_bytes: bytes) -> Optional[Dict[str, float]]:
    """
    Read GPS coordinates from image EXIF data.
    
    Args:
        image_bytes: Image bytes to read from
        
    Returns:
        Dictionary with 'latitude' and 'longitude' keys, or None if no GPS data
    """
    try:
        exif_dict = piexif.load(image_bytes)
        
        if "GPS" not in exif_dict or not exif_dict["GPS"]:
            return None
        
        gps_data = exif_dict["GPS"]
        
        # Check if GPS coordinates exist
        if (piexif.GPSIFD.GPSLatitude not in gps_data or 
            piexif.GPSIFD.GPSLongitude not in gps_data):
            return None
        
        # Extract latitude
        lat = gps_data[piexif.GPSIFD.GPSLatitude]
        lat_ref = gps_data[piexif.GPSIFD.GPSLatitudeRef].decode('ascii')
        latitude = (lat[0][0] / lat[0][1] + 
                   lat[1][0] / lat[1][1] / 60 + 
                   lat[2][0] / lat[2][1] / 3600)
        if lat_ref == 'S':
            latitude = -latitude
        
        # Extract longitude
        lon = gps_data[piexif.GPSIFD.GPSLongitude]
        lon_ref = gps_data[piexif.GPSIFD.GPSLongitudeRef].decode('ascii')
        longitude = (lon[0][0] / lon[0][1] + 
                    lon[1][0] / lon[1][1] / 60 + 
                    lon[2][0] / lon[2][1] / 3600)
        if lon_ref == 'W':
            longitude = -longitude
        
        return {
            "latitude": latitude,
            "longitude": longitude
        }
        
    except Exception:
        return None
