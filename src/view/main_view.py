import flet as ft
from datetime import date, datetime
from typing import List
from ..controller import DownloadController


class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = DownloadController()
        self._setup_page()
        self._create_components()
        self._build_layout()
    
    def _setup_page(self):
        """Configure page properties"""
        self.page.title = "Descargador de Reportes Excel"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a1a"  # Dark background
        self.page.window_width = 800
        self.page.window_height = 700
        self.page.window_resizable = True
        self.page.window_min_width = 600
        self.page.window_min_height = 500
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
    
    def _create_components(self):
        """Create UI components"""
        # Logo
        self.logo = ft.Image(
            src="src/assets/danper-logo.png",
            width=80,
            height=80,
            fit=ft.ImageFit.CONTAIN
        )
        
        # Company name
        self.company_name = ft.Text(
            "DANPER",
            size=12,
            weight=ft.FontWeight.BOLD,
            color="#c41a1d",  # Dark red for company name
            text_align=ft.TextAlign.CENTER
        )
        
        # Title
        self.title = ft.Text(
            "Descargador de Reportes de Fitosanidad",
            size=22,
            weight=ft.FontWeight.BOLD,
            color="#f9ebe8",  # Light beige for title
            text_align=ft.TextAlign.CENTER
        )
        
        # Subtitle
        self.subtitle = ft.Text(
            "Selecciona el rango de fechas para descargar los reportes Excel",
            size=13,
            color="#ec6161",  # Light red for subtitle
            text_align=ft.TextAlign.CENTER
        )
        
        # Date inputs
        today = date.today()
        self.start_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            value=today,
            on_change=self._on_date_change
        )
        
        self.end_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
            value=today,
            on_change=self._on_date_change
        )
        
        # File picker for selecting download folder
        self.folder_picker = ft.FilePicker(
            on_result=self._on_folder_selected
        )
        
        self.page.overlay.extend([self.start_date_picker, self.end_date_picker, self.folder_picker])
        
        # Date input fields
        self.start_date_field = ft.TextField(
            label="Fecha de Inicio",
            value=today.strftime("%Y-%m-%d"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_start_date_picker
        )
        
        self.end_date_field = ft.TextField(
            label="Fecha de Fin",
            value=today.strftime("%Y-%m-%d"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_end_date_picker
        )
        
        # Folder selection
        self.selected_folder = "downloads"  # Default folder
        self.folder_field = ft.TextField(
            label="Carpeta de Descarga",
            value=self.selected_folder,
            read_only=True,
            suffix_icon=ft.Icons.FOLDER,
            expand=True
        )
        
        self.folder_button = ft.ElevatedButton(
            text="Seleccionar",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._select_folder,
            style=ft.ButtonStyle(
                color="#f9ebe8",  # Light beige text
                bgcolor="#ec6161"  # Light red background
            )
        )
        
        # Download button
        self.download_button = ft.ElevatedButton(
            text="Descargar Reportes",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(
                color="#f9ebe8",  # Light beige text
                bgcolor="#c41a1d",  # Dark red background
                padding=ft.padding.symmetric(horizontal=30, vertical=15)
            ),
            on_click=self._on_download_click
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False,
            color="#ec6161",  # Light red progress
            bgcolor="#2a2a2a"  # Dark background
        )
        
        # Status text
        self.status_text = ft.Text(
            "",
            size=12,
            color="#f9ebe8",  # Light beige text
            text_align=ft.TextAlign.CENTER
        )
        
        # Results container with scroll
        self.results_container = ft.Column(
            visible=False,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Error container
        self.error_container = ft.Container(
            content=ft.Text("", color="#fb0404"),  # Bright red error text
            visible=False,
            bgcolor="#2a1a1a",  # Dark background with red tint
            border=ft.border.all(1, "#c41a1d"),  # Dark red border
            border_radius=8,
            padding=10
        )
    
    def _build_layout(self):
        """Build the main layout"""
        # Date selection - responsive layout
        date_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.start_date_field,
                    col={"sm": 12, "md": 6},
                    padding=ft.padding.only(right=10)
                ),
                ft.Container(
                    content=self.end_date_field,
                    col={"sm": 12, "md": 6},
                    padding=ft.padding.only(left=10)
                )
            ],
            spacing=10
        )
        
        # Folder selection - responsive layout
        folder_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.folder_field,
                    col={"sm": 12, "md": 8},
                    padding=ft.padding.only(right=10)
                ),
                ft.Container(
                    content=self.folder_button,
                    col={"sm": 12, "md": 4},
                    padding=ft.padding.only(left=10)
                )
            ],
            spacing=10
        )
        
        # Info card
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Información:", weight=ft.FontWeight.BOLD, color="#f9ebe8"),
                    ft.Text("• Se descargarán reportes de 4 cartillas (492, 493, 624, 669)", color="#ec6161"),
                    ft.Text("• Selecciona la carpeta donde guardar los archivos", color="#ec6161"),
                    ft.Text("• La descarga es asíncrona y puede tomar varios minutos", color="#ec6161")
                ]),
                padding=15,
                bgcolor="#2a2a2a"  # Dark card background
            ),
            elevation=2,
            color="#2a2a2a"  # Dark card color
        )
        
        # Results section with scroll
        results_section = ft.Container(
            content=self.results_container,
            height=300,  # Fixed height for scroll
            visible=False,
            border=ft.border.all(1, "#ec6161"),  # Light red border
            border_radius=8,
            padding=10,
            bgcolor="#2a2a2a"  # Dark background
        )
        
        # Main content with responsive layout
        main_content = ft.Column(
            controls=[
                # Header section with logo
                ft.Container(
                    content=ft.Column([
                        # Logo and company name centered
                        ft.Container(
                            content=ft.Column([
                                self.logo,
                                ft.Container(height=5),
                                self.company_name
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=15)
                        ),
                        
                        # Title and subtitle centered
                        ft.Column([
                            self.title,
                            ft.Container(height=5),
                            self.subtitle,
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0),
                        
                        # Divider
                        ft.Container(
                            content=ft.Divider(color="#ec6161"),
                            margin=ft.margin.only(top=20)
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0),
                    bgcolor="#2a2a2a",  # Dark header background
                    border_radius=10,
                    padding=25,
                    margin=ft.margin.only(bottom=25),
                    border=ft.border.all(1, "#ec6161")  # Light red border
                ),
                
                # Form section
                ft.Container(
                    content=ft.Column([
                        date_row,
                        ft.Container(height=15),
                        folder_row,
                    ]),
                    padding=ft.padding.symmetric(horizontal=20)
                ),
                
                # Action section
                ft.Container(
                    content=ft.Column([
                        self.download_button,
                        ft.Container(height=10),
                        self.progress_bar,
                        self.status_text,
                        self.error_container,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=20)
                ),
                
                # Results section
                results_section,
                
                # Info section
                ft.Container(
                    content=info_card,
                    padding=ft.padding.only(top=20)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
        )
        
        # Add to page with responsive container
        self.page.add(
            ft.Container(
                content=main_content,
                expand=True,
                padding=ft.padding.symmetric(horizontal=10, vertical=10)
            )
        )
        
        # Store reference to results section for show/hide
        self.results_section = results_section
    
    def _on_date_change(self, e):
        """Handle date picker changes"""
        if e.control == self.start_date_picker:
            if self.start_date_picker.value:
                self.start_date_field.value = self.start_date_picker.value.strftime("%Y-%m-%d")
        elif e.control == self.end_date_picker:
            if self.end_date_picker.value:
                self.end_date_field.value = self.end_date_picker.value.strftime("%Y-%m-%d")
        
        self.page.update()
    
    def _open_start_date_picker(self, e):
        """Open start date picker"""
        self.start_date_picker.open = True
        self.page.update()
    
    def _open_end_date_picker(self, e):
        """Open end date picker"""
        self.end_date_picker.open = True
        self.page.update()
    
    def _select_folder(self, e):
        """Open folder picker"""
        self.folder_picker.get_directory_path()
    
    def _on_folder_selected(self, e: ft.FilePickerResultEvent):
        """Handle folder selection"""
        if e.path:
            self.selected_folder = e.path
            self.folder_field.value = e.path
            self.page.update()
        else:
            # User cancelled selection, keep current folder
            pass
    
    def _on_download_click(self, e):
        """Handle download button click"""
        if self.controller.is_downloading:
            self._show_error("Ya hay una descarga en progreso")
            return
        
        # Get dates
        try:
            start_date = datetime.strptime(self.start_date_field.value, "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_date_field.value, "%Y-%m-%d").date()
        except ValueError:
            self._show_error("Formato de fecha inválido")
            return
        
        # Validate dates
        is_valid, error_message = self.controller.validate_date_range(start_date, end_date)
        if not is_valid:
            self._show_error(error_message)
            return
        
        # Start download
        self._start_download(start_date, end_date)
    
    def _start_download(self, start_date: date, end_date: date):
        """Start the download process"""
        self._hide_error()
        self._hide_results()
        self._show_progress()
        
        # Run download in background using Flet's page.run_task
        self.page.run_task(
            self._download_task,
            start_date,
            end_date
        )
    
    async def _download_task(self, start_date: date, end_date: date):
        """Async download task"""
        await self.controller.download_reports(
            start_date=start_date,
            end_date=end_date,
            download_path=self.selected_folder,
            progress_callback=self._on_progress_update,
            completion_callback=self._on_download_complete,
            error_callback=self._on_download_error
        )
    
    def _on_progress_update(self, progress: float, message: str):
        """Handle progress updates"""
        self.progress_bar.value = progress
        self.status_text.value = message
        self.page.update()
    
    def _on_download_complete(self, file_paths: List[str]):
        """Handle download completion"""
        self._hide_progress()
        self._show_results(file_paths)
        self.page.update()
    
    def _on_download_error(self, error_message: str):
        """Handle download errors"""
        self._hide_progress()
        self._show_error(error_message)
        self.page.update()
    
    def _show_progress(self):
        """Show progress indicators"""
        self.progress_bar.visible = True
        self.status_text.visible = True
        self.download_button.disabled = True
        self.page.update()
    
    def _hide_progress(self):
        """Hide progress indicators"""
        self.progress_bar.visible = False
        self.status_text.visible = False
        self.download_button.disabled = False
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error message"""
        self.error_container.content.value = message
        self.error_container.visible = True
        self.page.update()
    
    def _hide_error(self):
        """Hide error message"""
        self.error_container.visible = False
        self.page.update()
    
    def _show_results(self, file_paths: List[str]):
        """Show download results with detailed file information"""
        self.results_container.controls.clear()
        
        # Success message
        success_text = ft.Text(
            f"✅ Descarga completada exitosamente: {len(file_paths)} archivos",
            color="#ec6161",  # Light red for success
            weight=ft.FontWeight.BOLD,
            size=16
        )
        self.results_container.controls.append(success_text)
        
        # Add divider
        self.results_container.controls.append(ft.Divider(height=20, color="#ec6161"))
        
        # File list with detailed information
        if file_paths:
            files_title = ft.Text(
                "Archivos descargados:", 
                weight=ft.FontWeight.BOLD,
                size=14,
                color="#f9ebe8"  # Light beige for section title
            )
            self.results_container.controls.append(files_title)
            
            for i, file_path in enumerate(file_paths):
                # Get file summary using Polars
                file_summary = self.controller.download_service.get_file_summary(file_path)
                
                # Create detailed file information
                file_info_content = [
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color="#ec6161", size=20),  # Light red icon
                        ft.Text(
                            f"{i+1}. {file_summary.get('filename', 'Unknown')}", 
                            weight=ft.FontWeight.BOLD, 
                            expand=True,
                            size=13,
                            color="#f9ebe8"  # Light beige filename
                        )
                    ])
                ]
                
                # Add file details if available
                if 'error' not in file_summary:
                    details_text = f"📊 {file_summary.get('rows', 0)} filas, {file_summary.get('columns', 0)} columnas | 💾 {file_summary.get('file_size_mb', 0)} MB"
                    file_info_content.append(
                        ft.Text(details_text, size=11, color="#ec6161")  # Light red details
                    )
                    
                    # Show first few column names if available
                    if file_summary.get('column_names'):
                        columns_preview = ", ".join(file_summary['column_names'][:3])
                        if len(file_summary['column_names']) > 3:
                            columns_preview += f" ... (+{len(file_summary['column_names']) - 3} más)"
                        file_info_content.append(
                            ft.Text(f"📋 Columnas: {columns_preview}", size=10, color="#c41a1d")  # Dark red columns
                        )
                else:
                    # Show error information
                    file_info_content.append(
                        ft.Text(f"⚠️ Error: {file_summary['error']}", size=11, color="#fb0404")  # Bright red error
                    )
                    file_info_content.append(
                        ft.Text(f"💾 {file_summary.get('file_size_mb', 0)} MB", size=11, color="#ec6161")  # Light red size
                    )
                
                # Add file path (truncated for better display)
                path_display = file_path if len(file_path) <= 60 else f"...{file_path[-57:]}"
                file_info_content.append(
                    ft.Text(f"📁 {path_display}", size=9, color="#f9ebe8")  # Light beige path
                )
                
                file_item = ft.Container(
                    content=ft.Column(file_info_content, spacing=3),
                    bgcolor="#3a2a2a",  # Dark background with slight red tint
                    border=ft.border.all(1, "#ec6161"),  # Light red border
                    border_radius=8,
                    padding=12,
                    margin=ft.margin.symmetric(vertical=3)
                )
                self.results_container.controls.append(file_item)
        
        # Show the results section
        self.results_section.visible = True
        self.results_container.visible = True
        self.page.update()
    
    def _hide_results(self):
        """Hide results"""
        self.results_section.visible = False
        self.results_container.visible = False
        self.page.update()
