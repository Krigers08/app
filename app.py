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
        frame = tk.Frame(self.master)
        frame.pack(anchor="nw", pady=20)

        tk.Label(frame, text="Title:").grid(row=0, column=0, padx=5)
        self.title_entry = tk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Button(frame, text="Export PDF", command=self.generate_pdf_report).grid(row=0, column=2, padx=5)


    def generate_pdf_report(self):
        c = canvas.Canvas("report.pdf")
        c.drawString(1, 750, self.title_entry.get())
        c.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()