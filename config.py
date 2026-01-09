"""
WaveReborn Configuration File
Centralized configuration for all hardcoded values
"""

import os
import json
import subprocess

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Network configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 8080
BACKEND_HOST = "127.0.0.1"

# Audio configuration
DEFAULT_CHANNELS = ["Music", "Game", "Voice", "System"]
DEFAULT_LATENCY_MS = 20

# Audio device configuration
CONFIG_FILE = os.path.join(BASE_DIR, "wave_config.json")


def get_default_audio_device():
    """Auto-detect the default PulseAudio output device"""
    try:
        result = subprocess.run(
            ["pactl", "get-default-sink"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try to find any USB audio device
    try:
        result = subprocess.run(
            ["pactl", "list", "short", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.strip().split('\n'):
            if line and 'usb' in line.lower():
                parts = line.split('\t')
                if len(parts) >= 2:
                    return parts[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Ultimate fallback
    return "alsa_output.usb-Maono_ProStudio_2x2_Lite-analog-stereo"


def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")

    # Create default config
    default_device = get_default_audio_device()
    config = {
        "audio": {
            "output_device": default_device,
            "channels": DEFAULT_CHANNELS,
            "latency_ms": DEFAULT_LATENCY_MS
        },
        "network": {
            "backend_port": BACKEND_PORT,
            "frontend_port": FRONTEND_PORT,
            "backend_host": BACKEND_HOST
        }
    }

    save_config(config)
    return config


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, indent=2, fp=f)
    except IOError as e:
        print(f"Warning: Could not save config file: {e}")


def get_audio_output_device():
    """Get the configured audio output device"""
    config = load_config()
    return config.get("audio", {}).get("output_device", get_default_audio_device())


def get_channels():
    """Get the configured channels"""
    config = load_config()
    return config.get("audio", {}).get("channels", DEFAULT_CHANNELS)


def get_latency():
    """Get the configured latency in milliseconds"""
    config = load_config()
    return config.get("audio", {}).get("latency_ms", DEFAULT_LATENCY_MS)


def get_backend_port():
    """Get the configured backend port"""
    config = load_config()
    return config.get("network", {}).get("backend_port", BACKEND_PORT)


def get_frontend_port():
    """Get the configured frontend port"""
    config = load_config()
    return config.get("network", {}).get("frontend_port", FRONTEND_PORT)


def get_backend_host():
    """Get the configured backend host"""
    config = load_config()
    return config.get("network", {}).get("backend_host", BACKEND_HOST)


# Initialize config on import
_config = load_config()
