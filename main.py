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
    
    # Load .env.local if it exists (overrides .env)
    env_local_path = os.path.join(base_path, '.env.local')
    if os.path.exists(env_local_path):
import flet as ft
from dotenv import load_dotenv
import os
import sys
from src.view import MainView, LoginView


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
    
    # Load .env.local if it exists (overrides .env)
    env_local_path = os.path.join(base_path, '.env.local')
    if os.path.exists(env_local_path):
        load_dotenv(env_local_path, override=True)
    
    if not os.path.exists(env_path) and not os.path.exists(env_local_path):
        # Fallback: try loading from current directory
        load_dotenv()
    
    # Get asset paths
    logo_path = get_asset_path('danper-logo.png')
    
    def route_change(route):
        page.views.clear()
        
        # Check authentication
        is_authenticated = page.session.get("authenticated")
        
        if page.route == "/login":
            page.views.append(LoginView(page))
        elif not is_authenticated:
            page.go("/login")
        else:
            # Main App View
            # We create a base view and let MainView populate it
            # MainView uses page.add() which adds to the top view
            main_view_obj = ft.View(
                "/",
                padding=0,
                bgcolor="#121212"
            )
            page.views.append(main_view_obj)
            
            # Initialize MainView (it will add controls to the view we just pushed)
            MainView(page, logo_path=logo_path)
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start at root (will redirect to login if not auth)
    page.go("/")


if __name__ == "__main__":
    # Run the Flet application
    # For web deployment, use view=WEB_BROWSER and configure port
    
    # Check if running in production (Docker/Dokploy)
    is_production = os.getenv('PRODUCTION', 'false').lower() == 'true'
    
    # Ensure assets directory is correctly set
    # Assuming assets are in src/assets
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'assets')
    
    if is_production:
        # Web server mode for Dokploy
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            port=8080,
            host="0.0.0.0",
            assets_dir=assets_dir
        )
    else:
        # Desktop mode for local development
        ft.app(target=main, assets_dir=assets_dir)