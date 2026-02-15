# Gesture Control YouTube Player (Python + MediaPipe)

Control YouTube in your browser using hand gestures detected from your webcam.

This script uses:
- **OpenCV** for camera capture
- **MediaPipe Hands** for hand landmark tracking
- **PyAutoGUI** for keyboard shortcuts (fullscreen, next, close tab)
- **YouTube Data API v3** to search a song and open the first result

---

## Features
Open the first YouTube result for a song query  
Skip to next YouTube video  
toggle fullscreen (YouTube “F”)  
Close the current browser tab (Ctrl+W)  
Hold-to-trigger + cooldown to reduce accidental actions  

---

## Gestures & Actions

| Gesture | Meaning | Action |
| ✌️ Peace sign (index + middle up) | Open YouTube song | Searches `YOUTUBE_QUERY` and opens first result |
| 🤙 Pinky only (pinky up, others down) | Next video | `Shift + N` |
| ✋ Open palm (4 fingers up) | Fullscreen | `F` |
| 👊 Fist (no fingers up) | Close tab | `Ctrl + W` |

**Hold time:** `0.4s` (default)  
**Cooldown:** `3.0s` (default)

---

## Requirements

- Python 3.9+ recommended
- A working webcam
- Chrome / Edge (or any browser that supports these shortcuts)
- A YouTube Data API key

---

## Install (Windows / macOS / Linux)

### 1) Create a virtual environment (recommended)
**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
