import flet as ft
from datetime import date, datetime, timedelta
from typing import List
from ..controller import DownloadController
import os

class MainView:
    def __init__(self, page: ft.Page, logo_path: str = None):
        self.page = page
        self.logo_path = logo_path or "src/assets/danper-logo.png"
        self.controller = DownloadController()
        
        # Modern Dark Theme Colors
        self.COLOR_PRIMARY = "#C41A1D"    # Danper Red
        self.COLOR_BACKGROUND = "#121212" # Very Dark Grey (Material Dark)
        self.COLOR_SURFACE = "#1E1E1E"    # Dark Grey (Cards)
        self.COLOR_TEXT = "#E0E0E0"       # Light Grey/White
        self.COLOR_TEXT_SECONDARY = "#A0A0A0" # Dimmed Text
        self.COLOR_BORDER = "#333333"     # Dark Border
        
        self._setup_page()
        self._create_components()
        self._build_layout()
    
    def _setup_page(self):
        """Configure page properties"""
        self.page.title = "DANPER - Descargador de Reportes"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = self.COLOR_BACKGROUND
        self.page.window_width = 900
        self.page.window_height = 800
        self.page.window_resizable = True
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
    
    def _create_components(self):
        """Create UI components"""
        # --- Header Components ---
        self.logo = ft.Image(
            src=self.logo_path,
            width=120,
            height=60,
            fit=ft.ImageFit.CONTAIN
        )
        
        self.title = ft.Text(
            "Descargador de Reportes",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=self.COLOR_PRIMARY
        )
        
        # --- Configuration Components ---
        
        # Fundo Selection
        fundo_options = [ft.dropdown.Option(key=f.code, text=f.name) for f in self.controller.fundos]
        self.fundo_dropdown = ft.Dropdown(
            label="Seleccionar Fundo",
            options=fundo_options,
            width=400,
            border_color=self.COLOR_PRIMARY,
            color=self.COLOR_TEXT,
            bgcolor=self.COLOR_SURFACE,
            label_style=ft.TextStyle(color=self.COLOR_TEXT_SECONDARY),
            border_radius=5,
            focused_border_color=self.COLOR_PRIMARY
        )
        
        # Cartilla Selection (Checkbox List)
        self.cartilla_checkboxes = []
        for c in self.controller.cartillas:
            self.cartilla_checkboxes.append(
                ft.Checkbox(
                    label=str(c), 
                    value=False, 
                    data=c.code, 
                    active_color=self.COLOR_PRIMARY,
                    check_color="white",
                    label_style=ft.TextStyle(color=self.COLOR_TEXT)
                )
            )
            
        self.cartilla_list_container = ft.Column(
            controls=self.cartilla_checkboxes,
            scroll=ft.ScrollMode.AUTO,
            height=150
        )
        
        # Date Selection
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Initialize DatePickers
        self.start_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            value=yesterday,
            on_change=self._on_date_change
        )
        
        self.end_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            value=yesterday,
            on_change=self._on_date_change
        )
        
        # Important: Add to overlay immediately
        self.page.overlay.append(self.start_date_picker)
        self.page.overlay.append(self.end_date_picker)
        
        self.start_date_field = ft.TextField(
            label="Fecha Inicio",
            value=yesterday.strftime("%Y-%m-%d"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_start_date_picker,
            width=180,
            border_color=self.COLOR_PRIMARY,
            color=self.COLOR_TEXT,
            bgcolor=self.COLOR_SURFACE,
            label_style=ft.TextStyle(color=self.COLOR_TEXT_SECONDARY),
            border_radius=5
        )
        
        self.end_date_field = ft.TextField(
            label="Fecha Fin",
            value=yesterday.strftime("%Y-%m-%d"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_end_date_picker,
            width=180,
            border_color=self.COLOR_PRIMARY,
            color=self.COLOR_TEXT,
            bgcolor=self.COLOR_SURFACE,
            label_style=ft.TextStyle(color=self.COLOR_TEXT_SECONDARY),
            border_radius=5
        )
        
        # Download Path Selection
        # Directory picker (only for desktop)
        self.directory_path_text = ft.TextField(
            label="Carpeta de Descarga",
            value=os.path.abspath(os.getcwd()),
            read_only=True,
            expand=True,
            bgcolor="#2b2d31",
            border_color="#43474e",
            color="white",
            text_size=14,
            height=45,
            content_padding=10,
            border_radius=8,
            visible=not self.page.web
        )

        self.directory_picker = ft.FilePicker(on_result=self._on_directory_picked)
        self.page.overlay.append(self.directory_picker)
        
        # Web mode info text
        self.web_info_text = ft.Text(
            "Los archivos se descargarán automáticamente en un archivo ZIP.",
            color="#8e918f",
            size=12,
            italic=True,
            visible=self.page.web
        )

        self.browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Examinar...",
            icon_color="white",
            bgcolor="#43474e",
            on_click=lambda _: self.directory_picker.get_directory_path(),
            visible=not self.page.web,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        
        # We map path_field to directory_path_text for compatibility with existing code
        self.path_field = self.directory_path_text
        
        # --- Action Components ---
        self.download_button = ft.ElevatedButton(
            text="DESCARGAR REPORTES",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(
                color="white",
                bgcolor=self.COLOR_PRIMARY,
                padding=ft.padding.symmetric(horizontal=40, vertical=20),
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=5
            ),
            on_click=self._on_download_click
        )
        
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False,
            color=self.COLOR_PRIMARY,
            bgcolor=self.COLOR_SURFACE,
            bar_height=5
        )
        
        self.status_text = ft.Text("", size=12, color=self.COLOR_TEXT)
        
        # Results
        self.results_container = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        # Error Banner
        self.error_banner = ft.Container(
            content=ft.Text("", color="white"),
            bgcolor="#D32F2F", # Error Red
            padding=10,
            border_radius=5,
            visible=False,
            border=ft.border.all(1, "#FF5252")
        )

    def _build_layout(self):
        """Build the main layout"""
        
        # Header
        header = ft.Container(
            content=ft.Row(
                [self.logo, self.title],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=self.COLOR_SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="black",
                offset=ft.Offset(0, 4)
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, self.COLOR_PRIMARY))
        )
        
        # Configuration Card
        config_content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=self.COLOR_PRIMARY),
                ft.Text("Configuración de Descarga", size=18, weight=ft.FontWeight.BOLD, color=self.COLOR_TEXT)
            ]),
            ft.Divider(color=self.COLOR_BORDER),
            
            # Fundo
            ft.Text("1. Selecciona el Fundo:", weight=ft.FontWeight.BOLD, color=self.COLOR_TEXT),
            self.fundo_dropdown,
            
            # Cartillas
            ft.Text("2. Selecciona las Cartillas:", weight=ft.FontWeight.BOLD, color=self.COLOR_TEXT),
            ft.Container(
                content=self.cartilla_list_container,
                border=ft.border.all(1, self.COLOR_BORDER),
                border_radius=5,
                padding=5,
                height=150,
                bgcolor=self.COLOR_BACKGROUND
            ),
            
            # Dates
            ft.Text("3. Rango de Fechas:", weight=ft.FontWeight.BOLD, color=self.COLOR_TEXT),
            ft.Row([self.start_date_field, self.end_date_field]),
            
            # Path
            ft.Text("4. Ubicación de Descarga:", weight=ft.FontWeight.BOLD, color=self.COLOR_TEXT),
            ft.Row([self.path_field, self.browse_button, self.web_info_text]),
        ], spacing=15)
        
        config_card = ft.Container(
            content=config_content,
            padding=25,
            bgcolor=self.COLOR_SURFACE,
            border_radius=15,
            border=ft.border.all(1, self.COLOR_BORDER),
            shadow=ft.BoxShadow(blur_radius=10, color="black")
        )
        
        # Action Section
        action_section = ft.Column([
            self.error_banner,
            self.download_button,
            ft.Container(height=10),
            self.progress_bar,
            self.status_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Main Content
        main_content = ft.Column([
            config_card,
            ft.Container(height=30),
            action_section,
            ft.Container(height=30),
            ft.Text("Resultados:", weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_TEXT),
            ft.Container(
                content=self.results_container,
                height=200,
                border=ft.border.all(1, self.COLOR_BORDER),
                border_radius=5,
                padding=10,
                bgcolor=self.COLOR_SURFACE
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Elegant Footer Signature
        footer = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CODE, size=14, color=self.COLOR_TEXT_SECONDARY),
                        ft.Text(
                            "Creado por Anthony y Beto",
                            size=11,
                            color=self.COLOR_TEXT_SECONDARY,
                            italic=True
                        ),
                        ft.Container(width=5),
                        ft.Text("•", size=11, color=self.COLOR_BORDER),
                        ft.Container(width=5),
                        ft.Text(
                            "Área de Proyecciones",
                            size=11,
                            color=self.COLOR_TEXT_SECONDARY,
                            weight=ft.FontWeight.W_300
                        )
                    ], spacing=5),
                    opacity=0.6
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=15),
            border=ft.border.only(top=ft.BorderSide(1, self.COLOR_BORDER))
        )
        
        # Return the main layout instead of adding directly to page
        self.layout = ft.Column([
            header,
            ft.Container(
                content=main_content,
                padding=20,
                expand=True
            ),
            footer
        ], expand=True)
        
        # Note: We do NOT add to page here anymore. 
        # The controller (main.py) will add self.layout to the View.

    def _on_date_change(self, e):
        if e.control == self.start_date_picker and self.start_date_picker.value:
            self.start_date_field.value = self.start_date_picker.value.strftime("%Y-%m-%d")
        elif e.control == self.end_date_picker and self.end_date_picker.value:
            self.end_date_field.value = self.end_date_picker.value.strftime("%Y-%m-%d")
        self.page.update()

    def _open_start_date_picker(self, e):
        self.start_date_picker.open = True
        self.page.update()
    
    def _open_end_date_picker(self, e):
        self.end_date_picker.open = True
        self.page.update()

    def _on_directory_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.path_field.value = e.path
            self.path_field.update() # Update only the field, safer than page.update()

    def _on_download_click(self, e):
        # 1. Validate Fundo
        if not self.fundo_dropdown.value:
            self._show_error("Por favor selecciona un Fundo.")
            return
            
        # 2. Validate Cartillas
        selected_cartillas = [cb.data for cb in self.cartilla_checkboxes if cb.value]
        if not selected_cartillas:
            self._show_error("Por favor selecciona al menos una Cartilla.")
            return
            
        # 3. Validate Dates
        try:
            start_date = datetime.strptime(self.start_date_field.value, "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_date_field.value, "%Y-%m-%d").date()
        except ValueError:
            self._show_error("Formato de fecha inválido.")
            return
            
        is_valid, msg = self.controller.validate_date_range(start_date, end_date)
        if not is_valid:
            self._show_error(msg)
            return
            
        # 4. Start Download
        self._start_download(start_date, end_date, selected_cartillas, self.fundo_dropdown.value, self.path_field.value)

    def _start_download(self, start_date, end_date, cartillas, fundo_code, path):
        self._hide_error()
        self.progress_bar.visible = True
        self.download_button.disabled = True
        self.results_container.controls.clear()
        self.page.update()
        
        self.page.run_task(
            self._download_task,
            start_date, end_date, cartillas, fundo_code, path
        )

    async def _download_task(self, start_date, end_date, cartillas, fundo_code, path):
        await self.controller.download_reports(
            start_date=start_date,
            end_date=end_date,
            selected_cartillas=cartillas,
            selected_fundo_code=fundo_code,
            download_path=path,
            progress_callback=self._on_progress,
            completion_callback=self._on_complete,
            error_callback=self._on_error
        )

    def _on_progress(self, progress, message):
        self.progress_bar.value = progress
        self.status_text.value = message
        self.page.update()

    def _on_complete(self, files):
        self.progress_bar.visible = False
        self.download_button.disabled = False
        
        if self.page.web:
            self.status_text.value = f"Completado! Iniciando descarga de {len(files)} archivo(s)..."
            self.page.update()
            
            import shutil
            import time
            
            # Ensure assets/downloads exists
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            assets_dir = os.path.join(base_dir, 'src', 'assets', 'downloads')
            os.makedirs(assets_dir, exist_ok=True)
            
            for f in files:
                filename = os.path.basename(f)
                dest_path = os.path.join(assets_dir, filename)
                try:
                    shutil.copy2(f, dest_path)
                    ts = int(time.time())
                    self.page.launch_url(f"/downloads/{filename}?t={ts}")
                except Exception as e:
                    print(f"Error preparing web download for {filename}: {e}")

            self.status_text.value = f"Completado! Revise sus descargas."
        else:
            self.status_text.value = f"Completado! {len(files)} archivos descargados."
        
        for f in files:
            self.results_container.controls.append(
                ft.Text(f"✅ {os.path.basename(f)}", color="#4CAF50") # Green for success
            )
        self.page.update()

    def _on_error(self, message):
        self.progress_bar.visible = False
        self.download_button.disabled = False
        self._show_error(message)

    def _show_error(self, message):
        self.error_banner.content.value = message
        self.error_banner.visible = True
        self.page.update()

    def _hide_error(self):
        self.error_banner.visible = False
        self.page.update()
