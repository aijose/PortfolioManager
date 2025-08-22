"""CSV parsing and validation utilities for portfolio data."""

import csv
import io
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, field_validator, ValidationError


class CSVHoldingData(BaseModel):
    """Schema for validating CSV holding data."""
    symbol: str
    shares: float
    allocation: float
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Symbol cannot be empty')
        symbol = v.strip().upper()
        if len(symbol) < 1 or len(symbol) > 10:
            raise ValueError('Symbol must be 1-10 characters long')
        if not symbol.isalnum():
            raise ValueError('Symbol must contain only letters and numbers')
        return symbol
    
    @field_validator('shares')
    @classmethod
    def shares_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Shares must be non-negative')
        return v
    
    @field_validator('allocation')
    @classmethod
    def allocation_must_be_valid(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Allocation must be between 0.01 and 100')
        return v


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors."""
    def __init__(self, message: str, row: int = None, field: str = None):
        self.message = message
        self.row = row
        self.field = field
        super().__init__(self.format_message())
    
    def format_message(self):
        if self.row is not None:
            if self.field:
                return f"Row {self.row}, {self.field}: {self.message}"
            else:
                return f"Row {self.row}: {self.message}"
        return self.message


class CSVPortfolioParser:
    """Parser for portfolio CSV files."""
    
    REQUIRED_COLUMNS = ['Symbol', 'Shares', 'Allocation']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def parse_csv_content(self, content: str) -> Tuple[List[CSVHoldingData], List[str], List[str]]:
        """
        Parse CSV content and return validated holdings data.
        
        Returns:
            Tuple of (holdings_data, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        holdings_data = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Validate headers
            if not csv_reader.fieldnames:
                raise CSVValidationError("CSV file appears to be empty")
            
            # Check for required columns (case-insensitive)
            fieldnames_lower = [name.lower().strip() for name in csv_reader.fieldnames]
            required_lower = [col.lower() for col in self.REQUIRED_COLUMNS]
            
            missing_columns = []
            for required_col in required_lower:
                if required_col not in fieldnames_lower:
                    missing_columns.append(required_col.title())
            
            if missing_columns:
                raise CSVValidationError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Create mapping from case-insensitive column names to actual names
            column_mapping = {}
            for actual_name in csv_reader.fieldnames:
                lower_name = actual_name.lower().strip()
                if lower_name in required_lower:
                    column_mapping[lower_name] = actual_name
            
            # Process rows
            row_number = 1  # Header is row 0
            symbols_seen = set()
            total_allocation = 0.0
            
            for row in csv_reader:
                row_number += 1
                
                try:
                    # Skip empty rows
                    if not any(row.values()) or all(not str(v).strip() for v in row.values()):
                        continue
                    
                    # Extract data using case-insensitive mapping
                    symbol = row[column_mapping['symbol']].strip() if row.get(column_mapping['symbol']) else ''
                    shares_str = row[column_mapping['shares']].strip() if row.get(column_mapping['shares']) else ''
                    allocation_str = row[column_mapping['allocation']].strip() if row.get(column_mapping['allocation']) else ''
                    
                    # Convert to appropriate types
                    try:
                        shares = float(shares_str) if shares_str else 0.0
                    except ValueError:
                        raise CSVValidationError(f"Invalid shares value: '{shares_str}'", row_number, "Shares")
                    
                    try:
                        allocation = float(allocation_str) if allocation_str else 0.0
                    except ValueError:
                        raise CSVValidationError(f"Invalid allocation value: '{allocation_str}'", row_number, "Allocation")
                    
                    # Validate data
                    holding_data = CSVHoldingData(
                        symbol=symbol,
                        shares=shares,
                        allocation=allocation
                    )
                    
                    # Check for duplicate symbols
                    if holding_data.symbol in symbols_seen:
                        raise CSVValidationError(f"Duplicate symbol: {holding_data.symbol}", row_number)
                    
                    symbols_seen.add(holding_data.symbol)
                    total_allocation += holding_data.allocation
                    holdings_data.append(holding_data)
                    
                except ValidationError as e:
                    for error in e.errors():
                        field = error['loc'][0] if error['loc'] else 'unknown'
                        message = error['msg']
                        self.errors.append(CSVValidationError(message, row_number, field.title()).format_message())
                except CSVValidationError as e:
                    self.errors.append(e.format_message())
                except Exception as e:
                    self.errors.append(CSVValidationError(f"Unexpected error: {str(e)}", row_number).format_message())
            
            # Check total allocation
            if holdings_data:  # Only check if we have data
                if abs(total_allocation - 100.0) > 0.01:
                    if total_allocation < 99.99:
                        self.warnings.append(f"Total allocation is {total_allocation:.2f}%, which is less than 100%")
                    elif total_allocation > 100.01:
                        self.errors.append(f"Total allocation is {total_allocation:.2f}%, which exceeds 100%")
            
            # If no data was processed
            if not holdings_data and not self.errors:
                self.errors.append("No valid holding data found in CSV file")
        
        except CSVValidationError as e:
            self.errors.append(e.format_message())
        except Exception as e:
            self.errors.append(f"Failed to parse CSV file: {str(e)}")
        
        return holdings_data, self.errors, self.warnings
    
    def validate_file_size(self, content: str, max_size_mb: int = 1) -> bool:
        """Validate file size."""
        size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if size_mb > max_size_mb:
            self.errors.append(f"File size ({size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
            return False
        return True
    
    def generate_sample_csv(self) -> str:
        """Generate a sample CSV file content for user reference."""
        sample_data = [
            ['Symbol', 'Shares', 'Allocation'],
            ['AAPL', '100', '25.0'],
            ['MSFT', '80', '20.0'],
            ['GOOGL', '45', '15.0'],
            ['TSLA', '50', '10.0'],
            ['JPM', '75', '10.0'],
            ['JNJ', '60', '8.0'],
            ['VTI', '200', '7.0'],
            ['BND', '500', '5.0']
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(sample_data)
        return output.getvalue()