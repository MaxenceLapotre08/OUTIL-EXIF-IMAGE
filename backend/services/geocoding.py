"""
Geocoding service for converting addresses to GPS coordinates.
Uses OpenStreetMap's Nominatim service via geopy.
"""
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os


class GeocodingService:
    """Service for geocoding addresses to GPS coordinates."""
    
    def __init__(self, user_agent: str = None):
        """
        Initialize the geocoding service.
        
        Args:
            user_agent: User agent string for Nominatim API
        """
        self.user_agent = user_agent or os.getenv("USER_AGENT", "EXIF-Metadata-Editor/1.0")
        self.geolocator = Nominatim(user_agent=self.user_agent, timeout=10)
    
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert an address to GPS coordinates (latitude, longitude).
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
            
        Raises:
            ValueError: If address is empty or invalid
            GeocoderServiceError: If the geocoding service is unavailable
        """
        if not address or not address.strip():
            raise ValueError("Address cannot be empty")
        
        try:
            location = self.geolocator.geocode(address)
            
            if location:
                return (location.latitude, location.longitude)
            else:
                return None
                
        except GeocoderTimedOut:
            # Retry once on timeout
            try:
                location = self.geolocator.geocode(address)
                if location:
                    return (location.latitude, location.longitude)
                return None
            except Exception as e:
                raise GeocoderServiceError(f"Geocoding service timed out: {str(e)}")
                
        except GeocoderServiceError as e:
            raise GeocoderServiceError(f"Geocoding service error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid address or geocoding error: {str(e)}")
