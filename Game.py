import tkinter as tk
import random
from collections import deque

class ConceptRainGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Concept Rain Game")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f8ff")

        # Game state
        self.score = 0
        self.level = 1
        self.lives = 5
        self.falling_speed = 1.5
        self.spawn_rate = 3000
        self.current_item = None
        self.word_queue = deque()
        self.shown_concepts = []
        self.current_correct_category = None
        self.current_word = None  # Track current word separately

        # Levels and settings
        self.max_level = 5
        self.items_per_level = {i: 5 * i for i in range(1, 6)}
        self.items_spawned = 0

        # Concept categories - only questions visible
        self.concepts = {
            "Data Types": ["Whole number type", "Decimal number type", "Text type", 
                          "True/False type", "Collection type"],
            "Functions": ["Output function", "Input function", "Length function",
                         "Number sequence", "Type check"],
            "Control Flow": ["Conditional", "Loop through items", "Loop while true",
                           "Define function"],
            "Operators": ["Addition", "Subtraction", "Multiplication",
                         "Division", "Equality", "Inequality"]
        }

        # Actual answers mapping
        self.answers = {
            "Whole number type": ("int", "Data Types"),
            "Decimal number type": ("float", "Data Types"),
            "Text type": ("str", "Data Types"),
            "True/False type": ("bool", "Data Types"),
            "Collection type": ("list", "Data Types"),
            "Output function": ("print()", "Functions"),
            "Input function": ("input()", "Functions"),
            "Length function": ("len()", "Functions"),
            "Number sequence": ("range()", "Functions"),
            "Type check": ("type()", "Functions"),
            "Conditional": ("if", "Control Flow"),
            "Loop through items": ("for", "Control Flow"),
            "Loop while true": ("while", "Control Flow"),
            "Define function": ("def", "Control Flow"),
            "Addition": ("+", "Operators"),
            "Subtraction": ("-", "Operators"),
            "Multiplication": ("*", "Operators"),
            "Division": ("/", "Operators"),
            "Equality": ("==", "Operators"),
            "Inequality": ("!=", "Operators")
        }

        self.setup_ui()
        self.running = True
        self.start_game()

    def setup_ui(self):
        # Canvas for falling words
        self.canvas = tk.Canvas(self.root, width=900, height=500, bg="#d0f0ff", highlightthickness=0)
        self.canvas.pack()

        # Info labels
        info_frame = tk.Frame(self.root, bg="#f0f8ff")
        info_frame.pack(fill=tk.X, pady=10)

        self.score_label = tk.Label(info_frame, text="Score: 0", font=("Arial", 14), bg="#f0f8ff", fg="green")
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(info_frame, text="Level: 1", font=("Arial", 14), bg="#f0f8ff", fg="blue")
        self.level_label.pack(side=tk.LEFT, padx=20)

        self.lives_label = tk.Label(info_frame, text="Lives: ❤️ x 5", font=("Arial", 14), bg="#f0f8ff", fg="red")
        self.lives_label.pack(side=tk.RIGHT, padx=20)

        # Frame for category buttons
        self.option_frame = tk.Frame(self.root, bg="#f0f8ff", height=120)
        self.option_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        # Instruction label
        tk.Label(self.option_frame, 
                text="Select the category that matches the falling term:", 
                font=("Arial", 12), 
                bg="#f0f8ff").pack()

        # Try Again button (initially hidden)
        self.try_again_btn = tk.Button(
            self.root, 
            text="Try Again", 
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.reset_game
        )
        self.try_again_btn.pack_forget()

        # Answer reveal label (hidden initially)
        self.answer_label = tk.Label(
            self.canvas,
            text="",
            font=("Arial", 12),
            bg="#d0f0ff"
        )

    def start_game(self):
        self.game_loop()
        self.root.after(self.spawn_rate, self.spawn_word)

    def spawn_word(self):
        if not self.running:
            return
        if self.items_spawned >= self.items_per_level[self.level]:
            return

        # Select a random question (not answer)
        question = random.choice(list(self.answers.keys()))
        self.word_queue.append(question)
        
        if self.current_item is None and self.word_queue:
            self.create_falling_item(self.word_queue.popleft())

        self.items_spawned += 1
        self.root.after(self.spawn_rate, self.spawn_word)

    def create_falling_item(self, question):
        if self.current_item is not None:
            return

        x = random.randint(150, 750)
        rect = self.canvas.create_rectangle(
            x - 80, 0, x + 80, 40, 
            fill=random.choice(["#ff9999", "#99ccff", "#ccffcc"]),
            outline="black", width=2
        )
        text = self.canvas.create_text(
            x, 20, 
            text=question,  # Show only the question
            font=("Arial", 12, "bold")
        )

        self.current_item = {
            "rect": rect,
            "text": text,
            "question": question,
            "x": x,
            "y": 20
        }

        # Store the correct answer and category
        self.current_word, self.current_correct_category = self.answers[question]
        self.shown_concepts.append((self.current_word, self.current_correct_category))
        self.show_options()

    def show_options(self):
        # Clear previous buttons (keep first child which is the instruction label)
        for widget in self.option_frame.winfo_children()[1:]:
            widget.destroy()

        all_categories = list(self.concepts.keys())
        wrong_choices = [c for c in all_categories if c != self.current_correct_category]
        
        # Select 3 wrong options + correct one
        options = random.sample(wrong_choices, 3) + [self.current_correct_category]
        random.shuffle(options)

        button_frame = tk.Frame(self.option_frame, bg="#f0f0ff")
        button_frame.pack(pady=5)

        for cat in options:
            btn = tk.Button(
                button_frame,
                text=cat,
                font=("Arial", 12, "bold"),
                bg="#8888ff",  # All buttons same color initially
                fg="white",
                width=15,
                height=2,
                command=lambda c=cat: self.check_answer(c)
            )
            btn.pack(side=tk.LEFT, padx=10, pady=5)

    def check_answer(self, selected_category):
        if self.current_item is None:
            return

        # Show the actual answer before giving feedback
        x, y = self.current_item["x"], self.current_item["y"]
        self.canvas.itemconfig(self.current_item["text"], text=self.current_word)
        
        if selected_category == self.current_correct_category:
            self.score += 10
            self.score_label.config(text=f"Score: {self.score}")
            self.flash_item(self.current_item, "green")
            self.root.after(300, self.remove_current_item)
            
            if self.items_spawned >= self.items_per_level[self.level] and len(self.word_queue) == 0:
                self.root.after(500, self.next_level)
        else:
            self.flash_item(self.current_item, "red")
            self.root.after(300, self.lose_life)

    def flash_item(self, item, color):
        self.canvas.itemconfig(item["rect"], fill=color)
        self.root.after(200, lambda: self.canvas.itemconfig(
            item["rect"], 
            fill=random.choice(["#ff9999", "#99ccff", "#ccffcc"])
        ))

    def remove_current_item(self):
        if self.current_item:
            self.canvas.delete(self.current_item["rect"])
            self.canvas.delete(self.current_item["text"])
            self.current_item = None
            self.current_word = None
            
            if self.word_queue:
                self.create_falling_item(self.word_queue.popleft())

    def game_loop(self):
        if not self.running:
            return

        if self.current_item:
            self.canvas.move(self.current_item["rect"], 0, self.falling_speed)
            self.canvas.move(self.current_item["text"], 0, self.falling_speed)
            self.current_item["y"] += self.falling_speed

            if self.current_item["y"] > 480:
                self.lose_life()

        self.root.after(30, self.game_loop)

    def lose_life(self):
        if self.current_item:
            # Reveal the answer before removing
            self.canvas.itemconfig(self.current_item["text"], text=self.current_word)
            self.root.after(500, lambda: [
                self.canvas.delete(self.current_item["rect"]),
                self.canvas.delete(self.current_item["text"]),
                self.set_current_item_none()
            ])

        self.lives -= 1
        self.lives_label.config(text=f"Lives: ❤️ x {self.lives}")
        
        if self.lives <= 0:
            self.end_game(win=False)
        elif self.word_queue:
            self.root.after(600, lambda: self.create_falling_item(self.word_queue.popleft()))

    def set_current_item_none(self):
        self.current_item = None
        self.current_word = None

    def next_level(self):
        if self.level >= self.max_level:
            self.end_game(win=True)
            return

        self.level += 1
        self.level_label.config(text=f"Level: {self.level}")
        self.falling_speed += 0.5
        self.spawn_rate = max(1000, self.spawn_rate - 300)
        self.items_spawned = 0
        self.word_queue.clear()

        self.canvas.delete("all")
        self.root.after(self.spawn_rate, self.spawn_word)

    def end_game(self, win=False):
        self.running = False
        self.canvas.delete("all")
        
        # Clear option buttons but keep the instruction label
        for widget in self.option_frame.winfo_children()[1:]:
            widget.destroy()

        # Show game result
        result_text = "🎉 YOU WIN! 🎉" if win else "Game Over"
        result_color = "green" if win else "red"
        self.canvas.create_text(450, 150, text=result_text, fill=result_color, font=("Arial", 40, "bold"))
        self.canvas.create_text(450, 210, text=f"Final Score: {self.score}", fill="black", font=("Arial", 24))

        # Show learned concepts in unordered list
        summary = {}
        for word, cat in self.shown_concepts:
            summary.setdefault(cat, []).append(word)

        y = 260
        self.canvas.create_text(450, y, text="📘 What You Learned:", font=("Arial", 18, "bold"), fill="blue")
        y += 40
        
        # Create a frame to hold the list items
        list_frame = tk.Frame(self.canvas, bg="#d0f0ff")
        self.canvas.create_window(450, y+100, window=list_frame, width=800)
        
        # Add list items with bullet points
        for cat, words in summary.items():
            tk.Label(list_frame, 
                    text=f"• {cat}:", 
                    font=("Arial", 12, "bold"), 
                    bg="#d0f0ff", 
                    anchor="w").pack(anchor="w", padx=20)
            for word in words:
                tk.Label(list_frame, 
                        text=f"  → {word}", 
                        font=("Arial", 11), 
                        bg="#d0f0ff", 
                        anchor="w").pack(anchor="w", padx=40)

        # Show Try Again button
        self.try_again_btn.pack(pady=20)

    def reset_game(self):
        # Hide Try Again button
        self.try_again_btn.pack_forget()
        
        # Reset game state
        self.score = 0
        self.level = 1
        self.lives = 5
        self.falling_speed = 1.5
        self.spawn_rate = 3000
        self.current_item = None
        self.current_word = None
        self.word_queue.clear()
        self.shown_concepts = []
        self.items_spawned = 0
        
        # Update UI
        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 1")
        self.lives_label.config(text="Lives: ❤️ x 5")
        
        # Clear canvas and restart
        self.canvas.delete("all")
        self.running = True
        self.start_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = ConceptRainGame(root)
    root.mainloop()