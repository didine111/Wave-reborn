from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import audio
import config
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import json
import subprocess

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    audio.init_audio()
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/channels")
def get_channels():
    return [{"name": ch,
             "volume_stream": audio.VOLUME_STREAM_STATE.get(ch, 100),
             "volume_you": audio.VOLUME_YOU_STATE.get(ch, 100),
             "mute": audio.MUTE_STATE.get(ch, False)} for ch in audio.CHANNELS]

@app.post("/set_volume_stream")
def set_volume_stream(channel: str = Query(...), value: int = Query(...)):
    audio.set_volume_stream(channel, value)
    return {"status": "ok"}

@app.post("/set_volume_you")
def set_volume_you(channel: str = Query(...), value: int = Query(...)):
    audio.set_volume_you(channel, value)
    return {"status": "ok"}

@app.post("/mute")
def mute(channel: str = Query(...)):
    audio.mute_channel(channel)
    return {"status": "ok"}

@app.post("/unmute")
def unmute(channel: str = Query(...)):
    audio.unmute_channel(channel)
    return {"status": "ok"}

@app.get("/applications")
def get_applications():
    """Get list of all applications with their routing info"""
    return audio.get_applications()

@app.post("/route_application")
def route_application(app_index: str = Query(...), channel: str = Query(...)):
    """Route an application to a channel"""
    success = audio.route_application_to_channel(app_index, channel)
    return {"status": "ok" if success else "error"}

@app.websocket("/vu")
async def websocket_vu(websocket: WebSocket):
    """WebSocket endpoint for real-time VU meter data"""
    await websocket.accept()
    try:
        while True:
            levels = audio.get_channel_levels()
            await websocket.send_json(levels)
            await asyncio.sleep(0.05)  # ~20 FPS
    except WebSocketDisconnect:
        pass

# Configuration endpoints
@app.get("/config")
def get_config():
    """Get current configuration"""
    return config.load_config()

@app.post("/config")
def save_config_endpoint(new_config: dict = Body(...)):
    """Save configuration"""
    try:
        config.save_config(new_config)
        return {"status": "ok", "message": "Configuration saved successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/config/reset")
def reset_config():
    """Reset configuration to defaults"""
    try:
        if os.path.exists(config.CONFIG_FILE):
            os.remove(config.CONFIG_FILE)
        new_config = config.load_config()  # Will create default
        return {"status": "ok", "message": "Configuration reset to defaults", "config": new_config}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/config/devices")
def get_audio_devices():
    """Get list of available audio devices"""
    try:
        result = subprocess.run(
            ["pactl", "list", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )

        devices = []
        current_device = {}

        for line in result.stdout.split('\n'):
            if line.startswith('Sink #'):
                if current_device:
                    devices.append(current_device)
                current_device = {}
            elif 'Name:' in line and current_device is not None:
                current_device['name'] = line.split('Name:')[1].strip()
            elif 'Description:' in line and current_device is not None:
                current_device['description'] = line.split('Description:')[1].strip()

        if current_device:
            devices.append(current_device)

        return {"devices": devices}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"devices": [], "error": str(e)}
        )

# фронтенд
frontend_dir = "frontend"
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
