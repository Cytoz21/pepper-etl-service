"""
File naming and organization utilities.
Handles dynamic filename generation and folder determination based on Excel content.
"""

from pathlib import Path
from typing import Optional, Tuple
import polars as pl

from .excel_utils import process_excel_data, read_excel_with_fallback


def generate_dynamic_filename_from_df(df) -> Optional[str]:
    """Generate dynamic filename from DataFrame: DD-JY-C format"""
    try:
        if df is None or df.is_empty():
            return None
        
        # Process the data (filter columns and convert types)
        df = process_excel_data(df)
        
        if df is None or df.is_empty():
            return None
        
        # Extract information for filename
        day_digits = None
        fundo_abbrev = "JY"  # Default to Jayanca abbreviation
        cartilla_suffix = "C"  # Default to California
        
        # Get the first row to extract information
        first_row = df.head(1).to_dicts()[0] if not df.is_empty() else {}
        
        # Extract day digits from date column (looking for date-like columns)
        date_columns = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        if not date_columns:
            # Look for columns that might contain dates
            for col in df.columns:
                if df[col].dtype in [pl.Date, pl.Datetime]:
                    date_columns.append(col)
                    break
        
        if date_columns:
            date_value = first_row.get(date_columns[0])
            if date_value:
                # Try to extract day from date
                try:
                    if hasattr(date_value, 'day'):
                        day_digits = f"{date_value.day:02d}"
                    elif isinstance(date_value, str):
                        # Try to parse date string
                        import re
                        date_match = re.search(r'(\d{1,2})', str(date_value))
                        if date_match:
                            day_digits = f"{int(date_match.group(1)):02d}"
                except (ValueError, AttributeError, TypeError):
                    pass
        
        # Extract fundo information
        fundo_columns = [col for col in df.columns if 'fundo' in col.lower()]
        if fundo_columns:
            fundo_value = first_row.get(fundo_columns[0])
            if fundo_value and isinstance(fundo_value, str):
                if 'jayanca' in fundo_value.lower():
                    fundo_abbrev = "JY"
                # Add more fundo abbreviations as needed
        
        # Extract cartilla information - check the last word
        cartilla_columns = [col for col in df.columns if 'cartilla' in col.lower()]
        if cartilla_columns:
            cartilla_value = first_row.get(cartilla_columns[0])
            if cartilla_value and isinstance(cartilla_value, str):
                # Split the cartilla value into words and get the last word
                words = cartilla_value.strip().split()
                if words:
                    last_word = words[-1].lower()
                    if last_word == 'piquillo':
                        cartilla_suffix = "P"
                    elif last_word == 'california':
                        cartilla_suffix = "C"
        
        # Generate filename if we have the day digits
        if day_digits:
            new_filename = f"{day_digits}-{fundo_abbrev}-{cartilla_suffix}.xlsx"
            return new_filename
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error generando nombre dinámico desde DataFrame: {str(e)}")
        return None


def generate_dynamic_filename(file_path: Path) -> Optional[str]:
    """Generate dynamic filename based on Excel content: DD-JY-C format"""
    try:
        df = read_excel_with_fallback(file_path)
        
        # Use the shared method to generate filename from DataFrame
        return generate_dynamic_filename_from_df(df)
        
    except Exception as e:
        print(f"⚠️ Error generando nombre dinámico para {file_path.name}: {str(e)}")
        return None


def determine_target_folder_and_filename(file_path: Path, cartilla_path: Path, ensayos_path: Path) -> Tuple[Path, Optional[str]]:
    """Determine target folder based on Excel content and generate dynamic filename"""
    try:
        df = read_excel_with_fallback(file_path)
        
        if df is None or df.is_empty():
            # Default to cartilla folder if can't read
            return cartilla_path, None
        
        # Process the data (filter columns and convert types)
        df = process_excel_data(df)
        
        if df is None or df.is_empty():
            return cartilla_path, None
        
        # Get the first row to extract information
        first_row = df.head(1).to_dicts()[0] if not df.is_empty() else {}
        
        # Determine target folder based on cartilla content
        target_folder = cartilla_path  # Default
        cartilla_columns = [col for col in df.columns if 'cartilla' in col.lower()]
        
        if cartilla_columns:
            cartilla_value = first_row.get(cartilla_columns[0])
            if cartilla_value and isinstance(cartilla_value, str):
                cartilla_lower = cartilla_value.lower()
                
                # Check for specific patterns
                if "proyecciones: conteos" in cartilla_lower:
                    target_folder = ensayos_path
                    print("📂 Detectado 'PROYECCIONES: CONTEOS' → Carpeta Ensayos")
                elif "cartilla proyección" in cartilla_lower:
                    target_folder = cartilla_path
                    print("📂 Detectado 'Cartilla Proyección' → Carpeta Cartilla")
        
        # Generate dynamic filename
        new_filename = generate_dynamic_filename_from_df(df)
        
        return target_folder, new_filename
        
    except Exception as e:
        print(f"⚠️ Error determinando carpeta para {file_path.name}: {str(e)}")
        # Default to cartilla folder
        return cartilla_path, None
