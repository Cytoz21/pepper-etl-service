import asyncio
import aiohttp
import os
import base64
import json
from pathlib import Path
from typing import List, Optional
import polars as pl
from ..model import APIRequest, APIResponse, DateRange


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
                    await progress_callback(progress, f"Descargado {i + 1}/{len(tasks)} reportes")
        
        return responses
    
    def save_files(self, responses: List[APIResponse], download_path: str = "downloads") -> List[str]:
        """Save downloaded files to disk and validate them"""
        Path(download_path).mkdir(exist_ok=True)
        saved_files = []
        
        for response in responses:
            if response.filename:
                file_path = Path(download_path) / response.filename
                
                # Save the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Validate the Excel file using Polars
                if self._validate_excel_file(file_path):
                    saved_files.append(str(file_path))
                    print(f"✅ Archivo válido guardado: {response.filename}")
                else:
                    print(f"⚠️ Archivo guardado pero con posibles problemas: {response.filename}")
                    saved_files.append(str(file_path))  # Still add it to the list
        
        return saved_files
    
    def _validate_excel_file(self, file_path: Path) -> bool:
        """Validate Excel file using Polars with fallback to openpyxl"""
        try:
            # Try to read the Excel file with Polars using different engines
            df = None
            
            # First try with fastexcel engine
            try:
                df = pl.read_excel(file_path, engine="fastexcel")
            except Exception:
                # Fallback to openpyxl engine
                try:
                    df = pl.read_excel(file_path, engine="openpyxl")
                except Exception:
                    # Last fallback: use pandas with openpyxl and convert to polars
                    import pandas as pd
                    pandas_df = pd.read_excel(file_path, engine="openpyxl")
                    df = pl.from_pandas(pandas_df)
            
            if df is None:
                print(f"❌ No se pudo leer el archivo {file_path.name}")
                return False
            
            # Basic validations
            if df.is_empty():
                print(f"⚠️ El archivo {file_path.name} está vacío")
                return False
            
            # Check if it has reasonable dimensions
            rows, cols = df.shape
            if rows == 0 or cols == 0:
                print(f"⚠️ El archivo {file_path.name} no tiene datos válidos (filas: {rows}, columnas: {cols})")
                return False
            
            print(f"📊 Archivo {file_path.name}: {rows} filas, {cols} columnas")
            
            # Optional: Log column names for debugging
            if cols > 0:
                column_names = df.columns[:5]  # First 5 columns
                print(f"📋 Primeras columnas: {column_names}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error validando {file_path.name}: {str(e)}")
            return False
    
    def get_file_summary(self, file_path: str) -> dict:
        """Get summary information about an Excel file using Polars"""
        try:
            # Try to read the Excel file with different engines
            df = None
            
            # First try with fastexcel engine
            try:
                df = pl.read_excel(file_path, engine="fastexcel")
            except Exception:
                # Fallback to openpyxl engine
                try:
                    df = pl.read_excel(file_path, engine="openpyxl")
                except Exception:
                    # Last fallback: use pandas with openpyxl and convert to polars
                    import pandas as pd
                    pandas_df = pd.read_excel(file_path, engine="openpyxl")
                    df = pl.from_pandas(pandas_df)
            
            if df is None:
                raise Exception("No se pudo leer el archivo Excel")
            
            summary = {
                'filename': Path(file_path).name,
                'rows': df.shape[0],
                'columns': df.shape[1],
                'column_names': df.columns,
                'file_size_mb': round(Path(file_path).stat().st_size / (1024 * 1024), 2)
            }
            
            # Add sample data (first few rows)
            if not df.is_empty():
                summary['sample_data'] = df.head(3).to_dicts()
            
            return summary
            
        except Exception as e:
            return {
                'filename': Path(file_path).name,
                'error': str(e),
                'file_size_mb': round(Path(file_path).stat().st_size / (1024 * 1024), 2) if Path(file_path).exists() else 0
            }
