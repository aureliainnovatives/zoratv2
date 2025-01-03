from typing import Dict, Any, ClassVar
import logging
from ...core.base_tool import BaseTool

logger = logging.getLogger(__name__)

class WeatherCapability(BaseTool):
    """Weather capability for getting weather information"""
    
    # Class constants (not Pydantic fields)
    MOCK_WEATHER: ClassVar[Dict[str, Dict[str, Any]]] = {
        "nashik": {
            "temperature": 28,
            "humidity": 65,
            "description": "partly cloudy",
            "wind_speed": 12
        },
        "mumbai": {
            "temperature": 32,
            "humidity": 75,
            "description": "humid and cloudy",
            "wind_speed": 15
        },
        "pune": {
            "temperature": 26,
            "humidity": 60,
            "description": "clear sky",
            "wind_speed": 8
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize weather capability"""
        # Set default config if needed
        config = {
            "name": "Weather",
            "description": "Fetch current weather details for a location",
            "parameters": {"location": "string"},
            **config  # Allow overrides from passed config
        }
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather information for a location"""
        try:
            location = input_data.get("location", "").lower()
            if not location:
                raise ValueError("Location is required")
                
            if location in self.MOCK_WEATHER:
                weather = self.MOCK_WEATHER[location]
                return {
                    "location": location.capitalize(),
                    "temperature": weather["temperature"],
                    "humidity": weather["humidity"],
                    "description": weather["description"],
                    "wind_speed": weather["wind_speed"]
                }
            else:
                raise ValueError(f"No weather data available for {location}")
                
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}")
            raise 