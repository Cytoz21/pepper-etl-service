import asyncio
import aiohttp
import os
import base64
import json
from pathlib import Path
from typing import List, Optional
from ..model import APIRequest, APIResponse, DateRange
from .utils import (
    has_valid_data,
    validate_excel_file,
    determine_target_folder_and_filename,
    get_file_summary as _get_file_summary
)


class DownloadService:
    def __init__(self):
        self.base_url = f"{os.getenv('API_SCHEME')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}{os.getenv('API_BASE')}{os.getenv('EXCEL_RPT_PATH')}"
        self.authorization = os.getenv('AUTHORIZATION')
        self.cartillas = [492, 493, 624, 669]
        self.fixed_params = {
            'prmstrFundo': '290',
            'prmintCultivo': '2',
            'prmstrRUCEmpresa': '20170040938'
        }
    
    def _build_request(self, cartilla: int, date_range: DateRange) -> APIRequest:
        """Build API request for a specific cartilla and date range"""
        params = {
            **self.fixed_params,
            'prmintCartilla': str(cartilla),
            'prmdatFechaInicio': date_range.start.strftime('%Y-%m-%d'),
            'prmdatFechaFin': date_range.end.strftime('%Y-%m-%d')
        }
        
        headers = {
            'Authorization': self.authorization
        } if self.authorization else {}
        
        return APIRequest(
            url=self.base_url,
            params=params,
            headers=headers
        )
    
    async def download_file(self, session: aiohttp.ClientSession, request: APIRequest, cartilla: int) -> Optional[APIResponse]:
        """Download a single file asynchronously"""
        try:
            async with session.get(request.url, params=request.params, headers=request.headers) as response:
                if response.status == 200:
                    # Get response content as text first
                    response_text = await response.text()
                    
                    # Try to parse as JSON in case the API returns a JSON response with base64 content
                    try:
                        json_response = json.loads(response_text)
                        if isinstance(json_response, dict) and 'content' in json_response:
                            # If it's a JSON response with content field
                            base64_content = json_response['content']
                        else:
                            # If it's just a base64 string directly
                            base64_content = response_text
                    except json.JSONDecodeError:
                        # If it's not JSON, assume it's a direct base64 string
                        base64_content = response_text
                    
                    # Decode base64 content to bytes
                    try:
                        # Remove any whitespace and decode
                        clean_base64 = base64_content.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                        content = base64.b64decode(clean_base64)
                    except Exception as decode_error:
                        print(f"Error decoding base64 for cartilla {cartilla}: {str(decode_error)}")
                        # Fallback: try to get raw bytes if base64 decoding fails
                        content = await response.read()
                    
                    filename = f"reporte_cartilla_{cartilla}_{request.params['prmdatFechaInicio']}_{request.params['prmdatFechaFin']}.xlsx"
                    return APIResponse(
                        content=content,
                        filename=filename,
                        content_type=response.headers.get('content-type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    )
                else:
                    print(f"Error downloading cartilla {cartilla}: HTTP {response.status}")
                    response_text = await response.text()
                    print(f"Response content: {response_text[:200]}...")  # Log first 200 chars for debugging
                    return None
        except Exception as e:
            print(f"Exception downloading cartilla {cartilla}: {str(e)}")
            return None
    
    async def download_all_reports(self, date_range: DateRange, progress_callback=None) -> List[APIResponse]:
        """Download all reports asynchronously"""
        requests = [self._build_request(cartilla, date_range) for cartilla in self.cartillas]
        responses = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, (request, cartilla) in enumerate(zip(requests, self.cartillas)):
                task = self.download_file(session, request, cartilla)
                tasks.append(task)
            
            # Execute all downloads concurrently
            for i, task in enumerate(asyncio.as_completed(tasks)):
                response = await task
                if response:
                    responses.append(response)
                
                # Update progress if callback provided
                if progress_callback:
                    progress = (i + 1) / len(tasks)
                    await progress_callback(progress, f"Procesando {i + 1}/{len(tasks)} reportes")
        
        return responses
    
    def save_files(self, responses: List[APIResponse], download_path: str = "downloads") -> List[str]:
        """Save downloaded files to disk with dynamic naming and organized folders based on content"""
        # Base path for organized storage
        base_path = Path("G:/.shortcut-targets-by-id/1-V4d2pzu_wx0WYYjxK1L6BhB2q-kvuUc/Pimientos/10 Reportes/20. Plantillas/1. RStudio/1. Conteo/Lambayeque")
        
        # Create base directory structure
        cartilla_path = base_path / "1. Cartilla"
        ensayos_path = base_path / "2. Ensayos"
        
        # Create directories if they don't exist
        cartilla_path.mkdir(parents=True, exist_ok=True)
        ensayos_path.mkdir(parents=True, exist_ok=True)
        
        # Fallback to local downloads folder
        Path(download_path).mkdir(exist_ok=True)
        
        saved_files = []
        
        for response in responses:
            if response.filename:
                # Save the file temporarily with original name in local downloads
                temp_file_path = Path(download_path) / response.filename
                
                # Save the file temporarily
                with open(temp_file_path, 'wb') as f:
                    f.write(response.content)
                
                # Check if file has valid data before processing
                if not has_valid_data(temp_file_path):
                    print(f"🚫 Archivo omitido (sin datos): {response.filename}")
                    temp_file_path.unlink()  # Delete empty file
                    continue
                
                # Determine target folder and generate dynamic filename
                target_folder, new_filename = determine_target_folder_and_filename(temp_file_path, cartilla_path, ensayos_path)
                
                # Use new filename if generated, otherwise keep original
                final_filename = new_filename if new_filename else response.filename
                
                # Final file path in the organized structure
                final_file_path = target_folder / final_filename
                
                try:
                    # Copy file to organized location
                    with open(final_file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Remove temporary file
                    temp_file_path.unlink()
                    
                    file_path = final_file_path
                    
                    if new_filename and new_filename != response.filename:
                        print(f"📝 Archivo renombrado y movido: {response.filename} → {target_folder.name}/{final_filename}")
                    else:
                        print(f"📁 Archivo movido a: {target_folder.name}/{final_filename}")
                        
                except Exception as e:
                    print(f"⚠️ Error moviendo archivo a carpeta organizada: {str(e)}")
                    # Keep file in local downloads as fallback
                    if new_filename and new_filename != response.filename:
                        fallback_path = Path(download_path) / new_filename
                        temp_file_path.rename(fallback_path)
                        file_path = fallback_path
                        print(f"📝 Archivo renombrado (local): {response.filename} → {new_filename}")
                    else:
                        file_path = temp_file_path
                
                # Validate the Excel file using Polars
                if validate_excel_file(file_path):
                    saved_files.append(str(file_path))
                    print(f"✅ Archivo válido guardado: {file_path.name}")
                else:
                    print(f"⚠️ Archivo guardado pero con posibles problemas: {file_path.name}")
                    saved_files.append(str(file_path))  # Still add it to the list
        
        return saved_files
    
    def get_file_summary(self, file_path: str) -> dict:
        """Get summary information about an Excel file using Polars with robust handling"""
        return _get_file_summary(file_path)
