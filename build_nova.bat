@echo off
echo Building Nova EXE...
pyinstaller --noconfirm --onedir --windowed ^
  --name Nova ^
  --icon=nova.ico ^
  --add-data "nova.ico;." ^
  --add-data "wake.wav;." ^
  --add-data "done.wav;." ^
  --hidden-import pyttsx3.drivers ^
  --hidden-import pyttsx3.drivers.sapi5 ^
  --hidden-import pyttsx3.drivers.espeak ^
  --hidden-import speech_recognition ^
  --hidden-import pyaudio ^
  --hidden-import screen_brightness_control ^
  --hidden-import pystray ^
  --hidden-import PIL ^
  --hidden-import PIL.Image ^
  --hidden-import comtypes.client ^
  --hidden-import comtypes.server ^
  --hidden-import google.genai ^
  main.py
echo.
echo Done! Your EXE is in the "dist" folder.
pause