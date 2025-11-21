import flet as ft
from dotenv import load_dotenv
import os
import sys
from src.view import MainView


def get_asset_path(asset_name):
    """Get the correct path to an asset file, works both in dev and compiled"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'src', 'assets', asset_name)


def main(page: ft.Page):
    """Main application entry point"""
    # Load environment variables from .env file
    # Try multiple locations to support both dev and compiled environments
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
        env_path = os.path.join(base_path, '.env')
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_path, '.env')
    
    # Load .env file if it exists
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Fallback: try loading from current directory
        load_dotenv()
    
    # Get asset paths
    logo_path = get_asset_path('danper-logo.png')
    
    # Create and initialize the main view
    MainView(page, logo_path=logo_path)


if __name__ == "__main__":
    # Run the Flet application
    ft.app(target=main)