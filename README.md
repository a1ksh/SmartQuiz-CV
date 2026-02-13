# SmartQuiz-CV

A Python-based interactive quiz application using OpenCV and MediaPipe for hand gesture control. Questions are fetched from SQLite database.

**Tags:** `python`, `opencv`, `computer-vision`, `hand-tracking`, `tkinter`, `sqlite`.


### How to Play:
1. **Start:** Click the "START" button to begin.
2. **Answering:** Show your fingers to the camera to select an answer:
    * ☝️ **1 finger:** Option 1
    * ✌️ **2 fingers:** Option 2
    * 🤟 **3 fingers:** Option 3
    * 🖖 **4 fingers:** Option 4

### Key Settings:
* **Wait:** There is a short delay (4 seconds) between answers to prevent accidental double-clicks.
* **Timer:** You have 20 seconds to answer each question.
