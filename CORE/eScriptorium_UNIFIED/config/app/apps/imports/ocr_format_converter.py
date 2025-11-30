"""
OCR Format Converter - Integration with UB-Mannheim ocr-fileformat
===================================================================

This module provides automatic conversion of various OCR formats to PAGE XML
using the ocr-fileformat tool from UB-Mannheim.

Supported formats:
- ABBYY FineReader XML → PAGE XML
- hOCR HTML → PAGE XML
- ALTO XML → PAGE XML (alternative to built-in parser)
- Text → PAGE XML
- And more...

Repository: https://github.com/UB-Mannheim/ocr-fileformat
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from lxml import etree

logger = logging.getLogger(__name__)


class OcrFormatConverter:
    """
    Wrapper for UB-Mannheim ocr-fileformat conversion tools.
    
    Converts various OCR formats to PAGE XML format that eScriptorium can parse.
    """
    
    # Path to ocr-fileformat installation
    OCR_FILEFORMAT_PATH = Path(os.environ.get(
        'OCR_FILEFORMAT_PATH',
        '/opt/ocr-fileformat'  # Default Docker path
    ))
    
    # Supported conversions (source format → script name)
    CONVERTERS = {
        'abbyy': 'abbyy__page',
        'hocr': 'hocr__page',
        'alto': 'alto__page',
        'text': 'text__page',
        'gcv': 'gcv__page',  # Google Cloud Vision
    }
    
    def __init__(self):
        """Initialize converter and check availability"""
        self.available = self._check_installation()
        
        if not self.available:
            logger.warning(
                f"ocr-fileformat not found at {self.OCR_FILEFORMAT_PATH}. "
                "Format conversion will be disabled."
            )
    
    def _check_installation(self) -> bool:
        """Check if ocr-fileformat is installed"""
        script_path = self.OCR_FILEFORMAT_PATH / 'script' / 'transform'
        return script_path.exists() and script_path.is_dir()
    
    def is_supported(self, format_name: str) -> bool:
        """Check if a format is supported for conversion"""
        return format_name.lower() in self.CONVERTERS
    
    def convert_to_page_xml(
        self,
        input_content: str,
        source_format: str,
        filename: str = "input.xml"
    ) -> Optional[str]:
        """
        Convert OCR format to PAGE XML.
        
        Args:
            input_content: String content of the source file
            source_format: Source format name ('abbyy', 'hocr', 'alto', etc.)
            filename: Original filename (for logging)
        
        Returns:
            PAGE XML content as string, or None if conversion failed
        
        Raises:
            ValueError: If format is not supported
            RuntimeError: If conversion fails
        """
        if not self.available:
            raise RuntimeError(
                "ocr-fileformat is not installed. "
                "Please install it to use format conversion."
            )
        
        format_key = source_format.lower()
        if format_key not in self.CONVERTERS:
            raise ValueError(
                f"Unsupported format: {source_format}. "
                f"Supported: {list(self.CONVERTERS.keys())}"
            )
        
        script_name = self.CONVERTERS[format_key]
        script_path = self.OCR_FILEFORMAT_PATH / 'script' / 'transform' / script_name
        
        if not script_path.exists():
            raise RuntimeError(
                f"Conversion script not found: {script_path}"
            )
        
        # Create temporary file for input
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{format_key}',
            delete=False,
            encoding='utf-8'
        ) as tmp_input:
            tmp_input.write(input_content)
            tmp_input_path = tmp_input.name
        
        try:
            # Run conversion
            logger.info(
                f"Converting {filename} from {source_format} to PAGE XML "
                f"using {script_name}"
            )
            
            result = subprocess.run(
                ['python3', str(script_path), tmp_input_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=60  # 60 second timeout
            )
            
            page_xml = result.stdout
            
            # Validate output is valid XML
            try:
                etree.fromstring(page_xml.encode('utf-8'))
            except etree.XMLSyntaxError as e:
                logger.error(f"Invalid PAGE XML output: {e}")
                raise RuntimeError(f"Conversion produced invalid XML: {e}")
            
            logger.info(
                f"Successfully converted {filename} from {source_format} to PAGE XML "
                f"({len(page_xml)} bytes)"
            )
            
            return page_xml
            
        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for {filename}")
            raise RuntimeError(f"Conversion timeout (>60s) for {filename}")
            
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Conversion failed for {filename}: {e.stderr}"
            )
            raise RuntimeError(
                f"Conversion failed: {e.stderr or 'Unknown error'}"
            )
            
        finally:
            # Clean up temporary file
            try:
                Path(tmp_input_path).unlink()
            except Exception:
                pass
    
    def detect_format(self, xml_content: str, filename: str) -> Optional[str]:
        """
        Detect OCR format from XML content.
        
        Args:
            xml_content: XML content as string
            filename: Original filename
        
        Returns:
            Format name ('abbyy', 'hocr', 'alto') or None if unknown
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError:
            # Try as HTML (for hOCR)
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(xml_content, 'html.parser')
                if soup.find(class_='ocr_page') or soup.find(class_='ocr_line'):
                    return 'hocr'
            except Exception:
                pass
            return None
        
        # Check namespace for ABBYY
        if root.nsmap:
            for ns in root.nsmap.values():
                if ns and 'abbyy' in ns.lower():
                    return 'abbyy'
        
        # Check for ALTO
        if 'alto' in root.tag.lower():
            return 'alto'
        
        # Check namespace for ALTO
        if root.nsmap:
            for ns in root.nsmap.values():
                if ns and 'alto' in ns.lower():
                    return 'alto'
        
        return None


# Global converter instance
_converter = None


def get_converter() -> OcrFormatConverter:
    """Get global converter instance (singleton)"""
    global _converter
    if _converter is None:
        _converter = OcrFormatConverter()
    return _converter
