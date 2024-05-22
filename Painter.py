import tkinter as tk

class Painter(tk.Canvas):
    def __init__(self, parent, algo):
        super().__init__(parent)
        self.algo = algo

    def draw(self):
        # Implement the drawing logic based on algo state
        self.delete("all")
        self.create_text(100, 100, text="Drawing drone", fill="black")
