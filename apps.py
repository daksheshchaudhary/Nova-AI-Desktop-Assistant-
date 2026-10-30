import os
import json
from difflib import get_close_matches

APP_DB = os.path.join(
    os.getenv("LOCALAPPDATA"),
    "Nova",
    "apps.json"
)

os.makedirs(os.path.dirname(APP_DB), exist_ok=True)

SEARCH_DIRS = [
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
    os.path.expandvars(r"%USERPROFILE%\Desktop"),
    r"C:\Program Files",
    r"C:\Program Files (x86)"
]


def scan_apps():
    apps = {}

    for base in SEARCH_DIRS:
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.endswith(".lnk") or file.endswith(".exe"):
                    name = (
                        file.lower()
                        .replace(".lnk", "")
                        .replace(".exe", "")
                        .replace("-", " ")
                        .replace("_", " ")
                        .strip()
                    )
                    path = os.path.join(root, file)
                    apps[name] = path

    with open(APP_DB, "w") as f:
        json.dump(apps, f, indent=4)

    return apps


def load_apps():
    if not os.path.exists(APP_DB):
        return scan_apps()

    with open(APP_DB, "r") as f:
        return json.load(f)


def find_app(spoken_name, apps):
    """
    Smart multi-stage app matching.
    Returns (matched_name, path) or (None, None)
    """
    spoken = spoken_name.lower().strip()
    keys = list(apps.keys())

    # Stage 1: Exact match
    if spoken in apps:
        return spoken, apps[spoken]

    # Stage 2: Fuzzy match (handles typos, close names)
    fuzzy = get_close_matches(spoken, keys, n=1, cutoff=0.6)
    if fuzzy:
        return fuzzy[0], apps[fuzzy[0]]

    # Stage 3: Partial / word match
    # e.g. "chrome" matches "google chrome"
    spoken_words = spoken.split()
    candidates = []

    for key in keys:
        key_words = key.split()
        # Check if ALL spoken words appear somewhere in the key
        if all(any(sw in kw for kw in key_words) for sw in spoken_words):
            candidates.append(key)
        # Also check if spoken is a substring of the key
        elif spoken in key:
            candidates.append(key)

    if candidates:
        # Pick the shortest/closest match
        candidates.sort(key=lambda x: abs(len(x) - len(spoken)))
        return candidates[0], apps[candidates[0]]

    # Stage 4: Reverse partial match
    # e.g. "microsoft edge" matches "edge"
    for key in keys:
        if key in spoken or spoken in key:
            return key, apps[key]

    return None, None