import tkinter as tk
import os

from reportlab.pdfgen import canvas
class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("600x400")
        self.master.title("Le app")

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Stinky Pinky")
        self.label.pack(pady=20)

        self.generate_pdf_button = tk.Button(
            self.master,
            text="gimme the pdf",
            command=self.generate_pdf_report
        )
        self.generate_pdf_button.pack(pady=10)

    def generate_pdf_report(self):
        c = canvas.Canvas("report.pdf")
        c.drawString(1, 750, "sigma sigma report")
        c.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()