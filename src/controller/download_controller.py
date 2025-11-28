from datetime import date
from typing import List, Callable, Optional
from ..model import DateRange, Fundo, Cartilla
from ..service import DownloadService, ConfigLoader


class DownloadController:
    def __init__(self):
        try:
            self.download_service = DownloadService()
        except ValueError as e:
            # Store error for later handling
            self.download_service = None
            self.download_service = None
            self._init_error = str(e)
            
        # Load configuration
        self.config_loader = ConfigLoader()
        self.fundos, self.cartillas = self.config_loader.load_config()
        
        self._is_downloading = False
    
    @property
    def is_downloading(self) -> bool:
        """Check if download is currently in progress"""
        return self._is_downloading
    
    async def download_reports(
        self, 
        start_date: date, 
        end_date: date,
        selected_cartillas: List[int],
        selected_fundo_code: str,
        download_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        completion_callback: Optional[Callable[[List[str]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        zip_output: bool = False
    ) -> None:
        """
        Download all reports for the given date range
        
        Args:
            start_date: Start date for the reports
            end_date: End date for the reports
            progress_callback: Callback for progress updates (progress: float, message: str)
            completion_callback: Callback when download completes (file_paths: List[str])
            error_callback: Callback for error handling (error_message: str)
            download_path: Optional fallback path for local downloads (defaults to "downloads")
            zip_output: If True, bundle all downloaded files into a single ZIP archive
        """
        if self._is_downloading:
            if error_callback:
                error_callback("Ya hay una descarga en progreso")
            return
        
        try:
            self._is_downloading = True
            
            # Check if download service was initialized correctly
            if self.download_service is None:
                raise ValueError(self._init_error)
            
            # Validate dates
            if start_date > end_date:
                raise ValueError("La fecha de inicio no puede ser mayor que la fecha de fin")
            
            # Download reports
            if progress_callback:
                progress_callback(0.1, "Iniciando descarga...")
            
            # Create DateRange object
            from ..model import DateRange
            date_range = DateRange(start=start_date, end=end_date)
            
            responses = await self.download_service.download_all_reports(
                date_range=date_range,
                cartillas=selected_cartillas,
                fundo_code=selected_fundo_code
            )
            
            if progress_callback:
                progress_callback(0.7, f"Descargados {len(responses)} reportes, guardando archivos...")
            
            # Create cartilla map (code to name)
            cartilla_map = {c.code: c.name for c in self.cartillas}
            
            # Save files
            saved_files = self.download_service.save_files(
                responses=responses,
                download_path=download_path,
                cartilla_map=cartilla_map
            )
            
            final_files = saved_files
            
            # Zip files if requested and we have files
            if zip_output and saved_files:
                if progress_callback:
                    progress_callback(0.9, "Comprimiendo archivos...")
                
                import zipfile
                import os
                
                # Create zip filename with timestamp
                timestamp = date.today().strftime("%Y%m%d")
                zip_filename = f"reportes_danper_{timestamp}.zip"
                zip_path = os.path.join(download_path, zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in saved_files:
                        zipf.write(file_path, os.path.basename(file_path))
                        # Optional: Remove original files if we only want the zip
                        # os.remove(file_path) 
                
                final_files = [zip_path]
            
            # Calculate statistics
            total_downloaded = len(responses)
            files_saved = len(saved_files)
            files_omitted = total_downloaded - files_saved
            
            if progress_callback:
                if files_omitted > 0:
                    progress_callback(1.0, f"✅ Guardados: {len(final_files)} archivo(s) | 🚫 Omitidos: {files_omitted} (sin datos)")
                else:
                    progress_callback(1.0, f"✅ Proceso completado: {len(final_files)} archivo(s) guardados")
            
            # Notify completion
            if completion_callback:
                completion_callback(final_files)
                
        except Exception as e:
            error_message = f"Error durante la descarga: {str(e)}"
            if error_callback:
                error_callback(error_message)
        finally:
            self._is_downloading = False
    
    def _create_async_progress_callback(self, callback: Optional[Callable[[float, str], None]]):
        """Create an async wrapper for the progress callback"""
        if not callback:
            return None
            
        async def async_callback(progress: float, message: str):
            callback(progress, message)
        
        return async_callback
    
    def validate_date_range(self, start_date: date, end_date: date) -> tuple[bool, str]:
        """
        Validate the date range
        
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if start_date > end_date:
            return False, "La fecha de inicio no puede ser mayor que la fecha de fin"
        
        if start_date > date.today():
            return False, "La fecha de inicio no puede ser futura"
        
        if end_date > date.today():
            return False, "La fecha de fin no puede ser futura"
        
        # Check if date range is too large (optional validation)
        delta = end_date - start_date
        if delta.days > 365:
            return False, "El rango de fechas no puede ser mayor a 365 días"
        
        return True, ""
