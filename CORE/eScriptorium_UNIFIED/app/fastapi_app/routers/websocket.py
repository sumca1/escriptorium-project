"""
WebSocket Router for Real-Time Image Processing
==============================================

This module provides WebSocket endpoints for real-time image processing with:
- Live progress updates
- Intermediate preview images
- Bidirectional communication
- Connection management

Author: GitHub Copilot
Date: 19 October 2025
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List, Callable, Optional, Any
import asyncio
import logging
import json
import base64
from datetime import datetime
import traceback

from ..services.image_processor import ImageProcessor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.
    
    Features:
    - Multiple client connections
    - Broadcast to all or specific clients
    - Connection lifecycle management
    - Error handling and cleanup
    """
    
    def __init__(self):
        """Initialize connection manager with empty connections list."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        logger.info("ConnectionManager initialized")
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept new WebSocket connection.
        
        Args:
            websocket: WebSocket connection instance
            client_id: Unique identifier for this client
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_message(client_id, {
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Successfully connected to FastAPI image processing service"
        })
    
    def disconnect(self, client_id: str):
        """
        Remove client from active connections.
        
        Args:
            client_id: Client to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
        
        # Cancel any ongoing processing tasks
        if client_id in self.processing_tasks:
            task = self.processing_tasks[client_id]
            if not task.done():
                task.cancel()
            del self.processing_tasks[client_id]
    
    async def send_message(self, client_id: str, message: Dict):
        """
        Send message to specific client.
        
        Args:
            client_id: Target client
            message: Message dictionary to send
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict, exclude: Optional[List[str]] = None):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
            exclude: List of client IDs to exclude from broadcast
        """
        exclude = exclude or []
        disconnected = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def get_connection_count(self) -> int:
        """Return number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


class ProgressCallback:
    """
    Callback class for progress updates during image processing.
    
    Sends progress messages via WebSocket as processing happens.
    """
    
    def __init__(self, client_id: str, manager: ConnectionManager):
        """
        Initialize progress callback.
        
        Args:
            client_id: Client to send updates to
            manager: Connection manager instance
        """
        self.client_id = client_id
        self.manager = manager
        self.current_step = 0
        self.total_steps = 4  # denoise, deskew, enhance, binarize
    
    async def update(self, step: str, progress: int, message: str, preview: Optional[bytes] = None):
        """
        Send progress update to client.
        
        Args:
            step: Current processing step name
            progress: Progress percentage (0-100)
            message: Status message
            preview: Optional preview image bytes
        """
        update_data = {
            "type": "progress",
            "step": step,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add preview if provided
        if preview:
            try:
                preview_base64 = base64.b64encode(preview).decode('utf-8')
                update_data["preview"] = preview_base64
                update_data["preview_size"] = len(preview)
            except Exception as e:
                logger.error(f"Error encoding preview: {e}")
        
        await self.manager.send_message(self.client_id, update_data)
    
    async def step_complete(self, step: str, duration: float):
        """
        Notify client that a processing step is complete.
        
        Args:
            step: Completed step name
            duration: Time taken in seconds
        """
        self.current_step += 1
        percent = int((self.current_step / self.total_steps) * 100)
        
        await self.manager.send_message(self.client_id, {
            "type": "step_complete",
            "step": step,
            "duration": round(duration, 3),
            "progress": percent,
            "timestamp": datetime.now().isoformat()
        })


async def process_image_with_progress(
    image_data: bytes,
    action: str,
    params: Dict[str, Any],
    callback: ProgressCallback
) -> Dict[str, Any]:
    """
    Process image with real-time progress updates.
    
    Args:
        image_data: Input image bytes
        action: Processing action (binarize, denoise, etc.)
        params: Processing parameters
        callback: Progress callback instance
    
    Returns:
        Processing result dictionary
    """
    import time
    
    try:
        # Convert bytes to image
        await callback.update("load", 5, "Loading image...")
        img = ImageProcessor.bytes_to_image(image_data)
        
        if action == "binarize":
            method = params.get("method", "otsu")
            threshold = params.get("threshold", 127)
            
            await callback.update("binarize", 30, f"Binarizing with {method} method...")
            start = time.time()
            
            result_img = ImageProcessor.binarize(img, method=method, threshold=threshold)
            
            duration = time.time() - start
            await callback.step_complete("binarize", duration)
            
            result_bytes = ImageProcessor.image_to_bytes(result_img, format='png')
            return {
                "status": "success",
                "action": "binarize",
                "method": method,
                "image": base64.b64encode(result_bytes).decode('utf-8'),
                "size": len(result_bytes)
            }
        
        elif action == "denoise":
            strength = params.get("strength", 10)
            
            await callback.update("denoise", 30, f"Denoising with strength {strength}...")
            start = time.time()
            
            result_img = ImageProcessor.denoise(img, strength=strength)
            
            duration = time.time() - start
            await callback.step_complete("denoise", duration)
            
            result_bytes = ImageProcessor.image_to_bytes(result_img, format='png')
            return {
                "status": "success",
                "action": "denoise",
                "strength": strength,
                "image": base64.b64encode(result_bytes).decode('utf-8'),
                "size": len(result_bytes)
            }
        
        elif action == "deskew":
            await callback.update("deskew", 30, "Detecting rotation angle...")
            start = time.time()
            
            result_img, angle = ImageProcessor.deskew(img)
            
            duration = time.time() - start
            await callback.step_complete("deskew", duration)
            
            result_bytes = ImageProcessor.image_to_bytes(result_img, format='png')
            return {
                "status": "success",
                "action": "deskew",
                "angle": angle,
                "image": base64.b64encode(result_bytes).decode('utf-8'),
                "size": len(result_bytes)
            }
        
        elif action == "enhance":
            clip_limit = params.get("clip_limit", 2.0)
            
            await callback.update("enhance", 30, f"Enhancing contrast (CLAHE)...")
            start = time.time()
            
            result_img = ImageProcessor.enhance_contrast(img, clip_limit=clip_limit)
            
            duration = time.time() - start
            await callback.step_complete("enhance", duration)
            
            result_bytes = ImageProcessor.image_to_bytes(result_img, format='png')
            return {
                "status": "success",
                "action": "enhance",
                "clip_limit": clip_limit,
                "image": base64.b64encode(result_bytes).decode('utf-8'),
                "size": len(result_bytes)
            }
        
        elif action == "auto_process":
            await callback.update("auto_process", 10, "Starting auto-process pipeline...")
            
            # Step 1: Denoise
            await callback.update("denoise", 20, "Step 1/4: Removing noise...")
            start = time.time()
            img = ImageProcessor.denoise(img, strength=10)
            duration = time.time() - start
            await callback.step_complete("denoise", duration)
            
            # Send preview
            preview_bytes = ImageProcessor.image_to_bytes(img, format='jpeg', quality=70)
            await callback.update("denoise", 25, "Noise removed", preview=preview_bytes)
            
            # Step 2: Deskew
            await callback.update("deskew", 40, "Step 2/4: Correcting rotation...")
            start = time.time()
            img, angle = ImageProcessor.deskew(img)
            duration = time.time() - start
            await callback.step_complete("deskew", duration)
            
            # Send preview
            preview_bytes = ImageProcessor.image_to_bytes(img, format='jpeg', quality=70)
            await callback.update("deskew", 50, f"Rotation corrected ({angle:.2f}°)", preview=preview_bytes)
            
            # Step 3: Enhance
            await callback.update("enhance", 60, "Step 3/4: Enhancing contrast...")
            start = time.time()
            img = ImageProcessor.enhance_contrast(img, clip_limit=2.0)
            duration = time.time() - start
            await callback.step_complete("enhance", duration)
            
            # Send preview
            preview_bytes = ImageProcessor.image_to_bytes(img, format='jpeg', quality=70)
            await callback.update("enhance", 75, "Contrast enhanced", preview=preview_bytes)
            
            # Step 4: Binarize
            await callback.update("binarize", 80, "Step 4/4: Binarizing...")
            start = time.time()
            img = ImageProcessor.binarize(img, method='otsu')
            duration = time.time() - start
            await callback.step_complete("binarize", duration)
            
            await callback.update("complete", 100, "Processing complete!")
            
            result_bytes = ImageProcessor.image_to_bytes(img, format='png')
            return {
                "status": "success",
                "action": "auto_process",
                "angle": angle,
                "steps": 4,
                "image": base64.b64encode(result_bytes).decode('utf-8'),
                "size": len(result_bytes)
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        logger.error(traceback.format_exc())
        raise


@router.websocket("/process")
async def websocket_process_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time image processing.
    
    Protocol:
    --------
    Client sends:
    {
        "action": "binarize" | "denoise" | "deskew" | "enhance" | "auto_process",
        "image": "base64_encoded_image",
        "params": {
            // action-specific parameters
        }
    }
    
    Server responds with:
    - progress updates: {"type": "progress", "step": "...", "progress": 0-100, ...}
    - step completion: {"type": "step_complete", "step": "...", "duration": ...}
    - final result: {"type": "result", "status": "success", "image": "...", ...}
    - errors: {"type": "error", "message": "..."}
    
    Example:
    --------
    ```javascript
    const ws = new WebSocket('ws://localhost:8001/ws/process');
    
    ws.onopen = () => {
        ws.send(JSON.stringify({
            action: 'auto_process',
            image: base64Image,
            params: {}
        }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'progress') {
            updateProgressBar(data.progress);
            if (data.preview) {
                updatePreview(data.preview);
            }
        }
    };
    ```
    """
    client_id = f"client_{datetime.now().timestamp()}"
    
    try:
        # Accept connection
        await manager.connect(websocket, client_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received from {client_id}: {message.get('action', 'unknown')}")
            
            # Extract processing parameters
            action = message.get("action")
            image_base64 = message.get("image")
            params = message.get("params", {})
            
            if not action or not image_base64:
                await manager.send_message(client_id, {
                    "type": "error",
                    "message": "Missing 'action' or 'image' in request"
                })
                continue
            
            try:
                # Decode image
                image_data = base64.b64decode(image_base64)
                
                # Create progress callback
                callback = ProgressCallback(client_id, manager)
                
                # Process image
                result = await process_image_with_progress(
                    image_data,
                    action,
                    params,
                    callback
                )
                
                # Send final result
                await manager.send_message(client_id, {
                    "type": "result",
                    **result
                })
                
            except Exception as e:
                logger.error(f"Processing error for {client_id}: {e}")
                logger.error(traceback.format_exc())
                
                await manager.send_message(client_id, {
                    "type": "error",
                    "message": str(e),
                    "traceback": traceback.format_exc()
                })
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
        manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        logger.error(traceback.format_exc())
        manager.disconnect(client_id)


@router.websocket("/monitor")
async def websocket_monitor_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for monitoring server status.
    
    Sends periodic updates about:
    - Active connections count
    - Server health
    - Processing statistics
    
    Example:
    --------
    ```javascript
    const ws = new WebSocket('ws://localhost:8001/ws/monitor');
    ws.onmessage = (event) => {
        const status = JSON.parse(event.data);
        console.log('Active connections:', status.connections);
    };
    ```
    """
    client_id = f"monitor_{datetime.now().timestamp()}"
    
    try:
        await manager.connect(websocket, client_id)
        
        while True:
            # Send status update every 5 seconds
            await manager.send_message(client_id, {
                "type": "status",
                "connections": manager.get_connection_count(),
                "timestamp": datetime.now().isoformat(),
                "status": "healthy"
            })
            
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        logger.info(f"Monitor {client_id} disconnected")
        manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"Monitor error for {client_id}: {e}")
        manager.disconnect(client_id)
