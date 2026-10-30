import sys
import speech_recognition as sr
import pyttsx3
import pyautogui
import screen_brightness_control as sbc
import psutil
import os
import winsound
from dotenv import load_dotenv
load_dotenv()
from apps import load_apps, scan_apps, find_app
from difflib import get_close_matches
import pygetwindow as gw
import time
import keyboard
import threading
import pystray
from PIL import Image
import datetime
import requests
import pyjokes
import wikipedia
import webbrowser
from groq import Groq
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import warnings
warnings.filterwarnings("ignore")
import subprocess

# ---------------- RESOURCE PATH ----------------

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# ---------------- SETUP ----------------

apps = load_apps()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

listener = sr.Recognizer()
listener.pause_threshold = 0.6
listener.non_speaking_duration = 0.3

# ---------------- VOLUME CONTROL ----------------

original_volume = None  # will be set at runtime
NIRCMD = resource_path("nircmd.exe")

def get_master_volume():
    try:
        import subprocess
        result = subprocess.run(
            ['powershell', '-WindowStyle', 'Hidden', '-command',
             '[Math]::Round((Get-Volume).Volume * 100)'],
            capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        val = int(result.stdout.strip())
        return val
    except:
        return 70

def duck_volume():
    global original_volume
    original_volume = get_master_volume()
    subprocess.Popen(
        [NIRCMD, "setsysvolume", str(int(30 * 655.35))],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def restore_volume():
    if original_volume is not None:
        subprocess.Popen(
            [NIRCMD, "setsysvolume", str(int(original_volume * 655.35))],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

# ---------------- AI BRAIN (Groq) ----------------

# GROQ_API_KEY = ""
# ai_client = Groq(api_key=GROQ_API_KEY)
# conversation_history = []
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

ai_client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

def ask_ai(user_input):
    try:
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = ai_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """You are Nova, a smart friendly and concise voice assistant on Windows.
Keep responses short and natural — you are speaking out loud, not writing.
Avoid bullet points, markdown, asterisks or long lists. Speak in plain sentences."""
                }
            ] + conversation_history,
            max_tokens=300
        )

        reply = response.choices[0].message.content
        reply = reply.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
        print(f"Nova (AI): {reply}")

        conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        if len(conversation_history) > 20:
            conversation_history.pop(0)
            conversation_history.pop(0)

        talk(reply)

    except Exception as e:
        print(f"AI error: {e}")
        talk("I'm having trouble thinking right now, try again.")

# ---------------- SPOTIFY ----------------


# SPOTIFY_CLIENT_ID = "8d00ddecbf584f4e902876aa912c2004"
# SPOTIFY_CLIENT_SECRET = "2b88fa1777984851bb399b7fa748a629"
# SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
#
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI,
#     scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
# ))
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
))

def get_active_device():
    try:
        devices = sp.devices()
        if not devices["devices"]:
            return None
        for d in devices["devices"]:
            if d["is_active"]:
                return d["id"]
        return devices["devices"][0]["id"]
    except:
        return None

def spotify_play_song(song_name):
    try:
        s = song_name.lower()
        s = re.sub(r'\bon spotify\b', '', s)
        s = re.sub(r'\bspotify\b', '', s)
        s = re.sub(r'\bplay\b', '', s)
        s = re.sub(r'\bsong\b', '', s)
        s = re.sub(r'\btrack\b', '', s)
        s = ' '.join(s.split()).strip()
        print(f"Searching Spotify for: '{s}'")

        results = sp.search(q=f"track:{s}", limit=1, type="track")
        tracks = results["tracks"]["items"]
        if not tracks:
            results = sp.search(q=s, limit=1, type="track")
            tracks = results["tracks"]["items"]

        if not tracks:
            talk(f"Couldn't find {s} on Spotify")
            return

        track = tracks[0]
        track_uri = track["uri"]
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        print(f"Found: {track_name} by {artist_name}")

        spotify_running = any("spotify" in p.name().lower()
                            for p in psutil.process_iter(['name']))
        if not spotify_running:
            talk("Opening Spotify")
            os.startfile(r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getlogin()))
            time.sleep(6)

        try:
            for win in gw.getAllWindows():
                if "spotify" in win.title.lower() and win.title.strip() != "":
                    win.activate()
                    time.sleep(1)
                    break
        except Exception:
            pass

        device_id = None
        for attempt in range(8):
            device_id = get_active_device()
            if device_id:
                break
            print(f"Waiting for Spotify device... attempt {attempt + 1}")
            time.sleep(2)

        if not device_id:
            talk("Spotify isn't responding. Please click on Spotify and try again.")
            return

        sp.start_playback(device_id=device_id, uris=[track_uri])
        time.sleep(0.5)
        talk(f"Playing {track_name} by {artist_name}")

    except Exception as e:
        print(f"Spotify error: {e}")
        talk("Something went wrong with Spotify")

def spotify_pause():
    try:
        sp.pause_playback()
        talk("Paused Spotify")
    except Exception as e:
        print(e)
        talk("Couldn't pause Spotify")

def spotify_resume():
    try:
        device_id = get_active_device()
        if device_id:
            sp.start_playback(device_id=device_id)
            talk("Resuming Spotify")
        else:
            talk("No active Spotify device found")
    except Exception as e:
        print(e)
        talk("Couldn't resume Spotify")

def spotify_next():
    try:
        sp.next_track()
        talk("Next song")
    except Exception as e:
        print(e)
        talk("Couldn't skip song")

def spotify_previous():
    try:
        sp.previous_track()
        talk("Previous song")
    except Exception as e:
        print(e)
        talk("Couldn't go back")

def spotify_current_song():
    try:
        current = sp.current_playback()
        if current and current["is_playing"]:
            track = current["item"]["name"]
            artist = current["item"]["artists"][0]["name"]
            talk(f"Currently playing {track} by {artist}")
        else:
            talk("Nothing is playing right now")
    except Exception as e:
        print(e)
        talk("Couldn't get current song")

# ---------------- SPEAK ----------------

def talk(text):
    # restore volume so Nova speaks clearly
    if original_volume is not None:
        subprocess.Popen(
            [NIRCMD, "setsysvolume", str(int(original_volume * 655.35))],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(0.3)  # tiny wait for volume to apply
    engine = pyttsx3.init()
    engine.setProperty("rate", 200)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    # duck back down after speaking if we're mid-command
    subprocess.Popen(
        [NIRCMD, "setsysvolume", str(int(30 * 655.35))],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

# ---------------- LISTEN ----------------

def listen():
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=0.3)
            listener.energy_threshold = 400
            listener.dynamic_energy_threshold = True
            listener.dynamic_energy_adjustment_damping = 0.15
            listener.dynamic_energy_ratio = 1.5
            audio = listener.listen(source, timeout=2, phrase_time_limit=4)
        command = listener.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except AssertionError:
        time.sleep(1)
        return ""
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except OSError:
        time.sleep(1)
        return ""
    except KeyboardInterrupt:
        print("Stopped manually")
        exit()

# ---------------- WAKE WORD ----------------

def listen_for_wakeword():
    while True:
        try:
            with sr.Microphone() as source:
                # longer ambient noise adjustment for wake word
                listener.adjust_for_ambient_noise(source, duration=0.5)
                listener.energy_threshold = 350
                listener.dynamic_energy_threshold = True
                # longer phrase limit so "hey nova" is caught fully
                audio = listener.listen(source, timeout=3, phrase_time_limit=4)
            text = listener.recognize_google(audio).lower()
            print(f"Heard: {text}")
            if "nova" in text or "nov" in text or "nova" in text or "no va" in text:
                return
        except:
            pass

# ---------------- SOUNDS ----------------

def play_wake_sound():
    path = resource_path("wake.wav")
    if os.path.exists(path):
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

def play_done_sound():
    path = resource_path("done.wav")
    if os.path.exists(path):
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

# ---------------- TRAY ----------------

def run_nova():
    print("Nova running in background...")
    while True:
        listen_for_wakeword()
        duck_volume()
        play_wake_sound()
        command = listen()
        if command:
            handle_command(command)
        play_done_sound()
        restore_volume()  # final restore after everything is done

def quit_nova(icon, item):
    icon.stop()
    os._exit(0)

def tray_icon():
    image = Image.open(resource_path("nova.ico"))
    menu = pystray.Menu(pystray.MenuItem("Exit Nova", quit_nova))
    icon = pystray.Icon("Nova", image, "Nova Assistant", menu)
    threading.Thread(target=run_nova, daemon=True).start()
    icon.run()

# ---------------- MEDIA CONTROLS ----------------

def control_app_media(app_name, action):
    app_name = app_name.lower()
    for win in gw.getAllWindows():
        title = win.title.lower()
        if app_name in title and title != "":
            try:
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(1)
                keyboard.press_and_release("play/pause media")
                talk(f"{action}ed {app_name}")
                return
            except Exception as e:
                print(e)
    talk(f"{app_name} not found")

# ---------------- CONFIRMATION ----------------

def confirm_action():
    talk("Are you sure?")
    response = listen()
    if response == "":
        talk("Cancelled")
        return False
    if any(word in response for word in ["yes", "yeah", "confirm", "do it", "sure"]):
        talk("Confirmed")
        return True
    talk("Cancelled")
    return False

# ---------------- APPS ----------------

def open_app(app_name):
    apps = load_apps()
    app_name = app_name.lower().strip()

    matched, path = find_app(app_name, apps)
    if matched:
        os.startfile(path)
        talk(f"Opening {matched}")
        return

    talk("App not found. Rescanning, one moment.")
    apps_fresh = scan_apps()

    matched, path = find_app(app_name, apps_fresh)
    if matched:
        os.startfile(path)
        talk(f"Opening {matched}")
    else:
        talk(f"Sorry, I couldn't find {app_name}")

def close_app(app_name):
    app_name = app_name.lower().strip()

    for win in gw.getAllWindows():
        title = win.title.lower()
        if app_name in title and title != "":
            try:
                win.close()
                talk(f"Closed {app_name}")
                return
            except Exception as e:
                print(e)

    all_titles = [w.title.lower() for w in gw.getAllWindows() if w.title.strip()]
    fuzzy = get_close_matches(app_name, all_titles, n=1, cutoff=0.5)
    if fuzzy:
        for win in gw.getAllWindows():
            if win.title.lower() == fuzzy[0]:
                try:
                    win.close()
                    talk(f"Closed {fuzzy[0]}")
                    return
                except Exception as e:
                    print(e)

    for proc in psutil.process_iter(['pid', 'name']):
        proc_name = proc.info['name'].lower().replace(".exe", "").replace("-", " ").replace("_", " ")
        if app_name in proc_name or proc_name in app_name:
            try:
                proc.terminate()
                talk(f"Closed {app_name}")
                return
            except Exception as e:
                print(e)

    running = {
        p.info['name'].lower().replace(".exe", "").replace("-", " ").replace("_", " "): p
        for p in psutil.process_iter(['pid', 'name'])
    }
    fuzzy_proc = get_close_matches(app_name, running.keys(), n=1, cutoff=0.6)
    if fuzzy_proc:
        try:
            running[fuzzy_proc[0]].terminate()
            talk(f"Closed {fuzzy_proc[0]}")
            return
        except Exception as e:
            print(e)

    talk(f"I couldn't find {app_name} running")

# ---------------- MEDIA ----------------

def play_pause():
    keyboard.send("play/pause media")

# ---------------- VOLUME ----------------

def volume_up():
    pyautogui.press("volumeup")

def volume_down():
    pyautogui.press("volumedown")

def set_volume(percent):
    global original_volume
    percent = max(0, min(100, percent))
    subprocess.Popen(
        [NIRCMD, "setsysvolume", str(int(percent * 655.35))],
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    original_volume = percent
    talk(f"Volume set to {percent}")

# ---------------- BRIGHTNESS ----------------

def brightness_up():
    try:
        current = sbc.get_brightness(display=0)
        if isinstance(current, list):
            current = current[0]
        sbc.set_brightness(min(100, current + 10))
    except Exception:
        talk("Brightness control not supported")

def brightness_down():
    try:
        current = sbc.get_brightness(display=0)
        if isinstance(current, list):
            current = current[0]
        sbc.set_brightness(max(0, current - 10))
    except Exception:
        talk("Brightness control not supported")

# ---------------- SYSTEM ----------------

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        talk(f"Battery at {int(battery.percent)} percent")
    else:
        talk("Could not read battery status")

def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")

def sleep_pc():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

# ---------------- TIME & DATE ----------------

def tell_time():
    now = datetime.datetime.now()
    talk(f"It is {now.strftime('%I:%M %p')}")

def tell_date():
    now = datetime.datetime.now()
    talk(f"Today is {now.strftime('%A, %B %d %Y')}")

# ---------------- WEATHER ----------------

def tell_weather(city="Dehradun"):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        res = requests.get(url, timeout=5).json()
        temp = res["current_condition"][0]["temp_C"]
        desc = res["current_condition"][0]["weatherDesc"][0]["value"]
        feels_like = res["current_condition"][0]["FeelsLikeC"]
        talk(f"It is {desc} in {city}, {temp} degrees celsius, feels like {feels_like} degrees")
    except Exception:
        talk("Weather service is unavailable right now")

# ---------------- JOKES ----------------

def tell_joke():
    joke = pyjokes.get_joke()
    print(joke)
    talk(joke)

# ---------------- WIKIPEDIA ----------------

def search_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=2, auto_suggest=True)
        print(summary)
        talk(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        talk(f"That topic is broad. Did you mean {e.options[0]}?")
    except wikipedia.exceptions.PageError:
        talk(f"I couldn't find anything about {query}")
    except Exception:
        talk("Something went wrong with the search")

# ---------------- OPEN WEBSITE ----------------

def open_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    talk(f"Opening {url}")

# ---------------- MATH ----------------

def calculate(command):
    try:
        command = command.replace("times", "*").replace("divided by", "/")
        command = command.replace("plus", "+").replace("minus", "-")
        command = command.replace("into", "*").replace("squared", "**2")
        expr = "".join(ch for ch in command if ch in "0123456789+-*/.() ")
        result = eval(expr.strip())
        talk(f"The answer is {result}")
        print(f"Result: {result}")
    except Exception:
        talk("I couldn't calculate that")

# ---------------- SCREENSHOT ----------------

def take_screenshot():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"nova_{now}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        talk("Screenshot saved to your Desktop")
        print(f"Screenshot saved: {path}")
    except Exception as e:
        talk("Couldn't take screenshot")
        print(e)

# ---------------- COMMAND HANDLER ----------------

def handle_command(command):
    if not command:
        return

    if "exit" in command or "goodbye" in command or "bye nova" in command:
        talk("Goodbye")
        os._exit(0)

    elif "what time" in command or ("time" in command and "weather" not in command):
        tell_time()

    elif "play" in command and "spotify" in command:
        song = command.replace("play", "").replace("spotify", "").replace("on", "").strip()
        if song:
            spotify_play_song(song)
        else:
            spotify_resume()

    elif "pause spotify" in command or "stop spotify" in command:
        spotify_pause()

    elif "next song" in command or "skip song" in command:
        spotify_next()

    elif "previous song" in command or "last song" in command:
        spotify_previous()

    elif "what song" in command or "current song" in command:
        spotify_current_song()

    elif "what date" in command or "what day" in command or "date" in command or "day" in command:
        tell_date()

    elif "screenshot" in command:
        take_screenshot()

    elif "go to" in command or "open website" in command:
        url = command.replace("open website", "").replace("go to", "").strip()
        open_website(url)

    elif "open" in command:
        open_app(command.replace("open", "").strip())

    elif "close" in command:
        close_app(command.replace("close", "").strip())

    elif "pause" in command or "play" in command:
        play_pause()
        talk("Done")

    elif "volume up" in command:
        volume_up()
    elif "volume down" in command:
        volume_down()
    elif "volume" in command:
        for word in command.split():
            if word.isdigit():
                set_volume(int(word))
                break

    elif "brightness up" in command:
        brightness_up()
    elif "brightness down" in command:
        brightness_down()

    elif "battery" in command:
        battery_status()

    elif "weather" in command:
        city = "Dehradun"
        if "in" in command:
            city = command.split("in")[-1].strip()
        tell_weather(city)

    elif "joke" in command:
        tell_joke()

    elif "calculate" in command:
        calculate(command.replace("calculate", "").strip())

    elif "lock" in command:
        if confirm_action():
            talk("Locking computer")
            lock_pc()

    elif "sleep" in command:
        if confirm_action():
            talk("Sleeping computer")
            sleep_pc()

    elif "shutdown" in command:
        if confirm_action():
            talk("Shutting down")
            os.system("shutdown /s /t 1")

    elif "restart" in command:
        if confirm_action():
            talk("Restarting")
            os.system("shutdown /r /t 1")

    else:
        ask_ai(command)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    print("Nova is running... Say 'Nova'")
    tray_icon()