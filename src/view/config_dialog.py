import flet as ft
from typing import Dict, Any, List

class ConfigDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, automation_controller):
        self.page_ref = page
        self.controller = automation_controller
        
        # UI Components
        self.time_field = ft.TextField(
            label="Hora de Ejecución (HH:MM)",
            hint_text="Ejemplo: 06:00",
            width=200,
            border_color="#C41A1D"
        )
        
        self.reports_container = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        
        # Initialize parent
        super().__init__(
            modal=True,
            title=ft.Text("Configuración de Automatización"),
            content=ft.Column([
                ft.Text("Configuración General", weight=ft.FontWeight.BOLD),
                self.time_field,
                ft.Divider(),
                ft.Text("Configuración de Cartillas", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.reports_container,
                    border=ft.border.all(1, "#333333"),
                    border_radius=5,
                    padding=10
                )
            ], width=600, height=450, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Guardar Cambios", 
                    bgcolor="#C41A1D", 
                    color="white",
                    on_click=self.save_config
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Load initial data
        self.load_config()

    def load_config(self):
        if not self.controller:
            return
            
        config = self.controller.get_config()
        self.time_field.value = config.get("schedule_time", "06:00")
        
        self.reports_container.controls.clear()
        self.report_inputs = []
        
        for report in config.get("reports", []):
            cartilla_id = report.get("cartilla_id")
            abbr = report.get("abbreviation", f"Cartilla {cartilla_id}")
            
            # Inputs for this report
            drive_input = ft.TextField(
                label="ID Carpeta Drive",
                value=report.get("drive_folder_id", ""),
                text_size=12,
                expand=True
            )
            
            path_input = ft.TextField(
                label="Ruta Local (Relativa)",
                value=report.get("local_path", ""),
                text_size=12,
                expand=True
            )
            
            # Store references to inputs along with original report data
            self.report_inputs.append({
                "original": report,
                "drive_input": drive_input,
                "path_input": path_input
            })
            
            # Add to UI
            self.reports_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{abbr} (ID: {cartilla_id})", weight=ft.FontWeight.BOLD, size=14),
                        ft.Row([drive_input, path_input], spacing=10)
                    ]),
                    padding=ft.padding.only(bottom=15)
                )
            )

    def save_config(self, e):
        if not self.controller:
            return

        new_time = self.time_field.value
        
        # Validate time format
        try:
            import time
            time.strptime(new_time, '%H:%M')
        except ValueError:
            self.page_ref.snack_bar = ft.SnackBar(ft.Text("Formato de hora inválido. Use HH:MM"))
            self.page_ref.snack_bar.open = True
            self.page_ref.update()
            return

        # Collect report configs
        new_reports = []
        for item in self.report_inputs:
            report = item["original"].copy()
            report["drive_folder_id"] = item["drive_input"].value
            report["local_path"] = item["path_input"].value
            new_reports.append(report)
            
        # Update controller
        success = self.controller.update_config(new_time, new_reports)
        
        if success:
            self.page_ref.snack_bar = ft.SnackBar(
                ft.Text("Configuración guardada exitosamente"), 
                bgcolor="#4CAF50"
            )
            self.close_dialog(None)
        else:
            self.page_ref.snack_bar = ft.SnackBar(
                ft.Text("Error al guardar la configuración"), 
                bgcolor="#D32F2F"
            )
            
        self.page_ref.snack_bar.open = True
        self.page_ref.update()

    def close_dialog(self, e):
        self.open = False
        self.page_ref.update()
