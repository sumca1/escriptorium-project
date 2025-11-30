"""
Image Processing REST API Endpoints
====================================

RESTful API for image processing operations.

Endpoints:
- POST /api/images/binarize      - Convert to black & white
- POST /api/images/denoise       - Remove noise
- POST /api/images/deskew        - Fix rotation
- POST /api/images/enhance       - Enhance contrast
- POST /api/images/auto-process  - Full automatic processing

All endpoints accept image files and return processed images.

Created: 2025-10-19
Author: BiblIA Team
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from typing import Optional
import logging

from ..services.image_processor import ImageProcessor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# ==========================================
# BINARIZATION ENDPOINT
# ==========================================

@router.post(
    "/binarize",
    summary="Binarize Image",
    description="Convert image to binary (black & white). Supports Otsu, Adaptive, and Manual methods.",
    response_description="Binary image (PNG format)",
    tags=["Processing"]
)
async def binarize_image(
    file: UploadFile = File(..., description="Image file to process"),
    method: str = Query(
        "otsu",
        description="Binarization method",
        enum=["otsu", "adaptive", "manual"]
    ),
    threshold: int = Query(
        127,
        ge=0,
        le=255,
        description="Threshold value (only for 'manual' method)"
    )
):
    """
    Convert image to binary (black & white).
    
    **Methods:**
    - `otsu`: Automatic threshold (best for most manuscripts)
    - `adaptive`: Adaptive threshold (good for uneven lighting)
    - `manual`: Manual threshold (use 'threshold' parameter)
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/binarize?method=otsu" \
         -F "file=@manuscript.jpg" \
         --output binary.png
    ```
    """
    try:
        logger.info(f"Binarization request: method={method}, threshold={threshold}")
        
        # Read image file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to image
        img = ImageProcessor.bytes_to_image(contents)
        
        # Validate
        if not ImageProcessor.validate_image(img):
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Process
        binary = ImageProcessor.binarize(img, method=method, threshold=threshold)
        
        # Convert back to bytes
        result_bytes = ImageProcessor.image_to_bytes(binary, format='PNG')
        
        logger.info(f"Binarization completed: size={len(result_bytes)} bytes")
        
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "X-Processing-Method": method,
                "X-Original-Filename": file.filename,
                "X-Processing-Status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Binarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# DENOISING ENDPOINT
# ==========================================

@router.post(
    "/denoise",
    summary="Denoise Image",
    description="Remove noise from image using Non-Local Means Denoising.",
    response_description="Denoised image (PNG format)",
    tags=["Processing"]
)
async def denoise_image(
    file: UploadFile = File(..., description="Image file to process"),
    strength: int = Query(
        10,
        ge=1,
        le=30,
        description="Denoising strength (higher = more smoothing)"
    )
):
    """
    Remove noise from image.
    
    Uses Non-Local Means Denoising algorithm for best results.
    
    **Parameters:**
    - `strength`: 1-30 (default: 10)
      - 1-5: Light denoising
      - 6-15: Medium denoising (recommended)
      - 16-30: Heavy denoising
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/denoise?strength=15" \
         -F "file=@noisy.jpg" \
         --output clean.png
    ```
    """
    try:
        logger.info(f"Denoising request: strength={strength}")
        
        # Read image file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to image
        img = ImageProcessor.bytes_to_image(contents)
        
        # Validate
        if not ImageProcessor.validate_image(img):
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Process
        denoised = ImageProcessor.denoise(img, strength=strength)
        
        # Convert back to bytes
        result_bytes = ImageProcessor.image_to_bytes(denoised, format='PNG')
        
        logger.info(f"Denoising completed: size={len(result_bytes)} bytes")
        
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "X-Denoising-Strength": str(strength),
                "X-Original-Filename": file.filename,
                "X-Processing-Status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Denoising failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# DESKEWING ENDPOINT
# ==========================================

@router.post(
    "/deskew",
    summary="Deskew Image",
    description="Automatically correct image rotation (deskew).",
    response_description="Deskewed image (PNG format)",
    tags=["Processing"]
)
async def deskew_image(
    file: UploadFile = File(..., description="Image file to process"),
    auto_crop: bool = Query(
        False,
        description="Crop black borders after rotation"
    )
):
    """
    Automatically correct image rotation.
    
    Detects text orientation and rotates image to be straight.
    
    **Returns:**
    - Image: Deskewed image (PNG)
    - Header `X-Skew-Angle`: Rotation angle applied (degrees)
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/deskew" \
         -F "file=@rotated.jpg" \
         --output straight.png
    ```
    """
    try:
        logger.info(f"Deskewing request: auto_crop={auto_crop}")
        
        # Read image file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to image
        img = ImageProcessor.bytes_to_image(contents)
        
        # Validate
        if not ImageProcessor.validate_image(img):
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Process
        deskewed, angle = ImageProcessor.deskew(img, auto_crop=auto_crop)
        
        # Convert back to bytes
        result_bytes = ImageProcessor.image_to_bytes(deskewed, format='PNG')
        
        logger.info(f"Deskewing completed: angle={angle:.2f}°, size={len(result_bytes)} bytes")
        
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "X-Skew-Angle": f"{angle:.2f}",
                "X-Original-Filename": file.filename,
                "X-Processing-Status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deskewing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# CONTRAST ENHANCEMENT ENDPOINT
# ==========================================

@router.post(
    "/enhance",
    summary="Enhance Contrast",
    description="Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).",
    response_description="Enhanced image (PNG format)",
    tags=["Processing"]
)
async def enhance_image(
    file: UploadFile = File(..., description="Image file to process"),
    clip_limit: float = Query(
        2.0,
        ge=1.0,
        le=4.0,
        description="Contrast clipping limit (higher = more contrast)"
    ),
    tile_size: int = Query(
        8,
        description="Tile size for histogram equalization",
        enum=[8, 16]
    )
):
    """
    Enhance image contrast using CLAHE.
    
    CLAHE (Contrast Limited Adaptive Histogram Equalization) is better
    than simple contrast adjustment for manuscripts.
    
    **Parameters:**
    - `clip_limit`: 1.0-4.0 (default: 2.0)
      - Lower = subtle enhancement
      - Higher = dramatic enhancement
    - `tile_size`: 8 or 16 (default: 8)
      - Smaller = more local adaptation
      - Larger = smoother result
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/enhance?clip_limit=3.0" \
         -F "file=@faded.jpg" \
         --output enhanced.png
    ```
    """
    try:
        logger.info(f"Enhancement request: clip_limit={clip_limit}, tile_size={tile_size}")
        
        # Read image file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to image
        img = ImageProcessor.bytes_to_image(contents)
        
        # Validate
        if not ImageProcessor.validate_image(img):
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Process
        enhanced = ImageProcessor.enhance_contrast(
            img, 
            clip_limit=clip_limit, 
            tile_size=tile_size
        )
        
        # Convert back to bytes
        result_bytes = ImageProcessor.image_to_bytes(enhanced, format='PNG')
        
        logger.info(f"Enhancement completed: size={len(result_bytes)} bytes")
        
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "X-Clip-Limit": str(clip_limit),
                "X-Tile-Size": str(tile_size),
                "X-Original-Filename": file.filename,
                "X-Processing-Status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# AUTO PROCESSING ENDPOINT
# ==========================================

@router.post(
    "/auto-process",
    summary="Auto Process Manuscript",
    description="Full automatic manuscript processing pipeline (denoise → deskew → enhance → binarize).",
    tags=["Processing"]
)
async def auto_process_image(
    file: UploadFile = File(..., description="Image file to process"),
    return_json: bool = Query(
        False,
        description="Return JSON with metadata instead of image"
    ),
    output_format: str = Query(
        "png",
        description="Output image format",
        enum=["png", "jpeg", "webp"]
    )
):
    """
    Full automatic manuscript processing.
    
    **Processing Pipeline:**
    1. Denoise (strength=10)
    2. Deskew (auto rotation)
    3. Enhance contrast (CLAHE)
    4. Binarize (Otsu)
    
    **Returns:**
    - If `return_json=false`: Binary image (default)
    - If `return_json=true`: JSON with metadata + base64 image
    
    **Example 1 - Get image:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/auto-process" \
         -F "file=@manuscript.jpg" \
         --output processed.png
    ```
    
    **Example 2 - Get JSON:**
    ```bash
    curl -X POST "http://localhost:8001/api/images/auto-process?return_json=true" \
         -F "file=@manuscript.jpg"
    ```
    """
    try:
        logger.info(f"Auto processing request: return_json={return_json}, format={output_format}")
        
        # Read image file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Convert to image
        img = ImageProcessor.bytes_to_image(contents)
        
        # Validate
        if not ImageProcessor.validate_image(img):
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Get image info
        img_info = ImageProcessor.get_image_info(img)
        
        # Process
        result = ImageProcessor.auto_process_manuscript(
            img, 
            return_intermediate=return_json
        )
        
        # Convert final image to bytes
        final_bytes = ImageProcessor.image_to_bytes(
            result['final'], 
            format=output_format.upper()
        )
        
        logger.info(f"Auto processing completed: angle={result['skew_angle']:.2f}°, size={len(final_bytes)} bytes")
        
        # Return JSON or image
        if return_json:
            import base64
            
            response_data = {
                "status": "success",
                "original_filename": file.filename,
                "original_size": {
                    "width": img_info['width'],
                    "height": img_info['height'],
                    "channels": img_info['channels']
                },
                "processing": {
                    "skew_angle": result['skew_angle'],
                    "steps_completed": len(result['steps']) if result['steps'] else 4
                },
                "output": {
                    "format": output_format.upper(),
                    "size_bytes": len(final_bytes),
                    "image_base64": base64.b64encode(final_bytes).decode('utf-8')
                }
            }
            
            return JSONResponse(content=response_data)
        
        else:
            return Response(
                content=final_bytes,
                media_type=f"image/{output_format}",
                headers={
                    "X-Skew-Angle": f"{result['skew_angle']:.2f}",
                    "X-Original-Filename": file.filename,
                    "X-Processing-Steps": "4",
                    "X-Processing-Status": "success"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# INFO ENDPOINT
# ==========================================

@router.get(
    "/info",
    summary="Get Image Info",
    description="Get information about supported formats and capabilities.",
    tags=["Info"]
)
async def get_processing_info():
    """
    Get API information and capabilities.
    
    Returns supported formats, methods, and parameter ranges.
    """
    return {
        "service": "Image Processing API",
        "version": "1.0.0",
        "endpoints": {
            "binarize": {
                "path": "/api/images/binarize",
                "methods": ["otsu", "adaptive", "manual"],
                "parameters": {
                    "method": "otsu|adaptive|manual",
                    "threshold": "0-255 (manual only)"
                }
            },
            "denoise": {
                "path": "/api/images/denoise",
                "parameters": {
                    "strength": "1-30 (default: 10)"
                }
            },
            "deskew": {
                "path": "/api/images/deskew",
                "parameters": {
                    "auto_crop": "true|false"
                }
            },
            "enhance": {
                "path": "/api/images/enhance",
                "parameters": {
                    "clip_limit": "1.0-4.0 (default: 2.0)",
                    "tile_size": "8|16 (default: 8)"
                }
            },
            "auto_process": {
                "path": "/api/images/auto-process",
                "pipeline": ["denoise", "deskew", "enhance", "binarize"],
                "parameters": {
                    "return_json": "true|false",
                    "output_format": "png|jpeg|webp"
                }
            }
        },
        "supported_formats": {
            "input": ["JPEG", "PNG", "TIFF", "BMP", "WEBP"],
            "output": ["PNG", "JPEG", "WEBP"]
        },
        "performance": {
            "binarize": "~50ms",
            "denoise": "~200ms",
            "deskew": "~100ms",
            "enhance": "~80ms",
            "auto_process": "~430ms"
        }
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@router.get(
    "/health",
    summary="Health Check",
    description="Check if image processing service is operational.",
    tags=["Info"]
)
async def health_check():
    """Check service health."""
    return {
        "status": "healthy",
        "service": "image_processing",
        "opencv": "available",
        "numpy": "available"
    }
