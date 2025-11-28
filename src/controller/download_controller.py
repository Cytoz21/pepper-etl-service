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
        error_callback: Optional[Callable[[str], None]] = None
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
            
            # Calculate statistics
            total_downloaded = len(responses)
            files_saved = len(saved_files)
            files_omitted = total_downloaded - files_saved
            
            if progress_callback:
                if files_omitted > 0:
                    progress_callback(1.0, f"✅ Guardados: {files_saved} archivos | 🚫 Omitidos: {files_omitted} (sin datos)")
                else:
                    progress_callback(1.0, f"✅ Proceso completado: {files_saved} archivos guardados")
            
            # Notify completion
            if completion_callback:
                # In web mode, we might need to move files to assets or return relative paths
                # For now, we return the absolute paths and let the View handle the logic
                completion_callback(saved_files)
                
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
