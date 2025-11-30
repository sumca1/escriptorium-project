"""
🚀 Surya OCR Engine Integration for eScriptorium
================================================

Wrapper for Surya OCR that integrates with eScriptorium.
Maintains all the power of Surya API while providing a unified interface.

Key Features:
  ✓ Hebrew/Arabic/English + 90+ languages
  ✓ Batch processing support
  ✓ Confidence scores
  ✓ Line-by-line text with bounding boxes
  ✓ GPU acceleration support
  ✓ Caching of loaded models
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import torch
from PIL import Image

# Import Surya - keeping its powerful API intact
try:
    from surya import models as surya_models
    from surya.recognition.schema import OCRResult, TextLine
except ImportError:
    raise ImportError(
        "Surya is not installed. Install with: pip install surya-ocr"
    )

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes for Results
# ============================================================================

@dataclass
class TextLineResult:
    """Result for a single line of text."""
    text: str
    confidence: float  # 0.0 - 1.0
    polygon: List[List[int]]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    bbox_valid: bool
    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None
    
    def __post_init__(self):
        """Calculate bbox coordinates from polygon."""
        if self.polygon and self.bbox_valid:
            xs = [p[0] for p in self.polygon]
            ys = [p[1] for p in self.polygon]
            self.x1 = min(xs)
            self.y1 = min(ys)
            self.x2 = max(xs)
            self.y2 = max(ys)


@dataclass
class PageOCRResult:
    """Result for an entire page."""
    image_path: str
    lines: List[TextLineResult]
    languages: List[str]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    page_width: int = None
    page_height: int = None


# ============================================================================
# Main Engine Class
# ============================================================================

class SuryaOCREngine:
    """
    Main Surya OCR Engine for eScriptorium.
    
    Features:
      • Preserves Surya's powerful API
      • Caches loaded models
      • Supports batch processing
      • Returns structured results
      • Hebrew/Arabic friendly (auto-sorts RTL)
    """
    
    # Class-level cache for models
    _predictors_cache = None
    _device_cache = None
    _dtype_cache = None
    
    def __init__(
        self,
        device: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
        batch_size_recognition: int = None,
        batch_size_detection: int = None,
        sort_lines: bool = True,
        languages: Optional[List[str]] = None
    ):
        """
        Initialize the Surya OCR Engine.
        
        Args:
            device: 'cuda', 'cpu', 'mps' (default: auto-detect)
            dtype: torch.float32, torch.float16 (default: float32)
            batch_size_recognition: Batch size for recognition (default: auto)
            batch_size_detection: Batch size for detection (default: auto)
            sort_lines: Sort lines for proper reading order (important for RTL)
            languages: List of language codes to support (default: ['he', 'en', 'ar'])
        """
        self.device = device or self._detect_device()
        self.dtype = dtype or torch.float32
        self.sort_lines = sort_lines
        self.languages = languages or ['he', 'en', 'ar']
        
        # Auto-tune batch sizes based on device
        if batch_size_recognition is None:
            batch_size_recognition = 256 if self.device == 'cuda' else 32
        if batch_size_detection is None:
            batch_size_detection = 64 if self.device == 'cuda' else 16
            
        self.batch_size_recognition = batch_size_recognition
        self.batch_size_detection = batch_size_detection
        
        logger.info(
            f"Surya OCR Engine initialized: "
            f"device={self.device}, "
            f"batch_size_recognition={self.batch_size_recognition}, "
            f"sort_lines={self.sort_lines}"
        )
        
        # Load models (with caching)
        self.predictors = self._load_predictors()
    
    @staticmethod
    def _detect_device() -> str:
        """Auto-detect the best device."""
        if torch.cuda.is_available():
            return 'cuda'
        elif torch.backends.mps.is_available():
            return 'mps'
        return 'cpu'
    
    @classmethod
    def _load_predictors(cls, device=None, dtype=None):
        """
        Load Surya predictors with caching.
        
        Once loaded, models stay in memory for fast inference.
        """
        if device is None:
            device = cls._detect_device()
        if dtype is None:
            dtype = torch.float32
            
        # Return cached predictors if device/dtype match
        if (cls._predictors_cache is not None and 
            cls._device_cache == device and 
            cls._dtype_cache == dtype):
            logger.info("Using cached Surya predictors")
            return cls._predictors_cache
        
        # Load fresh
        logger.info(f"Loading Surya models on {device}...")
        start = datetime.now()
        
        try:
            predictors = surya_models.load_predictors(device=device, dtype=dtype)
        except Exception as e:
            # Check if it's NetFree block
            if "418" in str(e) or "NetFree" in str(e):
                raise RuntimeError(
                    "NetFree firewall is blocking model downloads from "
                    "models.datalab.to. Please request approval from your "
                    "administrator for https://models.datalab.to"
                ) from e
            raise
        
        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"✅ Models loaded in {elapsed:.1f}s")
        
        # Cache the predictors
        cls._predictors_cache = predictors
        cls._device_cache = device
        cls._dtype_cache = dtype
        
        return predictors
    
    def _predictors(self):
        """Get cached predictors."""
        if SuryaOCREngine._predictors_cache is None:
            raise RuntimeError("Models not loaded. Call load_predictors() first.")
        return SuryaOCREngine._predictors_cache
    
    # ========================================================================
    # Main API Methods (keeping Surya's power!)
    # ========================================================================
    
    def recognize_page(
        self,
        image_path: str,
        save_debug_info: bool = False
    ) -> PageOCRResult:
        """
        Recognize text in a single page image.
        
        Args:
            image_path: Path to image file
            save_debug_info: Save debug polygon visualization
            
        Returns:
            PageOCRResult with all lines and metadata
        """
        start = datetime.now()
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Run OCR through Surya's powerful API
            results = self.recognize_pages(
                image_paths=[image_path],
                images=[image]
            )
            
            if results and results[0].success:
                result = results[0]
                result.processing_time = (datetime.now() - start).total_seconds()
                return result
            else:
                return PageOCRResult(
                    image_path=str(image_path),
                    lines=[],
                    languages=[],
                    processing_time=(datetime.now() - start).total_seconds(),
                    success=False,
                    error_message="Recognition failed"
                )
                
        except Exception as e:
            logger.error(f"Error recognizing {image_path}: {e}", exc_info=True)
            return PageOCRResult(
                image_path=str(image_path),
                lines=[],
                languages=[],
                processing_time=(datetime.now() - start).total_seconds(),
                success=False,
                error_message=str(e)
            )
    
    def recognize_pages(
        self,
        image_paths: List[str],
        images: List[Image.Image] = None
    ) -> List[PageOCRResult]:
        """
        Recognize text in multiple page images (batch processing).
        
        This is where Surya's batch power shines!
        
        Args:
            image_paths: List of image file paths
            images: Pre-loaded PIL images (optional, faster)
            
        Returns:
            List of PageOCRResult
        """
        if not image_paths:
            return []
        
        # Load images if not provided
        if images is None:
            images = []
            for path in image_paths:
                try:
                    images.append(Image.open(path))
                except Exception as e:
                    logger.error(f"Failed to load image {path}: {e}")
                    images.append(None)
        
        # Validate
        if len(images) != len(image_paths):
            raise ValueError("Mismatch between image_paths and images")
        
        start = datetime.now()
        logger.info(f"Processing batch of {len(images)} pages...")
        
        try:
            # Call Surya's powerful batch API
            predictors = self._predictors()
            recognizer = predictors['recognition']
            detector = predictors['detection']
            
            # This is the magic - Surya's batch processing
            surya_results = recognizer(
                images,
                det_predictor=detector,
                sort_lines=self.sort_lines,  # Important for Hebrew/Arabic
                recognition_batch_size=self.batch_size_recognition,
                detection_batch_size=self.batch_size_detection
            )
            
            # Convert Surya results to our format
            page_results = []
            for img_path, surya_result, image in zip(image_paths, surya_results, images):
                result = self._convert_surya_result(
                    img_path, surya_result, image
                )
                page_results.append(result)
            
            elapsed = (datetime.now() - start).total_seconds()
            logger.info(
                f"✅ Batch processing complete: "
                f"{len(page_results)} pages in {elapsed:.1f}s "
                f"({elapsed/len(page_results):.2f}s per page)"
            )
            
            return page_results
            
        except Exception as e:
            logger.error(f"Error in batch recognition: {e}", exc_info=True)
            # Return error results for all pages
            return [
                PageOCRResult(
                    image_path=str(path),
                    lines=[],
                    languages=[],
                    processing_time=0,
                    success=False,
                    error_message=str(e)
                )
                for path in image_paths
            ]
    
    def _convert_surya_result(
        self,
        image_path: str,
        surya_result: OCRResult,
        image: Image.Image
    ) -> PageOCRResult:
        """Convert Surya's OCRResult to our PageOCRResult format."""
        
        lines = []
        for text_line in surya_result.text_lines:
            line_result = TextLineResult(
                text=text_line.text,
                confidence=float(text_line.confidence),
                polygon=text_line.polygon,
                bbox_valid=text_line.bbox_valid
            )
            lines.append(line_result)
        
        return PageOCRResult(
            image_path=str(image_path),
            lines=lines,
            languages=surya_result.languages,
            processing_time=0,  # Will be set by caller
            success=True,
            page_width=image.width if image else None,
            page_height=image.height if image else None
        )
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status and diagnostics."""
        return {
            'device': self.device,
            'cuda_available': torch.cuda.is_available(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            'dtype': str(self.dtype),
            'batch_size_recognition': self.batch_size_recognition,
            'batch_size_detection': self.batch_size_detection,
            'sort_lines': self.sort_lines,
            'languages': self.languages,
            'models_loaded': SuryaOCREngine._predictors_cache is not None
        }
    
    def clear_cache(self):
        """Clear cached models (frees memory)."""
        logger.info("Clearing Surya model cache...")
        SuryaOCREngine._predictors_cache = None
        SuryaOCREngine._device_cache = None
        SuryaOCREngine._dtype_cache = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @property
    def recognizer(self):
        """Get the RecognitionPredictor directly (for advanced usage)."""
        return self._predictors()['recognition']
    
    @property
    def detector(self):
        """Get the DetectionPredictor directly (for advanced usage)."""
        return self._predictors()['detection']
    
    @property
    def layout_predictor(self):
        """Get the LayoutPredictor directly (for advanced usage)."""
        return self._predictors()['layout']


# ============================================================================
# Singleton Instance for Global Access
# ============================================================================

_engine_instance = None

def get_ocr_engine() -> SuryaOCREngine:
    """Get or create the global Surya OCR engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SuryaOCREngine()
    return _engine_instance


def set_ocr_engine(engine: SuryaOCREngine) -> None:
    """Set a custom OCR engine instance."""
    global _engine_instance
    _engine_instance = engine


# ============================================================================
# Helper Functions
# ============================================================================

def test_engine() -> bool:
    """Test if Surya engine works."""
    try:
        logger.info("Testing Surya OCR engine...")
        engine = SuryaOCREngine()
        status = engine.get_status()
        logger.info(f"Engine status: {status}")
        logger.info("✅ Engine test passed!")
        return True
    except Exception as e:
        logger.error(f"❌ Engine test failed: {e}", exc_info=True)
        return False
