import tkinter as tk
import os
import sqlite3

from reportlab.pdfgen import canvas
class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("600x400")
        self.master.title("Le app")

        self.create_widgets()
        self.create_database()

    def create_database(self):
        self.conn = sqlite3.connect('app_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                property TEXT
            )
        """)
        self.conn.commit()
        
    def create_widgets(self):
        frame = tk.Frame(self.master)
        frame.pack(anchor="nw", pady=20)

        tk.Label(frame, text="Title:").grid(row=0, column=0, padx=5)
        self.title_entry = tk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Property:").grid(row=1, column=0, padx=5)
        self.property_entry = tk.Entry(frame, width=30)
        self.property_entry.grid(row=1, column=1, padx=5)

        self.saved_label = tk.Label(text="", anchor="w", justify="left")
        self.saved_label.pack(anchor="w")

        #=============PLACE FOR DATABASE THINGY======


        tk.Button(frame,text="Save", command=self.save_data).grid(row=1, column=2, padx=5, pady=10)
        tk.Button(frame, text="Export PDF", command=self.generate_pdf_report).grid(row=3, column=0, padx=5, pady=10)

    def save_data(self):
        title_value = self.title_entry.get()
        property_value = self.property_entry.get()
        self.cursor.execute(
            "INSERT INTO data (title, property) VALUES (?, ?)",
            (title_value, property_value)
        )
        self.conn.commit()

        self.saved_label.config(
            text=f"Saved Data:\nTitle: {title_value}\nProperty: {property_value}"
        )

    def generate_pdf_report(self):
        c = canvas.Canvas("report.pdf")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1, 750, self.title_entry.get())
        c.setFont("Helvetica", 12)
        c.drawString(30, 735, self.property_entry.get())
        c.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()