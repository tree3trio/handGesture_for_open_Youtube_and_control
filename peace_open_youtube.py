import time
import webbrowser
import requests
import os
import cv2
import mediapipe as mp
import pyautogui


# CONFIG

YOUTUBE_QUERY = "Past Won't Leave My Bed"

HOLD_SECONDS = 0.4
COOLDOWN_SECONDS = 3.0

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set")

# Optional: make pyautogui safer (move mouse to corner to abort)
pyautogui.FAILSAFE = True

# MediaPipe setup

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def finger_extended(lm, tip, pip):
    # OpenCV coordinate system: smaller y = higher on screen
    return lm[tip].y < lm[pip].y


def count_extended_fingers(lm):
    """
    Count extended fingers among index/middle/ring/pinky.
    Thumb is ignored to keep things simpler & more stable.
    """
    index_up = finger_extended(lm, 8, 6)
    middle_up = finger_extended(lm, 12, 10)
    ring_up = finger_extended(lm, 16, 14)
    pinky_up = finger_extended(lm, 20, 18)
    return index_up + middle_up + ring_up + pinky_up, (index_up, middle_up, ring_up, pinky_up)

def pinky_only(lm):
    # pinky up, index/middle/ring down (thumb ignored)
    index_up = finger_extended(lm, 8, 6)
    middle_up = finger_extended(lm, 12, 10)
    ring_up = finger_extended(lm, 16, 14)
    pinky_up = finger_extended(lm, 20, 18)
    return pinky_up and (not index_up) and (not middle_up) and (not ring_up)

def peace_sign(lm):
    #  index + middle up, ring + pinky down
    n, (i, m, r, p) = count_extended_fingers(lm)
    return i and m and (not r) and (not p)


def open_palm(lm):
    #  open hand (index+middle+ring+pinky up)
    n, _ = count_extended_fingers(lm)
    return n == 4


def fist(lm):
    #  fist (index+middle+ring+pinky down)
    n, _ = count_extended_fingers(lm)
    return n == 0


def open_first_youtube_result(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "maxResults": 1,
        "q": query,
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("items"):
        video_id = data["items"][0]["id"]["videoId"]
        webbrowser.open(f"https://www.youtube.com/watch?v={video_id}&autoplay=1")


def fullscreen_browser():
    # Windows/Chrome/Edge fullscreen shortcut
    pyautogui.press("F")


def close_tab():
    # Close current tab in most browsers
    pyautogui.hotkey("ctrl", "w")
    
def skip_song():
    # YouTube next video shortcut
    pyautogui.hotkey("shift", "n")



# Camera loop

cap = cv2.VideoCapture(0)
hold_start = None
last_action = 0.0

with mp_hands.Hands(
    model_complexity=0,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        now = time.time()
        gesture = None  # "peace", "index", "palm", "fist"

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark

            # Priority order matters to avoid collisions
            if peace_sign(lm):
                gesture = "peace"
            elif pinky_only(lm):
                gesture = "pinky"
            elif open_palm(lm):
                gesture = "palm"
            elif fist(lm):
                gesture = "fist"

        if gesture:
            if gesture == "peace":
                label = "✌️ PEACE → YouTube (auto first)"
            elif gesture == "pinky":
                label = "🤙 PINKY → Next (Shift+N)"
            elif gesture == "palm":
                label = "✋ PALM → Fullscreen (F)"
            else:
                label = "👊 FIST → Close Tab (Ctrl+W)"

            cv2.putText(frame, label, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if hold_start is None:
                hold_start = now

            held = now - hold_start
            cv2.putText(frame, f"Hold: {held:.2f}s", (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            if held >= HOLD_SECONDS and (now - last_action) >= COOLDOWN_SECONDS:
                
                if gesture == "peace":
                    open_first_youtube_result(YOUTUBE_QUERY)
                elif gesture == "pinky":
                    skip_song()
                elif gesture == "palm":
                    fullscreen_browser()
                elif gesture == "fist":
                    close_tab()

                last_action = now
                hold_start = None
        else:
            hold_start = None
            cv2.putText(
                frame,
                "✌️ YouTube | 🤚 Pinky | ✋ Fullscreen | 👊 Close Tab",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2
            )

        cv2.putText(frame, "Press + to quit",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (200, 200, 200),
                    2)

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF in (ord('+'), ord('+')):
            break

cap.release()
cv2.destroyAllWindows()
#python   to open intherminal