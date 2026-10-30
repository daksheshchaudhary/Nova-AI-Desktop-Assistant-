# Nova
## AI-Powered Windows Voice Assistant

Nova is a voice-activated desktop assistant built with Python that lets you control your Windows PC entirely through speech. Say "Nova" to wake it up and give any command, from opening apps to asking the AI brain anything you want.

## Features

- Wake word detection: Say "Nova" to activate, works even with background noise
- AI Brain: Powered by Groq (LLaMA 3.1) for open-ended questions and conversations
- Spotify control: Search and play any song, pause, skip, previous, current song
- App control: Open and close any app with smart fuzzy matching
- Volume and Brightness: Instant control using voice
- Weather: Real-time weather for any city (no API key needed)
- Screenshot: Saves to Desktop automatically
- Math: Solve calculations with your voice
- Web: Open any website by voice
- Wikipedia: Search any topic
- Jokes: Because why not
- System controls: Lock, sleep, shutdown, restart with confirmation
- Battery status: Check remaining battery
- Visual overlay: Screen corners pulse in red-orange when Nova is active
- Volume ducking: Background volume drops instantly when Nova wakes up
- System tray: Runs silently in the background

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Speech Recognition | SpeechRecognition, PyAudio |
| Text to Speech | pyttsx3 |
| AI Brain | Groq API (LLaMA 3.1) |
| Music | Spotify Web API, Spotipy |
| System Control | pyautogui, keyboard, psutil, nircmd |
| Brightness | screen-brightness-control |
| Window Control | pygetwindow |
| UI | Tkinter, pystray, Pillow |
| Packaging | PyInstaller |
| Weather | wttr.in (free, no API key) |

## Requirements

- Windows 10 or 11 (64-bit)
- Python 3.11
- Microphone
- Spotify Premium (for playback control)
- Active internet connection

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOURUSERNAME/Nova.git
cd Nova
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install speechrecognition pyttsx3 pyautogui screen-brightness-control psutil pygetwindow keyboard pystray pillow requests pyjokes wikipedia groq spotipy re warnings
```

### 4. Download nircmd

Download from https://www.nirsoft.net/utils/nircmd.html (64-bit version).

Place nircmd.exe in the project folder.

### 5. Add your API keys

Open main.py and fill in:

```python
GROQ_API_KEY = "your-groq-key-here"
SPOTIFY_CLIENT_ID = "your-spotify-client-id"
SPOTIFY_CLIENT_SECRET = "your-spotify-client-secret"
```

Groq API key: Free at https://console.groq.com

Spotify credentials: Free at https://developer.spotify.com/dashboard

### 6. Run Nova

```bash
python main.py
```

## Build as EXE

```bash
pyinstaller --noconfirm --onedir --windowed ^
  --name Nova ^
  --icon=nova.ico ^
  --add-data "nova.ico;." ^
  --add-data "wake.wav;." ^
  --add-data "done.wav;." ^
  --add-data "nircmd.exe;." ^
  --hidden-import pyttsx3.drivers ^
  --hidden-import pyttsx3.drivers.sapi5 ^
  --hidden-import speech_recognition ^
  --hidden-import pyaudio ^
  --hidden-import screen_brightness_control ^
  --hidden-import pystray ^
  --hidden-import PIL ^
  --hidden-import groq ^
  main.py
```

The EXE will be in the dist/Nova/ folder.

## Voice Commands

| Command | Example |
|---|---|
| Open app | "open spotify" |
| Close app | "close chrome" |
| Play song | "play Blinding Lights on Spotify" |
| Pause Spotify | "pause spotify" |
| Next song | "next song" |
| Previous song | "previous song" |
| Current song | "what song is playing" |
| Volume up/down | "volume up" / "volume down" |
| Set volume | "volume 60" |
| Brightness up/down | "brightness up" / "brightness down" |
| Weather | "weather" / "weather in Mumbai" |
| Time | "what time is it" |
| Date | "what day is it" |
| Screenshot | "take a screenshot" |
| Math | "calculate 25 plus 30" |
| Open website | "go to youtube.com" |
| Wikipedia | "who is Elon Musk" |
| Joke | "tell me a joke" |
| Battery | "battery" |
| Lock PC | "lock" |
| Sleep PC | "sleep" |
| Shutdown | "shutdown" |
| Restart | "restart" |
| Ask AI anything | "what is the meaning of life" |
| Exit | "goodbye" |

## Project Structure

```text
nova/
├── main.py          # Main application
├── apps.py          # App scanning and fuzzy matching
├── apps.json        # Cached app database
├── nova.ico         # Tray icon
├── wake.wav         # Wake sound
├── done.wav         # Done sound
├── nircmd.exe       # Volume control tool
└── build_nova.bat   # Build script for EXE
```

## How It Works

1. Nova runs silently in the Windows system tray.
2. It continuously listens for the wake word "Nova".
3. On detection, screen corners glow and volume ducks to 30% instantly.
4. Nova listens for your command.
5. The command is matched against built-in actions.
6. If no match, it is sent to the Groq AI for a natural response.
7. Nova speaks the response at full volume.
8. Volume restores, overlay disappears, and Nova goes back to listening.

## Known Limitations

- Spotify control requires Spotify Premium.
- Brightness control may not work on all monitors/display adapters.
- Web apps like LinkedIn or SoundCloud cannot be opened (no desktop install).
- Requires internet for speech recognition and AI responses.

## Author

Built by Dakshesh Chaudhary.

## License

This project is private and not licensed for public distribution.