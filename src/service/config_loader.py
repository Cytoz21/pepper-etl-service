import csv
import os
from typing import List, Tuple
from ..model.config import Fundo, Cartilla

class ConfigLoader:
    def __init__(self, csv_path: str = "Libro1.csv"):
        self.csv_path = csv_path

    def load_config(self) -> Tuple[List[Fundo], List[Cartilla]]:
        """
        Load Fundos and Cartillas from the CSV file.
        Returns a tuple containing a list of Fundos and a list of Cartillas.
        """
        fundos = []
        cartillas = []

        if not os.path.exists(self.csv_path):
            # Fallback or empty if file doesn't exist, though it should.
            print(f"Warning: Config file {self.csv_path} not found.")
            return [], []

        try:
            with open(self.csv_path, mode='r', encoding='utf-8-sig') as f:
                # Using csv.reader to handle the semicolon delimiter
                reader = csv.reader(f, delimiter=';')
                
                # Skip header
                next(reader, None)

                for row in reader:
                    # Ensure row has enough columns
                    if not row:
                        continue

                    # Parse Fundo (Columns 0 and 1)
                    if len(row) >= 2:
                        fundo_name = row[0].strip()
                        fundo_code = row[1].strip()
                        if fundo_name and fundo_code:
                            fundos.append(Fundo(name=fundo_name, code=fundo_code))

                    # Parse Cartilla (Columns 3 and 4)
                    if len(row) >= 5:
                        cartilla_name = row[3].strip()
                        cartilla_code = row[4].strip()
                        if cartilla_name and cartilla_code:
                            try:
                                cartillas.append(Cartilla(name=cartilla_name, code=int(cartilla_code)))
                            except ValueError:
                                print(f"Warning: Invalid cartilla code '{cartilla_code}' for '{cartilla_name}'")

        except Exception as e:
            print(f"Error loading config from {self.csv_path}: {e}")
            return [], []

        return fundos, cartillas
