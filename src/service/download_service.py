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
        # Get environment variables with defaults for debugging
        api_scheme = os.getenv('API_SCHEME', 'http')
        api_host = os.getenv('API_HOST')
        api_port = os.getenv('API_PORT')
        api_base = os.getenv('API_BASE', '/WS_AB/api')
        excel_rpt_path = os.getenv('EXCEL_RPT_PATH', '/Fitosanidad/ZABG_ExcelRptEvaluacionesXVariable')
        
        # Validate required environment variables
        if not api_host or not api_port:
            raise ValueError(
                "Missing required environment variables. Please ensure .env file exists with:\n"
                "API_HOST and API_PORT are required.\n"
                "See .env.example for configuration template."
            )
        
        self.base_url = f"{api_scheme}://{api_host}:{api_port}{api_base}{excel_rpt_path}"
        self.authorization = os.getenv('AUTHORIZATION')
        self.base_url = f"{api_scheme}://{api_host}:{api_port}{api_base}{excel_rpt_path}"
        self.authorization = os.getenv('AUTHORIZATION')
        # Default fixed params (can be overridden)
        self.fixed_params = {
            'prmintCultivo': '2',
            'prmstrRUCEmpresa': '20170040938'
        }
    
    def _build_request(self, cartilla: int, date_range: DateRange, fundo_code: str) -> APIRequest:
        """Build API request for a specific cartilla and date range"""
        params = {
            **self.fixed_params,
            'prmstrFundo': fundo_code,
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
    
    async def download_all_reports(
        self, 
        date_range: DateRange, 
        cartillas: List[int], 
        fundo_code: str,
        progress_callback=None
    ) -> List[APIResponse]:
        """Download all reports asynchronously"""
        requests = [self._build_request(cartilla, date_range, fundo_code) for cartilla in cartillas]
        responses = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, (request, cartilla) in enumerate(zip(requests, cartillas)):
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
    
    def save_files(self, responses: List[APIResponse], download_path: str, cartilla_map: dict = None) -> List[str]:
        """Save downloaded files directly to download path with cartilla names"""
        # Use provided download path as base
        base_path = Path(download_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
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
                
                # Extract cartilla code from filename (e.g., reporte_cartilla_623_2025-11-17_2025-11-19.xlsx)
                import re
                match = re.search(r'cartilla_(\d+)_', response.filename)
                cartilla_code = int(match.group(1)) if match else None
                
                # Generate filename based on cartilla name
                if cartilla_code and cartilla_map and cartilla_code in cartilla_map:
                    cartilla_name = cartilla_map[cartilla_code]
                    # Sanitize filename (remove invalid characters)
                    safe_name = re.sub(r'[<>:"/\\|?*]', '_', cartilla_name)
                    final_filename = f"{safe_name}.xlsx"
                else:
                    final_filename = response.filename
                
                # Final file path
                final_file_path = base_path / final_filename
                
                # Move/rename file
                temp_file_path.rename(final_file_path)
                file_path = final_file_path
                
                if final_filename != response.filename:
                    print(f"📝 Archivo renombrado: {response.filename} → {final_filename}")
                else:
                    print(f"📁 Archivo guardado: {final_filename}")
                
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
