"""
Module for processing CSV files with payment data.
Provides functionality for reading, parsing, filtering by payment status,
and preparing data for further processing.
"""

import os
from typing import Dict, List, Optional, Union

import pandas as pd
from pandas import DataFrame
import logging

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Class for processing CSV files with payment data."""

    def __init__(self, file_path: str):
        """
        Initialize the CSV processor with a file path.

        Args:
            file_path: Path to the CSV file
        """
        self.file_path: str = file_path
        self._data: Optional[DataFrame] = None
        logger.info(f"CSVProcessor initialized with file: {self.file_path}")

    def read_csv(self, encoding: str = 'utf-8', **kwargs) -> DataFrame:
        """
        Read CSV file and return DataFrame.

        Args:
            encoding: File encoding (default: utf-8)
            **kwargs: Additional arguments to pass to pandas.read_csv

        Returns:
            DataFrame with CSV data

        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.EmptyDataError: If the file is empty
            pd.errors.ParserError: If the file cannot be parsed
        """
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")

        try:
            self._data = pd.read_csv(self.file_path, encoding=encoding, **kwargs)
            logger.info(f"CSV file loaded: {self.file_path}, rows: {len(self._data)}")
            return self._data
        except Exception as e:
            logger.error(f"Error reading CSV file {self.file_path}: {e}")
            raise type(e)(f"Error reading CSV file {self.file_path}: {str(e)}")

    def filter_by_status(self, status: str = "Оплачено") -> DataFrame:
        """
        Filter data by payment status.

        Args:
            status: Payment status to filter by (default: "Оплачено")

        Returns:
            DataFrame with filtered data

        Raises:
            ValueError: If data hasn't been loaded yet
            KeyError: If status column doesn't exist in the data
        """
        if self._data is None:
            logger.error("Data not loaded. Call read_csv() first.")
            raise ValueError("Data not loaded. Call read_csv() first.")

        # Try different possible column names for status
        status_columns = ["status", "статус", "Status", "Статус"]
        
        for col in status_columns:
            if col in self._data.columns:
                logger.info(f"Filtering by status: {status} in column: {col}")
                return self._data[self._data[col] == status].copy()
        
        logger.error(f"Status column not found in CSV. Available columns: {', '.join(self._data.columns)}")
        raise KeyError(f"Status column not found in CSV. Available columns: {', '.join(self._data.columns)}")

    def prepare_data(self, required_columns: Optional[List[str]] = None, status: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> DataFrame:
        """
        Prepare data for further processing.
        
        This method can be customized based on specific requirements.
        By default, it:
        1. Drops duplicates
        2. Fills missing values
        3. Converts date columns to datetime
        4. Selects only required columns if specified
        5. Фильтрует по статусу, если передан status
        6. Фильтрует по дате, если переданы date_from/date_to

        Args:
            required_columns: List of columns to keep in the result
            status: Payment status to filter by (если None — не фильтровать)
            date_from: Start date (YYYY-MM-DD) for filtering
            date_to: End date (YYYY-MM-DD) for filtering

        Returns:
            Processed DataFrame or dictionary of DataFrames

        Raises:
            ValueError: If data hasn't been loaded yet
        """
        if self._data is None:
            logger.error("Data not loaded. Call read_csv() first.")
            raise ValueError("Data not loaded. Call read_csv() first.")

        # Make a copy to avoid modifying the original data with filtered data
        processed_data: DataFrame = self._data.copy()

        if status is not None:
            status_columns = ["status", "статус", "Status", "Статус"]
            for col in status_columns:
                if col in processed_data.columns:
                    processed_data = processed_data[processed_data[col] == status].copy()
                    break
            else:
                logger.error(f"Status column not found in CSV. Available columns: {', '.join(processed_data.columns)}")
                raise KeyError(f"Status column not found in CSV. Available columns: {', '.join(processed_data.columns)}")
        
        # Drop duplicates
        processed_data = processed_data.drop_duplicates()
        
        # Fill missing values (customize as needed)
        processed_data = processed_data.fillna({
            col: "" if processed_data[col].dtype == "object" else 0
            for col in processed_data.columns
        })
        
        # Convert date columns to datetime
        date_columns = [
            col for col in processed_data.columns
            if any(date_keyword in col.lower() for date_keyword in ["date", "дата", "time", "время"])
        ]
        for col in date_columns:
            try:
                processed_data[col] = pd.to_datetime(processed_data[col], errors='coerce', dayfirst=True)
            except Exception as e:
                logger.warning(f"Failed to parse dates in column {col}: {e}")
        # Фильтрация по дате
        if (date_from or date_to) and date_columns:
            date_col = date_columns[0]
            if date_from:
                processed_data = processed_data[processed_data[date_col] >= pd.to_datetime(date_from)]
            if date_to:
                processed_data = processed_data[processed_data[date_col] <= pd.to_datetime(date_to)]
        if required_columns:
            available_columns = [col for col in required_columns if col in processed_data.columns]
            if not available_columns:
                logger.error(f"None of the required columns {required_columns} found in data")
                raise ValueError(f"None of the required columns {required_columns} found in data")
            processed_data = processed_data[available_columns]
        
        return processed_data

    def get_summary(self) -> Dict:
        """
        Get summary statistics of the data.

        Returns:
            Dictionary with summary information

        Raises:
            ValueError: If data hasn't been loaded yet
        """
        if self._data is None:
            raise ValueError("Data not loaded. Call read_csv() first.")
            
        return {
            "total_rows": len(self._data),
            "columns": list(self._data.columns),
            "missing_values": self._data.isnull().sum().to_dict(),
            "data_types": self._data.dtypes.astype(str).to_dict()
        }


def process_payment_csv(file_path: str, status: str = "Оплачено", required_columns: Optional[List[str]] = None) -> DataFrame:
    """
    Convenience function to process a payment CSV file in one go.
    
    Args:
        file_path: Path to the CSV file
        status: Payment status to filter by (default: "Оплачено")
        required_columns: List of columns to keep in the result
        
    Returns:
        Processed DataFrame with filtered data
    """
    processor = CSVProcessor(file_path)
    processor.read_csv()
    filtered_data = processor.filter_by_status(status)
    return processor.prepare_data(required_columns)
