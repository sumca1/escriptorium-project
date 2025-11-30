"""
BiblIA PDF Export Module
=========================
Export transcriptions to PDF with:
- Searchable text layer
- RTL support (Hebrew/Arabic)
- Original image background
- Multiple layout options
"""

import io
from typing import Optional, List
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, gray
from PIL import Image as PILImage
from arabic_reshaper import reshape
from bidi.algorithm import get_display

from django.conf import settings
from core.models import Document, DocumentPart, Line, LineTranscription, Transcription


class PDFExporter:
    """
    Export transcriptions to PDF with various options
    """
    
    # Layout options
    LAYOUT_TEXT_ONLY = 'text_only'
    LAYOUT_IMAGE_ONLY = 'image_only'
    LAYOUT_IMAGE_TEXT_OVERLAY = 'image_text_overlay'
    LAYOUT_IMAGE_TEXT_SIDEBYSIDE = 'image_text_side_by_side'
    
    def __init__(self, document: Document, transcription: Transcription):
        self.document = document
        self.transcription = transcription
        self.buffer = io.BytesIO()
        self.canvas = None
        
        # Register Hebrew font (using DejaVu which has good Hebrew support)
        try:
            font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            pdfmetrics.registerFont(TTFont('Hebrew', font_path))
            self.font_name = 'Hebrew'
        except:
            # Fallback to Helvetica if DejaVu not available
            self.font_name = 'Helvetica'
    
    def export(
        self,
        layout: str = LAYOUT_TEXT_ONLY,
        include_metadata: bool = True,
        font_size: int = 12,
        line_spacing: float = 1.5
    ) -> io.BytesIO:
        """
        Export to PDF with specified options
        
        Args:
            layout: One of the LAYOUT_* constants
            include_metadata: Include document metadata
            font_size: Text font size
            line_spacing: Line spacing multiplier
            
        Returns:
            BytesIO buffer with PDF content
        """
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)
        width, height = A4
        
        # Add metadata
        if include_metadata:
            self._add_metadata()
        
        # Export based on layout
        if layout == self.LAYOUT_TEXT_ONLY:
            self._export_text_only(font_size, line_spacing)
        elif layout == self.LAYOUT_IMAGE_ONLY:
            self._export_image_only()
        elif layout == self.LAYOUT_IMAGE_TEXT_OVERLAY:
            self._export_image_text_overlay(font_size)
        elif layout == self.LAYOUT_IMAGE_TEXT_SIDEBYSIDE:
            self._export_image_text_side_by_side(font_size, line_spacing)
        else:
            raise ValueError(f"Unknown layout: {layout}")
        
        self.canvas.save()
        self.buffer.seek(0)
        return self.buffer
    
    def _add_metadata(self):
        """Add PDF metadata"""
        self.canvas.setTitle(self.document.name)
        self.canvas.setAuthor(self.document.owner.username if self.document.owner else "BiblIA")
        self.canvas.setSubject(f"Transcription: {self.transcription.name}")
        self.canvas.setCreator("BiblIA eScriptorium Platform")
    
    def _format_rtl_text(self, text: str) -> str:
        """
        Format RTL text for PDF display
        """
        if not text:
            return ""
        
        # Check if text contains Hebrew or Arabic
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in text)
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        if has_hebrew or has_arabic:
            # Reshape Arabic if needed
            if has_arabic:
                text = reshape(text)
            # Apply BiDi algorithm
            return get_display(text)
        
        return text
    
    def _export_text_only(self, font_size: int, line_spacing: float):
        """Export text-only PDF"""
        width, height = A4
        margin = 20 * mm
        x = margin
        y = height - margin
        
        self.canvas.setFont(self.font_name, font_size)
        line_height = font_size * line_spacing
        
        # Get all parts and lines
        parts = DocumentPart.objects.filter(document=self.document).order_by('order')
        
        for part in parts:
            lines = Line.objects.filter(document_part=part).order_by('order')
            
            for line in lines:
                # Get transcription for this line
                try:
                    lt = LineTranscription.objects.get(
                        line=line,
                        transcription=self.transcription
                    )
                    text = lt.content or ""
                except LineTranscription.DoesNotExist:
                    text = ""
                
                if not text:
                    continue
                
                # Format RTL text
                formatted_text = self._format_rtl_text(text)
                
                # Check if we need a new page
                if y < margin + line_height:
                    self.canvas.showPage()
                    self.canvas.setFont(self.font_name, font_size)
                    y = height - margin
                
                # Draw text (right-aligned for RTL)
                has_rtl = any('\u0590' <= char <= '\u06FF' for char in text)
                if has_rtl:
                    # Right-aligned for RTL
                    self.canvas.drawRightString(width - margin, y, formatted_text)
                else:
                    # Left-aligned for LTR
                    self.canvas.drawString(x, y, formatted_text)
                
                y -= line_height
            
            # Add space between parts
            y -= line_height * 0.5
    
    def _export_image_only(self):
        """Export images-only PDF"""
        width, height = A4
        
        parts = DocumentPart.objects.filter(document=self.document).order_by('order')
        
        for part in parts:
            if not part.image:
                continue
            
            # Get image
            try:
                img = PILImage.open(part.image.path)
                img_width, img_height = img.size
                
                # Calculate scaling to fit page
                scale = min(width / img_width, height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Center image
                x = (width - new_width) / 2
                y = (height - new_height) / 2
                
                # Draw image
                self.canvas.drawImage(
                    part.image.path,
                    x, y,
                    width=new_width,
                    height=new_height,
                    preserveAspectRatio=True
                )
                
                self.canvas.showPage()
            except Exception as e:
                # Skip if image can't be loaded
                continue
    
    def _export_image_text_overlay(self, font_size: int):
        """Export PDF with text overlaid on images"""
        width, height = A4
        
        parts = DocumentPart.objects.filter(document=self.document).order_by('order')
        
        for part in parts:
            if not part.image:
                continue
            
            # Draw image
            try:
                img = PILImage.open(part.image.path)
                img_width, img_height = img.size
                
                # Calculate scaling
                scale = min(width / img_width, height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Center image
                x_offset = (width - new_width) / 2
                y_offset = (height - new_height) / 2
                
                # Draw image
                self.canvas.drawImage(
                    part.image.path,
                    x_offset, y_offset,
                    width=new_width,
                    height=new_height,
                    preserveAspectRatio=True
                )
                
                # Overlay text
                self.canvas.setFont(self.font_name, font_size)
                self.canvas.setFillColor(black)
                
                lines = Line.objects.filter(document_part=part).order_by('order')
                
                for line in lines:
                    if not line.baseline:
                        continue
                    
                    # Get transcription
                    try:
                        lt = LineTranscription.objects.get(
                            line=line,
                            transcription=self.transcription
                        )
                        text = lt.content or ""
                    except LineTranscription.DoesNotExist:
                        continue
                    
                    if not text:
                        continue
                    
                    # Parse baseline coordinates
                    coords = self._parse_baseline(line.baseline)
                    if not coords:
                        continue
                    
                    # Scale coordinates
                    x = coords[0][0] * scale + x_offset
                    y = height - (coords[0][1] * scale + y_offset)
                    
                    # Format and draw text
                    formatted_text = self._format_rtl_text(text)
                    self.canvas.drawString(x, y, formatted_text)
                
                self.canvas.showPage()
            except Exception as e:
                continue
    
    def _export_image_text_side_by_side(self, font_size: int, line_spacing: float):
        """Export PDF with image and text side by side"""
        width, height = A4
        margin = 10 * mm
        col_width = (width - 3 * margin) / 2
        
        parts = DocumentPart.objects.filter(document=self.document).order_by('order')
        
        for part in parts:
            # Left side: Image
            if part.image:
                try:
                    img = PILImage.open(part.image.path)
                    img_width, img_height = img.size
                    
                    # Scale to fit left column
                    scale = min(col_width / img_width, (height - 2 * margin) / img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    self.canvas.drawImage(
                        part.image.path,
                        margin,
                        height - margin - new_height,
                        width=new_width,
                        height=new_height,
                        preserveAspectRatio=True
                    )
                except:
                    pass
            
            # Right side: Text
            x = margin * 2 + col_width
            y = height - margin
            
            self.canvas.setFont(self.font_name, font_size)
            line_height = font_size * line_spacing
            
            lines = Line.objects.filter(document_part=part).order_by('order')
            
            for line in lines:
                try:
                    lt = LineTranscription.objects.get(
                        line=line,
                        transcription=self.transcription
                    )
                    text = lt.content or ""
                except LineTranscription.DoesNotExist:
                    continue
                
                if not text:
                    continue
                
                formatted_text = self._format_rtl_text(text)
                
                if y < margin + line_height:
                    break  # Can't fit more on this page
                
                # Draw text
                has_rtl = any('\u0590' <= char <= '\u06FF' for char in text)
                if has_rtl:
                    self.canvas.drawRightString(width - margin, y, formatted_text)
                else:
                    self.canvas.drawString(x, y, formatted_text)
                
                y -= line_height
            
            self.canvas.showPage()
    
    def _parse_baseline(self, baseline_str: str) -> Optional[List[tuple]]:
        """Parse baseline string to coordinates"""
        try:
            coords = []
            pairs = baseline_str.strip().split()
            for i in range(0, len(pairs), 2):
                x = float(pairs[i])
                y = float(pairs[i + 1])
                coords.append((x, y))
            return coords if coords else None
        except:
            return None
