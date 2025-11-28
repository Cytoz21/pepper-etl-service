import flet as ft
import bcrypt
import os
import time
from .main_view import MainView

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/login")
        self.page = page
        self.bgcolor = "#1a1c1e"
        self.padding = 0
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Rate limiting variables
        self.last_attempt_time = 0
        self.attempts = 0
        
        self._build_view()

    def _build_view(self):
        # Logo
        logo = ft.Image(
            src=self.page.logo_path if hasattr(self.page, 'logo_path') else "",
            width=200,
            fit=ft.ImageFit.CONTAIN,
        )

        # Error text
        self.error_text = ft.Text(
            value="",
            color="red",
            size=14,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )

        # Username field
        self.username_field = ft.TextField(
            label="Usuario",
            width=300,
            bgcolor="#2b2d31",
            border_color="#43474e",
            color="white",
            text_size=14,
            height=45,
            content_padding=10,
            border_radius=8,
            on_submit=lambda _: self.password_field.focus()
        )

        # Password field
        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            bgcolor="#2b2d31",
            border_color="#43474e",
            color="white",
            text_size=14,
            height=45,
            content_padding=10,
            border_radius=8,
            on_submit=self._login
        )

        # Login button
        login_button = ft.ElevatedButton(
            text="Iniciar Sesión",
            width=300,
            height=45,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#C41A1D",  # DANPER Red
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=self._login
        )

        # Container card
        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=20),
                    logo,
                    ft.Container(height=20),
                    ft.Text("Bienvenido", size=24, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("Ingrese sus credenciales para continuar", size=14, color="#8e918f"),
                    ft.Container(height=20),
                    self.error_text,
                    self.username_field,
                    ft.Container(height=10),
                    self.password_field,
                    ft.Container(height=20),
                    login_button,
                    ft.Container(height=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=400,
            padding=30,
            bgcolor="#111315",
            border_radius=16,
            border=ft.border.all(1, "#43474e"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.5, "black"),
            )
        )

        self.controls = [
            ft.Container(
                content=card,
                alignment=ft.alignment.center,
                expand=True
            )
        ]

    def _login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        self.error_text.visible = False
        self.page.update()

        # Basic validation
        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseña")
            return

        # Rate limiting (simple)
        current_time = time.time()
        if current_time - self.last_attempt_time < 2:  # 2 seconds delay between attempts
            self._show_error("Por favor espere unos segundos...")
            return
        
        self.last_attempt_time = current_time

        # Get credentials from env
        env_user = os.getenv("AUTH_USERNAME")
        env_pass_hash = os.getenv("AUTH_PASSWORD_HASH")

        if not env_user or not env_pass_hash:
            # Fallback/Error if not configured
            print("Error: AUTH_USERNAME or AUTH_PASSWORD_HASH not set")
            self._show_error("Error de configuración del servidor")
            return

        # Check username (constant time comparison not strictly necessary for username but good practice)
        if username != env_user:
            # Fake verify to prevent timing attacks (simulate work)
            bcrypt.checkpw(password.encode(), env_pass_hash.encode())
            self._show_error("Credenciales inválidas")
            return

        # Check password
        try:
            if bcrypt.checkpw(password.encode(), env_pass_hash.encode()):
                # Success
                self.page.session.set("authenticated", True)
                self.page.go("/")
            else:
                self._show_error("Credenciales inválidas")
        except Exception as e:
            print(f"Auth error: {e}")
            self._show_error("Error de autenticación")

    def _show_error(self, message):
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()
