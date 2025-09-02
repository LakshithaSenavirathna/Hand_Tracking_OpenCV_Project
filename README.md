# 🖐️ AI-Powered Hand Tracking Game with Voice Interaction

This project is a fun and interactive **hand-tracking game** built with Python. It combines **computer vision**, **voice control**, and **AI-powered feedback** to offer a dynamic gaming experience. Players use their hands in front of a webcam to hit targets, while a voice assistant provides instructions, encouragement, and tips.

---

##  Demo Video

Watch the gameplay in action!

[![Watch the video](https://img.youtube.com/vi/7E3w-aOlI2o/0.jpg)](https://youtu.be/7E3w-aOlI2o?si=XxVLDZrT3RRulm3l)

---

##  How It Works

1. Launch the game with `game_code.py`.
2. The game begins with an animated intro. Say “Start game” or press any key to start playing.
3. Use your hand to touch targets that appear in the webcam feed.
4. Voice commands like “Score,” “Time,” or “Tip” trigger voice feedback:
   - AI-powered responses (using OpenRouter API)
   - Encouragement and game stats
5. The game tracks and saves your **top score**.
6. Say **“Restart”** after game over or **“Quit”/press Q** to exit.

---

##  Tech Stack

- **Python**
- **OpenCV + CVZone** – Hand detection and tracking  
- **SpeechRecognition + Pyttsx3** – Voice input/output  
- **PyGame** – Sound effects and background music  
- **Pillow (PIL)** – GIF animations  
- **NumPy** – Numeric operations  
- **OpenRouter API** – AI responses (tips/encouragement)

---

##  Installation

```bash
# Clone the project
git clone https://github.com/LakshithaSenavirathna/Hand_Tracking_OpenCV_Project.git
cd Hand_Tracking_OpenCV_Project

Install dependencies

Make sure you have Python installed, and then run:

pip install -r requirements.txt


Your requirements.txt should include:

opencv-python
cvzone
pygame
numpy
pillow
SpeechRecognition
pyttsx3
requests

Add Your OpenRouter API Key

Open game_code.py and update the following line with your API key:

OPENROUTER_API_KEY = "sk-or-your_key_here"

Running the Game
python game_code.py


Gameplay controls:

Start: Press any key or say "Start game"

During play:

Say "Score" to hear your current score

Say "Time" to know how many seconds are left

Say "Tip" or "Encourage" to get AI-driven advice or encouragement

Game Over: Say "Restart", press R to play again; say "Quit" or press Q to exit

Code Structure & Files
├── game_code.py        # Main game script
├── gifstart.gif        # Intro animation
├── gifimg.gif          # Gameplay sprite (small GIF)
├── gifimg2.gif         # Alternate gameplay sprite
├── endgif.gif          # Game over animation
├── song.mp3            # Sound effect for scoring
├── song2.mp3           # Background music
├── top_score.txt       # Stores the highest score
└── requirements.txt    # Required Python libraries
