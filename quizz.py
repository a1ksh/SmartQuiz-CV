import tkinter as tk
from tkinter import font as tkFont, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import sqlite3
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time


class QuizApp:
    def load_questions_from_db(self):
        """Викторинаның сұрақтарын мәліметтер қорынан жүктеу"""
        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        cursor.execute("SELECT question, option1, option2, option3, option4, correct_answer FROM questions")
        data = cursor.fetchall()

        self.questions = []
        self.answers = []
        self.correct_answers = []

        for row in data:
            self.questions.append(row[0])
            self.answers.append([row[1], row[2], row[3], row[4]])
            self.correct_answers.append(row[5])
        conn.close()

    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("1024x768")
        self.root.configure(bg="#2E3440")

        self.questions = []
        self.answers = []
        self.correct_answers = []
        self.load_questions_from_db()

        self.current_question = 0
        self.score = 0

        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(detectionCon=0.8, maxHands=2)

        self.font_path = "arial.ttf"
        self.start_time = None
        self.answer_time_limit = 20
        self.last_answer_time = 0
        self.min_time_between_answers = 4
        self.quiz_finished = False
        self.selected_index = None

        self.start_frame = tk.Frame(self.root, bg="#2E3440", width=1024, height=768)
        self.quiz_frame = tk.Frame(self.root, bg="#2E3440", width=1024, height=768)
        self.result_frame = tk.Frame(self.root, bg="#2E3440", width=1024, height=768)

        self.show_start_screen()

    def show_start_screen(self):
        self.quiz_frame.pack_forget()
        self.result_frame.pack_forget()
        self.start_frame.pack(fill=tk.BOTH, expand=True)

        try:
            image = Image.open("image.png")
            image = image.resize((1024, 768), Image.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(image)

            background_label = tk.Label(self.start_frame, image=bg_image)
            background_label.place(relwidth=1, relheight=1)
            background_label.image = bg_image
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            self.start_frame.configure(bg="#4C566A")
        button_font = tkFont.Font(family="Helvetica", size=18, weight="bold")

        self.start_button = tk.Button(
            self.start_frame,
            text="START",
            command=self.start_quiz,
            font=button_font,
            bg="#FFD44C",
            fg="#000000",
            activebackground="#FFDC4F",
            activeforeground="#000000",
            borderwidth=0,
            highlightthickness=0,
            padx=70,
            pady=25,
            relief="flat"
        )
        self.start_button.configure(cursor="hand2", bd=0, highlightbackground="#FFD44C", highlightthickness=0)
        self.start_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

    def start_quiz(self):
        """Викторинаны іске қосады"""
        self.start_frame.pack_forget()
        self.result_frame.pack_forget()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self.quiz_started = True
        self.current_question = 0
        self.score = 0
        self.start_time = time.time()
        self.last_answer_time = time.time()
        self.video_label = tk.Label(self.quiz_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        self.update_frame()

    def check_answer(self, choice):
        """Таңдалған жауапты тексереді"""
        if time.time() - self.last_answer_time < self.min_time_between_answers:
            return
        if 0 <= choice < 4:
            if self.correct_answers[self.current_question] == choice + 1:
                self.score += 1
            self.current_question += 1
            self.selected_index = None
            if self.current_question >= len(self.questions):
                self.quiz_finished = True
                self.show_result()
                return
            self.start_time = time.time()
            self.last_answer_time = time.time()

    def draw_text(self, img, text, position, font_size=30, color=(255, 255, 255)):
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype(self.font_path, font_size, encoding='unic')
        draw.text(position, text, font=font, fill=color)
        return np.array(img_pil)

    def show_result(self):
        """Викторина нәтижесін көрсетеді"""
        self.video_label.pack_forget()
        self.quiz_frame.pack_forget()
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        try:
            result_image = Image.open("backgd.jpg")
            result_image = result_image.resize((1024, 768), Image.Resampling.LANCZOS)
            result_bg_image = ImageTk.PhotoImage(result_image)

            background_label = tk.Label(self.result_frame, image=result_bg_image)
            background_label.place(relwidth=1, relheight=1)
            background_label.image = result_bg_image
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            self.result_frame.configure(bg="#4C566A")

        percentage = (self.score / len(self.questions)) * 100


        if percentage < 50:
            result_text = "Көбірек тырысыңыз! 😔"
        elif percentage < 75:
            result_text = "Жақсы! 😊"
        elif percentage < 95:
            result_text = "Керемет! 😄"
        else:
            result_text = "Гениально! 🎉"

        result_label = tk.Label(
            self.result_frame,
            text=f"Тест аякталды!\nСіздің нәтижеңіз: {self.score} / {len(self.questions)}\nПроцент: {int(percentage)}%",
            font=("Helvetica", 28),
            bg="#ffffff",
            fg="#000000"
        )

        result_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)


        style = ttk.Style()
        style.configure("TProgressbar", thickness=20)
        progress = ttk.Progressbar(
            self.result_frame,
            orient="horizontal",
            length=500,
            mode="determinate",
            style="TProgressbar"
        )
        progress['value'] = percentage
        progress.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        comment_label = tk.Label(
            self.result_frame,
            text=result_text,
            font=("Helvetica", 24),
            bg="#ffffff",
            fg="#000000"
        )
        comment_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)


        close_button = tk.Button(
            self.result_frame,
            text="Жабу",
            command=self.root.destroy,
            font=("Helvetica", 18),
            bg="#FFD44C",
            fg="#000000",
            activebackground="#FFDC4F",
            activeforeground="#000000",
            borderwidth=0,
            highlightthickness=0,
            padx=70,
            pady=25,
            relief="flat"
        )
        close_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def update_frame(self):
        """Квиз экранындағы кадрды жаңартады"""
        if not self.quiz_started:
            return
        if self.quiz_finished:
            return
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.flip(img, 1)
        hands, img = self.detector.findHands(img)
        overlay = np.zeros((768, 1024, 3), dtype=np.uint8)

        img_resized = cv2.resize(img, (1024, 500))
        overlay[:500, :] = img_resized

        cv2.rectangle(overlay, (0, 500), (1024, 768), (0, 0, 139), -1)
        overlay = self.draw_text(overlay, self.questions[self.current_question], (20, 520), font_size=24)
        for i, ans in enumerate(self.answers[self.current_question]):
            text = f"{i+1}: {ans}"
            pos = (20, 560 + i * 40)
            overlay = self.draw_text(overlay, text, pos, font_size=24)
            if self.selected_index is not None and self.selected_index == i:
                cv2.rectangle(overlay, (pos[0]-10, pos[1]-10), (pos[0]+600, pos[1]+30), (0, 255, 255), 2)

        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)))
        self.video_label.config(image=img_tk)
        self.video_label.image = img_tk

        if time.time() - self.start_time > self.answer_time_limit:
            self.current_question += 1
            self.selected_index = None
            if self.current_question >= len(self.questions):
                self.quiz_finished = True
                self.show_result()
                return
            self.start_time = time.time()


        if hands:
            hand = hands[0]
            fingers = self.detector.fingersUp(hand)
            finger_count = sum(fingers)
            if finger_count in [1, 2, 3, 4]:
                self.selected_index = finger_count - 1
                if time.time() - self.last_answer_time >= self.min_time_between_answers:
                    self.check_answer(self.selected_index)
                    self.selected_index = None

        self.root.after(10, self.update_frame)


root = tk.Tk()
app = QuizApp(root)
root.mainloop()