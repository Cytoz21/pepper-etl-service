"""
Excel file processing utilities.
Handles reading, validating, and processing Excel files with robust fallback mechanisms.
"""

from pathlib import Path
import polars as pl


def process_excel_data(df):
    """Process Excel data: filter columns and convert data types"""
    try:
        if df is None or df.is_empty():
            return df
        
        # Filter out unwanted columns (case insensitive)
        columns_to_exclude = ['deskpit']  # Solo excluir DesKPIT, no Valor
        filtered_columns = []
        
        for col in df.columns:
            if col.lower() not in columns_to_exclude:
                filtered_columns.append(col)
        
        # Select only the filtered columns
        if filtered_columns:
            df = df.select(filtered_columns)
        
        # Convert specific columns to numeric
        columns_to_convert = ['muestra', 'valor']
        
        for col_name in columns_to_convert:
            # Find column with case-insensitive match
            matching_col = None
            for col in df.columns:
                if col.lower() == col_name.lower():
                    matching_col = col
                    break
            
            if matching_col:
                try:
                    # Convert to numeric, handling errors gracefully
                    df = df.with_columns(
                        pl.col(matching_col).cast(pl.Float64, strict=False).alias(matching_col)
                    )
                    print(f"✅ Columna '{matching_col}' convertida a numérico")
                except Exception as e:
                    print(f"⚠️ No se pudo convertir columna '{matching_col}' a numérico: {str(e)}")
        
        return df
        
    except Exception as e:
        print(f"⚠️ Error procesando datos del Excel: {str(e)}")
        return df


def read_excel_with_fallback(file_path: Path):
    """
    Read Excel file with multiple fallback strategies.
    Returns a Polars DataFrame or None if reading fails.
    """
    df = None
    
    # Try different engines to read the file
    try:
        df = pl.read_excel(file_path, engine="fastexcel")
    except Exception:
        try:
            df = pl.read_excel(file_path, engine="openpyxl")
        except Exception:
            try:
                import pandas as pd
                import pyarrow as pa
                
                pandas_df = pd.read_excel(file_path, engine="openpyxl")
                
                # Convert with proper handling
                try:
                    df = pl.from_pandas(pandas_df)
                except Exception:
                    try:
                        arrow_table = pa.Table.from_pandas(pandas_df)
                        df = pl.from_arrow(arrow_table)
                    except Exception:
                        # Convert dtypes manually
                        for col in pandas_df.columns:
                            if pandas_df[col].dtype.name.startswith('Int'):
                                pandas_df[col] = pandas_df[col].astype('float64')
                            elif pandas_df[col].dtype.name == 'object':
                                pandas_df[col] = pandas_df[col].astype('string')
                        df = pl.from_pandas(pandas_df)
            except ImportError:
                return None
    
    return df


def has_valid_data(file_path: Path) -> bool:
    """Check if Excel file has valid data (more than just headers)"""
    try:
        df = read_excel_with_fallback(file_path)
        
        if df is None:
            return False
        
        # Process the data (filter columns and convert types)
        df = process_excel_data(df)
        
        # Check if DataFrame is empty after processing
        if df is None or df.is_empty():
            return False
        
        # Check if it has reasonable dimensions (more than just headers)
        rows, cols = df.shape
        
        # Must have at least 1 data row (excluding headers) and at least 1 column
        if rows <= 0 or cols <= 0:
            return False
        
        # Additional validation: check if there's actual data content
        # (not just empty rows with NaN/null values)
        try:
            # Count non-null values across all columns
            non_null_count = 0
            for col in df.columns:
                non_null_count += df[col].null_count()
            
            # If all values are null, consider it empty
            total_cells = rows * cols
            if non_null_count == total_cells:
                return False
            
            # If we have very few non-null values relative to total cells, might be empty
            if total_cells > 0 and (total_cells - non_null_count) < (total_cells * 0.1):  # Less than 10% data
                return False
                
        except Exception:
            # If we can't check null values, assume it's valid if it has rows/cols
            pass
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error verificando datos en {file_path.name}: {str(e)}")
        return False


def validate_excel_file(file_path: Path) -> bool:
    """Validate Excel file using Polars with robust fallback handling"""
    try:
        df = read_excel_with_fallback(file_path)
        
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


def get_file_summary(file_path: str) -> dict:
    """Get summary information about an Excel file using Polars with robust handling"""
    try:
        df = read_excel_with_fallback(Path(file_path))
        
        if df is None:
            raise Exception("No se pudo leer el archivo Excel")
        
        # Process the data (filter columns and convert types)
        df = process_excel_data(df)
        
        if df is None:
            raise Exception("No se pudo procesar el archivo Excel")
        
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
