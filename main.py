import flet as ft
from dotenv import load_dotenv
from src.view import MainView


def main(page: ft.Page):
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Create and initialize the main view
    MainView(page)


if __name__ == "__main__":
    # Run the Flet application
    ft.app(target=main)