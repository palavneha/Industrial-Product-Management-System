from typing import List, Optional, Dict, Iterable, Sequence
import aspose.pycore
import aspose.pydrawing
import aspose.slides
import aspose.slides.ai
import aspose.slides.animation
import aspose.slides.charts
import aspose.slides.dom.ole
import aspose.slides.effects
import aspose.slides.excel
import aspose.slides.export
import aspose.slides.export.xaml
import aspose.slides.importing
import aspose.slides.ink
import aspose.slides.lowcode
import aspose.slides.mathtext
import aspose.slides.slideshow
import aspose.slides.smartart
import aspose.slides.spreadsheet
import aspose.slides.theme
import aspose.slides.util
import aspose.slides.vba
import aspose.slides.warnings

class ExcelDataCell:
    '''Represents a single cell in an Excel workbook.'''
    @property
    def value(self) -> any:
        '''Gets the value contained in the Excel cell.'''
        ...

    @property
    def name(self) -> str:
        '''Gets the name of the chart data cell.'''
        ...

    @property
    def row(self) -> int:
        '''Gets the zero-based index of the row in the worksheet where the cell is located.
                    Read-only :py:class:`int`.'''
        ...

    @property
    def column(self) -> int:
        '''Gets the zero-based index of the column in the worksheet where the cell is located.
                    Read-only :py:class:`int`.'''
        ...

    ...

class ExcelDataWorkbook:
    '''Represents a workbook that provides access to Excel data for general use.'''
    def __init__(self, file_path: str):
        '''Initializes a new instance using the specified file path.
        :param file_path: The full path to the Excel workbook file.'''
        ...

    def __init__(self, stream: io.RawIOBase):
        '''Initializes a new instance of the class using the provided stream.
        :param stream: A stream containing the Excel workbook data.'''
        ...

    @overload
    def get_cell(self, worksheet_index: int, row: int, column: int) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its index and cell coordinates.
        :param worksheet_index: Zero-based index of the worksheet.
        :param row: Zero-based row index of the cell.
        :param column: Zero-based column index of the cell.
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_name: str, row: int, column: int) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its name and cell coordinates.
        :param worksheet_name: The name of the worksheet.
        :param row: Zero-based row index of the cell.
        :param column: Zero-based column index of the cell.
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_index: int, cell_name: str) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its index and Excel-style cell name (e.g., "B2").
        :param worksheet_index: Zero-based index of the worksheet.
        :param cell_name: The Excel-style cell reference (e.g., "A1", "C5").
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_name: str, cell_name: str) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using Excel-style cell name (e.g., "B2").
        :param worksheet_name: The name of the worksheet.
        :param cell_name: The Excel-style cell reference (e.g., "A1", "C5").
        :returns: The cell at the specified location.'''
        ...

    def get_cells(self, formula: str, skip_hidden_cells: bool) -> Sequence[IExcelDataCell]:
        '''Retrieves a collection of cells from the workbook that match the specified formula.
        :param formula: A formula or range expression (e.g., "Sheet1!A1:B3") used to identify target cells.
        :param skip_hidden_cells: If ``true``, hidden cells (e.g., in hidden rows or columns) will be excluded from the result.
        :returns: A read-only list of cells that match the specified formula.'''
        ...

    def get_charts_from_worksheet(self, worksheet_name: str) -> List[PositionedString]:
        '''Retrieves a dictionary containing the indexes and names of all charts in the specified worksheet of an Excel workbook.
        :param worksheet_name: The name of the worksheet to search for charts.
        :returns: A list of :py:class:`aspose.slides.PositionedString` where the key is the chart index and the value is the chart name.'''
        ...

    def get_worksheet_names(self) -> List[str]:
        '''Retrieves the names of all worksheets contained in the Excel workbook.
        :returns: A list of worksheet names'''
        ...

    ...

class IExcelDataCell:
    '''Represents a single cell in an Excel workbook.'''
    @property
    def value(self) -> any:
        '''Gets the value contained in the Excel cell.
                    Read-only :py:class:`any`.'''
        ...

    @property
    def name(self) -> str:
        '''Gets the name of the chart data cell.
                    Read-only :py:class:`str`.'''
        ...

    @property
    def row(self) -> int:
        '''Gets the zero-based index of the row in the worksheet where the cell is located.
                    Read-only :py:class:`int`.'''
        ...

    @property
    def column(self) -> int:
        '''Gets the zero-based index of the column in the worksheet where the cell is located.
                    Read-only :py:class:`int`.'''
        ...

    ...

class IExcelDataWorkbook:
    '''Represents a workbook that provides access to Excel data for general use.'''
    @overload
    def get_cell(self, worksheet_index: int, row: int, column: int) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its index and cell coordinates.
        :param worksheet_index: Zero-based index of the worksheet.
        :param row: Zero-based row index of the cell.
        :param column: Zero-based column index of the cell.
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_name: str, row: int, column: int) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its name and cell coordinates.
        :param worksheet_name: The name of the worksheet.
        :param row: Zero-based row index of the cell.
        :param column: Zero-based column index of the cell.
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_index: int, cell_name: str) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using its index and Excel-style cell name (e.g., "B2").
        :param worksheet_index: Zero-based index of the worksheet.
        :param cell_name: The Excel-style cell reference (e.g., "A1", "C5").
        :returns: The cell at the specified location.'''
        ...

    @overload
    def get_cell(self, worksheet_name: str, cell_name: str) -> IExcelDataCell:
        '''Retrieves a cell from the specified worksheet using Excel-style cell name (e.g., "B2").
        :param worksheet_name: The name of the worksheet.
        :param cell_name: The Excel-style cell reference (e.g., "A1", "C5").
        :returns: The cell at the specified location.'''
        ...

    def get_cells(self, formula: str, skip_hidden_cells: bool) -> Sequence[IExcelDataCell]:
        '''Retrieves a collection of cells from the workbook that match the specified formula.
        :param formula: A formula or range expression (e.g., "Sheet1!A1:B3") used to identify target cells.
        :param skip_hidden_cells: If ``true``, hidden cells (e.g., in hidden rows or columns) will be excluded from the result.
        :returns: A read-only list of cells that match the specified formula.'''
        ...

    def get_charts_from_worksheet(self, worksheet_name: str) -> List[PositionedString]:
        '''Retrieves a dictionary containing the indexes and names of all charts in the specified worksheet of an Excel workbook.
        :param worksheet_name: The name of the worksheet to search for charts.
        :returns: A list of :py:class:`aspose.slides.PositionedString` where the key is the chart index and the value is the chart name.'''
        ...

    def get_worksheet_names(self) -> List[str]:
        '''Retrieves the names of all worksheets contained in the Excel workbook.
        :returns: A list of worksheet names'''
        ...

    ...

