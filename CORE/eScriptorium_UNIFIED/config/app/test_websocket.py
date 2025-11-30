import asyncio
import websockets
import json
import base64
import sys

async def test_websocket():
    uri = "ws://localhost:8001/ws/process"
    
    # Read test image
    try:
        with open('demo_input.jpg', 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
    except FileNotFoundError:
        print("❌ Test image not found. Creating one...")
        import numpy as np
        import cv2
        
        img = np.ones((600, 800, 3), dtype=np.uint8) * 240
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        for i in range(10):
            y = 60 + i * 50
            cv2.line(img, (50, y), (700, y), (0, 0, 0), 3)
        
        cv2.imwrite('demo_input.jpg', img)
        
        with open('demo_input.jpg', 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print("✅ Test image created")
    
    print(f"🔌 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send processing request
            message = {
                "action": "auto_process",
                "image": image_base64,
                "params": {}
            }
            
            print("🚀 Sending processing request...")
            await websocket.send(json.dumps(message))
            
            # Receive messages
            print("📨 Receiving updates...")
            print()
            
            result_image = None
            
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    msg_type = data.get('type')
                    
                    if msg_type == 'connected':
                        print(f"✅ {data.get('message')}")
                    
                    elif msg_type == 'progress':
                        progress = data.get('progress', 0)
                        message_text = data.get('message', '')
                        step = data.get('step', '')
                        print(f"⏳ [{step}] {progress}% - {message_text}")
                        
                        if data.get('preview'):
                            print(f"   📸 Preview received ({len(data['preview'])} bytes)")
                    
                    elif msg_type == 'step_complete':
                        step = data.get('step')
                        duration = data.get('duration')
                        print(f"✅ Step '{step}' completed in {duration}s")
                    
                    elif msg_type == 'result':
                        print()
                        print("=" * 60)
                        print("🎉 Processing Complete!")
                        print("=" * 60)
                        print(f"Action: {data.get('action')}")
                        print(f"Status: {data.get('status')}")
                        if 'angle' in data:
                            print(f"Skew angle: {data['angle']:.2f}°")
                        print(f"Result size: {data.get('size', 0)} bytes")
                        
                        # Save result
                        result_image = data.get('image')
                        if result_image:
                            result_bytes = base64.b64decode(result_image)
                            with open('websocket_result.png', 'wb') as f:
                                f.write(result_bytes)
                            print(f"💾 Saved: websocket_result.png ({len(result_bytes)} bytes)")
                        
                        break
                    
                    elif msg_type == 'error':
                        print(f"❌ Error: {data.get('message')}")
                        break
                
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 Connection closed")
                    break
            
            print()
            print("✅ WebSocket test complete!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_websocket())
    sys.exit(exit_code)
