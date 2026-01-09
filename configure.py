#!/usr/bin/env python3
"""
WaveReborn Configuration Utility
Interactive CLI tool for configuring WaveReborn settings
"""

import subprocess
import json
import os
import sys

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wave_config.json")


def list_audio_devices():
    """List all available PulseAudio output devices"""
    try:
        result = subprocess.run(
            ["pactl", "list", "short", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )
        devices = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    idx = parts[0].strip()
                    name = parts[1].strip()
                    devices.append((idx, name))
        return devices
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def get_device_description(device_name):
    """Get human-readable description of a device"""
    try:
        result = subprocess.run(
            ["pactl", "list", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )

        in_device = False
        for line in result.stdout.split('\n'):
            if f"Name: {device_name}" in line:
                in_device = True
            elif in_device and "Description:" in line:
                return line.split("Description:")[1].strip()
            elif in_device and line.startswith("Sink #"):
                in_device = False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return device_name


def load_config():
    """Load current configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Default config
    return {
        "audio": {
            "output_device": "alsa_output.usb-Maono_ProStudio_2x2_Lite-analog-stereo",
            "channels": ["Music", "Game", "Voice", "System"],
            "latency_ms": 20
        },
        "network": {
            "backend_port": 8000,
            "frontend_port": 8080,
            "backend_host": "127.0.0.1"
        }
    }


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, indent=2, fp=f)
        print(f"\n✅ Configuration saved to {CONFIG_FILE}")
        return True
    except IOError as e:
        print(f"\n❌ Error saving config: {e}")
        return False


def configure_audio_device():
    """Interactive audio device configuration"""
    print("\n" + "="*60)
    print("🎧 Audio Device Configuration")
    print("="*60)

    devices = list_audio_devices()
    if not devices:
        print("\n❌ No PulseAudio devices found. Is PulseAudio running?")
        return None

    print("\nAvailable audio output devices:\n")
    for i, (idx, name) in enumerate(devices, 1):
        desc = get_device_description(name)
        print(f"{i}. {desc}")
        print(f"   Device: {name}\n")

    while True:
        try:
            choice = input(f"Select device (1-{len(devices)}) or 'q' to cancel: ").strip()
            if choice.lower() == 'q':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(devices):
                return devices[choice_num - 1][1]
            else:
                print(f"Please enter a number between 1 and {len(devices)}")
        except ValueError:
            print("Please enter a valid number")


def configure_channels():
    """Interactive channel configuration"""
    print("\n" + "="*60)
    print("📻 Channel Configuration")
    print("="*60)

    print("\nDefault channels: Music, Game, Voice, System")
    print("You can customize the channel names.\n")

    use_default = input("Use default channels? (y/n): ").strip().lower()
    if use_default == 'y':
        return ["Music", "Game", "Voice", "System"]

    channels = []
    print("\nEnter channel names (enter empty name to finish, minimum 2 channels):")
    i = 1
    while True:
        name = input(f"Channel {i}: ").strip()
        if not name:
            if len(channels) >= 2:
                break
            else:
                print("Please enter at least 2 channels")
                continue
        if name not in channels:
            channels.append(name)
            i += 1
        else:
            print(f"Channel '{name}' already exists")

    return channels


def configure_latency():
    """Interactive latency configuration"""
    print("\n" + "="*60)
    print("⏱️  Audio Latency Configuration")
    print("="*60)

    print("\nAudio latency in milliseconds (lower = less delay, but more CPU)")
    print("Recommended: 20ms (default)")
    print("Low-latency: 10ms")
    print("High stability: 50ms\n")

    while True:
        try:
            latency = input("Enter latency in ms (10-100) [default: 20]: ").strip()
            if not latency:
                return 20

            latency_ms = int(latency)
            if 10 <= latency_ms <= 100:
                return latency_ms
            else:
                print("Please enter a value between 10 and 100")
        except ValueError:
            print("Please enter a valid number")


def configure_network():
    """Interactive network configuration"""
    print("\n" + "="*60)
    print("🌐 Network Configuration")
    print("="*60)

    print("\nBackend API port (default: 8000)")
    backend_port = input("Backend port [8000]: ").strip()
    backend_port = int(backend_port) if backend_port else 8000

    print("\nFrontend server port (default: 8080)")
    frontend_port = input("Frontend port [8080]: ").strip()
    frontend_port = int(frontend_port) if frontend_port else 8080

    print("\nBackend host (default: 127.0.0.1)")
    backend_host = input("Backend host [127.0.0.1]: ").strip()
    backend_host = backend_host if backend_host else "127.0.0.1"

    return {
        "backend_port": backend_port,
        "frontend_port": frontend_port,
        "backend_host": backend_host
    }


def show_current_config():
    """Display current configuration"""
    config = load_config()

    print("\n" + "="*60)
    print("📋 Current Configuration")
    print("="*60)

    print("\n🎧 Audio Settings:")
    audio = config.get("audio", {})
    device = audio.get("output_device", "Not set")
    print(f"  Output Device: {device}")
    desc = get_device_description(device)
    if desc != device:
        print(f"  Description: {desc}")
    print(f"  Channels: {', '.join(audio.get('channels', []))}")
    print(f"  Latency: {audio.get('latency_ms', 20)}ms")

    print("\n🌐 Network Settings:")
    network = config.get("network", {})
    print(f"  Backend: {network.get('backend_host', '127.0.0.1')}:{network.get('backend_port', 8000)}")
    print(f"  Frontend: {network.get('frontend_port', 8080)}")

    print("\n" + "="*60)


def main():
    """Main configuration menu"""
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║         WaveReborn Configuration Utility                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    if not os.path.exists(CONFIG_FILE):
        print("\n⚠️  No configuration file found. Creating default config...")
        config = load_config()
        save_config(config)

    while True:
        show_current_config()

        print("\n📝 Configuration Options:")
        print("  1. Configure audio output device")
        print("  2. Configure channels")
        print("  3. Configure audio latency")
        print("  4. Configure network ports")
        print("  5. Quick setup (all options)")
        print("  6. Reset to defaults")
        print("  q. Quit")

        choice = input("\nSelect option: ").strip().lower()

        config = load_config()

        if choice == '1':
            device = configure_audio_device()
            if device:
                config["audio"]["output_device"] = device
                save_config(config)

        elif choice == '2':
            channels = configure_channels()
            if channels:
                config["audio"]["channels"] = channels
                save_config(config)

        elif choice == '3':
            latency = configure_latency()
            if latency:
                config["audio"]["latency_ms"] = latency
                save_config(config)

        elif choice == '4':
            network = configure_network()
            if network:
                config["network"] = network
                save_config(config)

        elif choice == '5':
            # Quick setup
            print("\n🚀 Quick Setup - Configure all options\n")

            device = configure_audio_device()
            if device:
                config["audio"]["output_device"] = device

            channels = configure_channels()
            if channels:
                config["audio"]["channels"] = channels

            latency = configure_latency()
            if latency:
                config["audio"]["latency_ms"] = latency

            network = configure_network()
            if network:
                config["network"] = network

            save_config(config)

        elif choice == '6':
            confirm = input("\n⚠️  Reset to defaults? This will overwrite your config (y/n): ").strip().lower()
            if confirm == 'y':
                os.remove(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None
                print("✅ Configuration reset to defaults")

        elif choice == 'q':
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuration cancelled")
        sys.exit(0)
