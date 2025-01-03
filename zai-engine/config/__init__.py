import os
import json
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration based on MODE environment variable."""
    mode = os.getenv("MODE", "development").lower()
    if mode not in ["development", "production"]:
        raise ValueError(f"Invalid MODE: {mode}. Must be 'development' or 'production'")
    
    # Get config file path
    config_dir = Path(__file__).parent / "environments"
    config_file = config_dir / f"{mode}.json"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # Load and parse JSON
    with open(config_file, "r") as f:
        return json.load(f)

# Export the config instance
config = load_config() 