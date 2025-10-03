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
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 600
        self.page.window_height = 500
        self.page.window_resizable = False
        self.page.padding = 20
    
    def _create_components(self):
        """Create UI components"""
        # Title
        self.title = ft.Text(
            "Descargador de Reportes de Fitosanidad",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_800
        )
        
        # Subtitle
        self.subtitle = ft.Text(
            "Selecciona el rango de fechas para descargar los reportes Excel",
            size=14,
            color=ft.Colors.GREY_700
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
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE_600
            )
        )
        
        # Download button
        self.download_button = ft.ElevatedButton(
            text="Descargar Reportes",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
                padding=ft.padding.symmetric(horizontal=30, vertical=15)
            ),
            on_click=self._on_download_click
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False
        )
        
        # Status text
        self.status_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER
        )
        
        # Results container
        self.results_container = ft.Column(
            visible=False,
            spacing=10
        )
        
        # Error container
        self.error_container = ft.Container(
            content=ft.Text("", color=ft.Colors.RED_600),
            visible=False,
            bgcolor=ft.Colors.RED_50,
            border=ft.border.all(1, ft.Colors.RED_200),
            border_radius=8,
            padding=10
        )
    
    def _build_layout(self):
        """Build the main layout"""
        # Date selection row
        date_row = ft.Row(
            controls=[
                ft.Container(
                    content=self.start_date_field,
                    expand=1,
                    margin=ft.margin.only(right=10)
                ),
                ft.Container(
                    content=self.end_date_field,
                    expand=1,
                    margin=ft.margin.only(left=10)
                )
            ],
            spacing=20
        )
        
        # Folder selection row
        folder_row = ft.Row(
            controls=[
                self.folder_field,
                ft.Container(
                    content=self.folder_button,
                    margin=ft.margin.only(left=10)
                )
            ],
            spacing=10
        )
        
        # Info card
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Información:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Se descargarán reportes de 4 cartillas (492, 493, 624, 669)"),
                    ft.Text("• Selecciona la carpeta donde guardar los archivos"),
                    ft.Text("• La descarga es asíncrona y puede tomar varios minutos")
                ]),
                padding=15
            ),
            elevation=2
        )
        
        # Main content
        main_content = ft.Column(
            controls=[
                self.title,
                self.subtitle,
                ft.Divider(height=20),
                date_row,
                ft.Container(height=15),
                folder_row,
                ft.Container(height=20),
                self.download_button,
                ft.Container(height=10),
                self.progress_bar,
                self.status_text,
                self.error_container,
                self.results_container,
                ft.Container(height=20),
                info_card
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        
        # Add to page
        self.page.add(
            ft.Container(
                content=main_content,
                alignment=ft.alignment.center,
                expand=True
            )
        )
    
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
            color=ft.Colors.GREEN_600,
            weight=ft.FontWeight.BOLD
        )
        self.results_container.controls.append(success_text)
        
        # File list with detailed information
        if file_paths:
            files_title = ft.Text("Archivos descargados:", weight=ft.FontWeight.BOLD)
            self.results_container.controls.append(files_title)
            
            for file_path in file_paths:
                # Get file summary using Polars
                file_summary = self.controller.download_service.get_file_summary(file_path)
                
                # Create detailed file information
                file_info_content = [
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.GREEN_600),
                        ft.Text(file_summary.get('filename', 'Unknown'), weight=ft.FontWeight.BOLD, expand=True)
                    ])
                ]
                
                # Add file details if available
                if 'error' not in file_summary:
                    details_text = f"📊 {file_summary.get('rows', 0)} filas, {file_summary.get('columns', 0)} columnas | 💾 {file_summary.get('file_size_mb', 0)} MB"
                    file_info_content.append(
                        ft.Text(details_text, size=12, color=ft.Colors.GREY_600)
                    )
                    
                    # Show first few column names if available
                    if file_summary.get('column_names'):
                        columns_preview = ", ".join(file_summary['column_names'][:3])
                        if len(file_summary['column_names']) > 3:
                            columns_preview += f" ... (+{len(file_summary['column_names']) - 3} más)"
                        file_info_content.append(
                            ft.Text(f"📋 Columnas: {columns_preview}", size=11, color=ft.Colors.BLUE_600)
                        )
                else:
                    # Show error information
                    file_info_content.append(
                        ft.Text(f"⚠️ Error: {file_summary['error']}", size=12, color=ft.Colors.RED_600)
                    )
                    file_info_content.append(
                        ft.Text(f"💾 {file_summary.get('file_size_mb', 0)} MB", size=12, color=ft.Colors.GREY_600)
                    )
                
                # Add file path
                file_info_content.append(
                    ft.Text(f"📁 {file_path}", size=10, color=ft.Colors.GREY_500)
                )
                
                file_item = ft.Container(
                    content=ft.Column(file_info_content, spacing=5),
                    bgcolor=ft.Colors.GREEN_50,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                    border_radius=8,
                    padding=15,
                    margin=ft.margin.symmetric(vertical=5)
                )
                self.results_container.controls.append(file_item)
        
        self.results_container.visible = True
        self.page.update()
    
    def _hide_results(self):
        """Hide results"""
        self.results_container.visible = False
        self.page.update()
