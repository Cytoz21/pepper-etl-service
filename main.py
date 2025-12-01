import flet as ft
from dotenv import load_dotenv
import os
import sys
from src.view import MainView, LoginView


def get_asset_path(asset_name):
    """Get the correct path to an asset file, works both in dev and compiled"""
    # Check if running in Web mode (Dokploy/Flet Web)
    is_web = os.getenv('PRODUCTION', 'false').lower() == 'true'
    
    if is_web:
        return asset_name

    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'src', 'assets', asset_name)


def main(page: ft.Page, automation_controller=None):
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
    
    # Store logo path in page for LoginView access
    page.logo_path = logo_path
    
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
            main_view_obj = ft.View(
                "/",
                padding=0,
                bgcolor="#121212"
            )
            
            # Initialize MainView
            main_view_instance = MainView(page, logo_path=logo_path, automation_controller=automation_controller)
            
            # Add layout to view
            main_view_obj.controls.append(main_view_instance.layout)
            
            page.views.append(main_view_obj)
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start at root (will redirect to login if not auth)
    page.go("/")

    # Initialize Automation (inside main to share event loop)
    try:
        from src.controller.automation_controller import AutomationController
        from src.service.scheduler_service import SchedulerService
        
        # Use the controller passed from outside if available, otherwise create new
        # (Python closures capture variables by reference)
        # The 'nonlocal' keyword is not applicable here as automation_controller is a parameter.
        # The assignment 'automation_controller = AutomationController()' updates the local parameter.
        # The MainView instance created in route_change will correctly use this updated local variable.
        
    except Exception as e:
        print(f"⚠️ Automation not available: {str(e)}")
        print("   The app will continue without automation features.")


if __name__ == "__main__":
    # Run the Flet application
    # For web deployment, use view=WEB_BROWSER and configure port
    
    # Check if running in production (Docker/Dokploy)
    is_production = os.getenv('PRODUCTION', 'false').lower() == 'true'
    
    # Ensure assets directory is correctly set
    # Assuming assets are in src/assets
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'assets')
    
    # We initialize controller as None here, it will be created inside main
    automation_controller_ref = None

    if is_production:
        # Web server mode for Dokploy
        ft.app(
            target=lambda page: main(page, automation_controller_ref), 
            view=ft.AppView.WEB_BROWSER,
            port=8080,
            host="0.0.0.0",
            assets_dir=assets_dir
        )
    else:
        # Desktop mode for local development
        ft.app(target=lambda page: main(page, automation_controller_ref), assets_dir=assets_dir)