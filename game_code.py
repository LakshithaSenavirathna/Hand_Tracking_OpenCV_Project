import random
import time
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
from PIL import Image
import pygame
import os
import speech_recognition as sr
import pyttsx3
import threading
import queue
import requests
import json

# Initialize pygame mixer
pygame.mixer.init()

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "deepseek/deepseek-r1:free"


def get_ai_response(prompt):
    """Get response from OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return None


# Voice Interaction System Setup
class VoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.listening = False
        self.last_command_time = 0
        self.command_cooldown = 2

        # Configure voice
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()

        threading.Thread(target=_speak).start()

    def listen_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    command = self.recognizer.recognize_google(audio).lower()
                    if time.time() - self.last_command_time > self.command_cooldown:
                        self.command_queue.put(command)
                        self.last_command_time = time.time()
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as e:
                    print(f"Voice recognition error: {e}")

    def start_listening(self):
        if not self.listening:
            self.listening = True
            threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        self.listening = False

# Initialize voice system
voice_system = VoiceSystem()

def process_voice_command(command, game_state, score, top_score):
    response = None
    command = command.lower()

    if "start" in command and game_state == "start":
        return "playing", None
    elif "restart" in command and game_state == "end":
        return "playing", "Game restarted!"
    elif "quit" in command or "exit" in command:
        return "quit", "Quitting game..."

    if game_state == "playing":
        if "score" in command:
            response = f"Your score is {score}"
        elif "time" in command:
            remaining = int(totalTime - (time.time() - timeStart))
            response = f"{remaining} seconds remaining"
        elif "tip" in command or "help" in command:
            prompt = f"The player asked for help in a hand-tracking game. Current score: {score}. Give one short tip."
            response = get_ai_response(prompt) or "Try focusing on the center of targets"

    if "compliment" in command or "encourage" in command:
        prompt = f"The player requested encouragement in a hand-tracking game. Score: {score}. Give a short motivational phrase."
        response = get_ai_response(prompt) or "You're doing great! Keep going!"

    return game_state, response


# Load sound effects
try:
    score_sound = pygame.mixer.Sound("song.mp3")
    background_sound = pygame.mixer.Sound("song2.mp3")
    background_sound.set_volume(0.5)
except Exception as e:
    print(f"Could not load sound files: {e}")
    score_sound = None
    background_sound = None

def load_gif(path, size=(1280, 720)):
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frame = gif.convert("RGBA").resize(size)
            frames.append(frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


# Load GIFs
gif1_frames = load_gif("gifimg.gif", size=(60, 60))
gif2_frames = load_gif("gifimg2.gif", size=(60, 60))
gif_start_frames = load_gif("gifstart.gif")
gif_end_frames = load_gif("endgif.gif")

current_gif1_frame = 0
current_gif2_frame = 0
start_frame_index = 0
end_frame_index = 0

# Webcam setup
cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Calibration data
x_dist = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 88, 75, 70, 67, 62, 59, 57]
y_cm = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
inv_x = [1 / d for d in x_dist]
coff = np.polyfit(inv_x, y_cm, 1)

# Load top score from file
top_score_file = "top_score.txt"
if os.path.exists(top_score_file):
    with open(top_score_file, "r") as file:
        try:
            top_score = int(file.read())
        except:
            top_score = 0
else:
    top_score = 0

# Colors
light_blue = (178, 102, 255)
light_green = (102, 0, 204)


# Game state
cx, cy = 250, 250
counter = 0
score = 0
totalTime = 20
game_state = 'start'
previous_score = -1
is_background_playing = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    key = cv2.waitKey(1)

    # Handle voice commands
    if not voice_system.listening and game_state != "quit":
        voice_system.start_listening()

    while not voice_system.command_queue.empty():
        command = voice_system.command_queue.get()
        new_state, response = process_voice_command(command, game_state, score, top_score)

        if new_state != game_state:
            game_state = new_state
            if game_state == "playing":
                timeStart = time.time()
                score = 0
                cx, cy = 250, 250
            elif game_state == "quit":
                break

        if response:
            voice_system.speak(response)

    if game_state == "quit":
        break

    # ----------- Start Page ------------
    if game_state == 'start':
        if background_sound and not is_background_playing:
            background_sound.play(-1)
            is_background_playing = True

        frame_pil = gif_start_frames[start_frame_index]
        start_frame_index = (start_frame_index + 1) % len(gif_start_frames)
        frame_np = np.array(frame_pil)
        img = cv2.cvtColor(frame_np, cv2.COLOR_RGBA2BGR)

        cvzone.putTextRect(img, 'Press any key to start', (400, 600), scale=2, offset=10, thickness=3,
                           colorR=light_green)
        cvzone.putTextRect(img, f'Top Score: {top_score}', (50, 50), scale=2, offset=10, colorR=light_green)
        cvzone.putTextRect(img, "Say 'Start game' to begin", (400, 650), scale=1, offset=5, colorR=light_green)

        if key != -1:
            game_state = 'playing'
            timeStart = time.time()
            score = 0
            previous_score = -1
            cx, cy = 250, 250
            counter = 0

    # ----------- Main Game ------------
    elif game_state == 'playing':
        if time.time() - timeStart < totalTime:
            hands, img = detector.findHands(img, draw=False)

            if hands:
                lmList = hands[0]['lmList']
                x, y, w, h = hands[0]['bbox']
                x1, y1, z1 = lmList[5]
                x2, y2, z2 = lmList[17]

                distance = int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
                inv_distance = 1 / distance
                distanceCM = coff[0] * inv_distance + coff[1]

                if distanceCM < 40 and x < cx < x + w and y < cy < y + h:
                    counter = 1

                cvzone.putTextRect(img, f'{int(distanceCM)}cm', (x + 8, y - 10), colorR=light_green)
                cv2.rectangle(img, (x, y), (x + w, y + h), light_blue, 3)

            if counter:
                counter += 1
                if counter == 3:
                    cx = random.randint(100, 1100)
                    cy = random.randint(100, 600)
                    score += 1
                    counter = 0
                    if random.random() < 0.3:
                        feedback = random.choice(["Nice!", "Great job!", "You got it!"])
                        voice_system.speak(feedback)

            if score != previous_score and score_sound:
                score_sound.play()
                previous_score = score

            frames = gif2_frames if counter else gif1_frames
            current_frame = current_gif2_frame if counter else current_gif1_frame

            if counter:
                current_gif2_frame = (current_gif2_frame + 1) % len(gif2_frames)
            else:
                current_gif1_frame = (current_gif1_frame + 1) % len(gif1_frames)

            frame_pil = frames[current_frame]
            frame_np = np.array(frame_pil)
            frame_bgra = cv2.cvtColor(frame_np, cv2.COLOR_RGBA2BGRA)
            b, g, r, a = cv2.split(frame_bgra)
            overlay_image = cv2.merge((b, g, r))

            h, w = overlay_image.shape[:2]
            x1, y1 = cx - w // 2, cy - h // 2
            x2, y2 = x1 + w, y1 + h
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img.shape[1], x2)
            y2 = min(img.shape[0], y2)

            if x1 < x2 and y1 < y2:
                overlay_region = overlay_image[:y2 - y1, :x2 - x1]
                alpha = a[:y2 - y1, :x2 - x1, np.newaxis] / 255.0
                background_roi = img[y1:y2, x1:x2]
                img[y1:y2, x1:x2] = (background_roi * (1 - alpha) + overlay_region * alpha).astype(np.uint8)

            cvzone.putTextRect(img, f'Time: {int(totalTime - (time.time() - timeStart))}', (1000, 75), scale=3,
                               offset=20, colorR=light_green)
            cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (60, 75), scale=3, offset=20, colorR=light_green)
            cvzone.putTextRect(img, f'Top: {str(top_score).zfill(2)}', (60, 150), scale=2, offset=10,
                               colorR=light_green)
            cvzone.putTextRect(img, "Voice: Listening...", (1000, 150), scale=1, offset=5, colorR=light_green)
        else:
            game_state = 'end'

    # ----------- End Page ------------
    elif game_state == 'end':
        frame_pil = gif_end_frames[end_frame_index]
        end_frame_index = (end_frame_index + 1) % len(gif_end_frames)
        frame_np = np.array(frame_pil)
        img = cv2.cvtColor(frame_np, cv2.COLOR_RGBA2BGR)

        cvzone.putTextRect(img, 'Game Over', (580, 350), scale=4, offset=20, thickness=6, colorR=light_green)
        cvzone.putTextRect(img, f'Your Score: {score}', (580, 450), scale=3, offset=20, colorR=light_green)

        if score > top_score:
            top_score = score
            with open(top_score_file, "w") as file:
                file.write(str(top_score))
            voice_system.speak(f"New high score! {score} points! Amazing!")
        else:
            voice_system.speak(f"Game over! You scored {score} points")


        cvzone.putTextRect(img, f'Top Score: {top_score}', (590, 510), scale=2, offset=10, colorR=light_green)
        cvzone.putTextRect(img, 'Press R to restart', (580, 560), scale=2, offset=10, colorR=light_green)
        cvzone.putTextRect(img, "Say 'Restart' to play again", (580, 600), scale=1, offset=5, colorR=light_green)

        if key == ord('r'):
            game_state = 'playing'
            timeStart = time.time()
            score = 0
            previous_score = -1
            cx, cy = 250, 250
            counter = 0
        elif key == ord('q'):
            break

    cv2.imshow("Image", img)

# Clean up
if background_sound and is_background_playing:
    background_sound.stop()
voice_system.stop_listening()
cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()