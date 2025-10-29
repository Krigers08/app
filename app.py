import tkinter as tk
import os
import sqlite3

from reportlab.pdfgen import canvas
from tkinter import ttk


class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("600x400")
        self.master.title("Le app")

        self.create_widgets()
        self.create_database()

        self.editing_id = None

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
        self.load_data()

    def create_widgets(self):
        #=============INPUT/FRAME==========
        frame = ttk.Frame(self.master)
        frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Description:").grid(row=1, column=0, sticky="w")
        self.property_entry = ttk.Entry(frame, width=30)
        self.property_entry.grid(row=1, column=1, padx=5)

        self.message_frame = ttk.Frame(self.master)
        self.message_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.message_label = ttk.Label(self.message_frame, text="", anchor="w")
        self.message_label.pack(fill="x")
        #=============DATABASE===============
        self.table = ttk.Treeview(
            self.master,
            columns=("ID", "Title", "Property"),
            show="headings"
        )
        self.table.heading("ID", text="ID")
        self.table.heading("Title", text="Title")
        self.table.heading("Property", text="Description")

        self.table.column("ID", width=35, anchor="center")
        self.table.column("Title", width=200, anchor="sw")
        self.table.column("Property", width=200, anchor="sw")

        self.table.pack(fill='both', expand=True, pady=10, padx=10)

        #==================ACTION BUTTONS==========================

        ttk.Button(frame,text="Save", command=self.save_data).grid(row=0, column=2, padx=5, pady=10)
        ttk.Button(frame, text="Export PDF", command=self.generate_pdf_report).grid(row=3, column=0, padx=5, pady=10,)
        ttk.Button(frame, text="Edit", command=self.edit_data).grid(row=1, column=2, padx=5, pady=10,)
    #================SHOW MESSAGE==========
    def show_message(self, text):
        self.message_label.config(text=text)
        self.message_label.after(3000, lambda: self.message_label.config(text=""))
    
    #================LOAD DATA==========
    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        self.cursor.execute("SELECT * FROM data")
        rows = self.cursor.fetchall()
        for row in rows:
            self.table.insert("", "end", values=row)

    #================EDIT DATA==========
    def edit_data(self):
        selection = self.table.selection()
        if not selection:
            self.show_message("Please select a record to edit.")
            return
        
        item = self.table.item(selection[0])
        self.editing_id = item["values"][0]
        title = item["values"][1]
        description = item["values"][2]

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)
        self.property_entry.delete(0, tk.END)
        self.property_entry.insert(0, description)

        self.show_message(f"Editing record ID {self.editing_id}")
    #================SAVE DATA==========
    def save_data(self):
        title_value = self.title_entry.get().strip()
        property_value = self.property_entry.get().strip()

        if not title_value or not property_value:
            self.show_message("Please fill in all fields.")
            return
        
        if self.editing_id:
            self.cursor.execute(
                "UPDATE data SET title=?, property=? WHERE id=?",
                (title_value, property_value, self.editing_id)
            )
            self.show_message("Data updated successfully.")
            self.editing_id = None
            
        else:
            self.cursor.execute(
                "INSERT INTO data (title, property) VALUES (?, ?)",
                (title_value, property_value)
            )
            self.show_message("Data saved successfully.")
        self.conn.commit()
        self.load_data()

        self.title_entry.delete(0, tk.END)
        self.property_entry.delete(0, tk.END)
    #================PDF REPORTING==========
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