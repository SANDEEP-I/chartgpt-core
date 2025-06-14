# app/services/file_parser.py

import os
import pandas as pd
from typing import Tuple

class FileParser:
    """
    File parser service: handles CSV & Excel file parsing with dynamic encoding handling.
    """

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
    ENCODING_TRIALS = ["utf-8", "utf-16", "latin1"]

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in FileParser.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        return ext

    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, pd.DataFrame]:
        ext = FileParser.detect_file_type(file_path)

        if ext == ".csv":
            for encoding in FileParser.ENCODING_TRIALS:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    return "csv", df
                except UnicodeDecodeError:
                    continue
            raise ValueError("Failed to decode CSV file with supported encodings.")

        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(file_path)
            return "excel", df

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def save_temp_file(upload_file) -> str:
        """
        Save uploaded file to temp directory for parsing.
        """
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        file_path = os.path.join(temp_dir, upload_file.filename)

        with open(file_path, "wb") as f:
            f.write(upload_file.file.read())

        return file_path
