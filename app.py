import tkinter as tk
import sqlite3

from reportlab.pdfgen import canvas
from tkinter import ttk, StringVar
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1080x720")
        self.master.title("Task Manager")

        self.create_widgets()
        self.create_database()

        self.editing_id = None

    #================MAIN DATABASE==========
    def create_database(self):
        self.conn = sqlite3.connect('app_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                property TEXT,
                price REAL,
                pvn_price REAL,
                quantity INTEGER,
                origin TEXT        
            )
        """)
        self.conn.commit()
        self.load_data()
        self.create_pvn_database()

    #================PVN DATABASE==========
    def create_pvn_database(self):
        conn = sqlite3.connect('pvn_rates.db')
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS pvn_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property TEXT UNIQUE,
                rate REAL
            )
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO pvn_rates (property, rate) VALUES
            ('Regular', 0.21),
            ('Foods', 0.12),
            ('Special', 0.05)
        """)

        conn.commit()
        conn.close()

    def create_widgets(self):
        #=============INPUT/FRAME==========
        frame = ttk.Frame(self.master)
        frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Product Type:").grid(row=1, column=0, sticky="w")
        self.property_var = StringVar()

        self.property_combo = ttk.Combobox(
            frame,
            textvariable=self.property_var,
            values=["Regular","Foods","Special"],
            state="readonly",
            width=27
        )

        self.property_combo.grid(row=1, column=1, padx=5)
        self.property_combo.set("Regular") 

        ttk.Label(frame, text="Price:").grid(row=2, column=0, sticky="w")
        self.price_entry = ttk.Entry(frame, width=30)
        self.price_entry.grid(row=2, column=1, padx=5)

        ttk.Label(frame, text="Quantity:").grid(row=3, column=0, sticky="w")
        self.quantity_entry = ttk.Entry(frame, width=30)
        self.quantity_entry.grid(row=3, column=1, padx=5)

        ttk.Label(frame, text="Origin:").grid(row=4, column=0, sticky="w")
        self.origin_entry = ttk.Entry(frame, width=30)
        self.origin_entry.grid(row=4, column=1, padx=5)

        self.message_label = ttk.Label(frame, text="", anchor="w")
        self.message_label.grid(row=0, column=3, padx=(10, 0), sticky="w")
        
        #=============DATABASE===============
        self.table = ttk.Treeview(
            self.master,
            columns=("ID", "Title", "Property", "Price", "PVN_Price", "Quantity", "Origin"),
            show="headings"
        )
        self.table.heading("ID", text="ID")
        self.table.heading("Title", text="Title")
        self.table.heading("Property", text="Category")
        self.table.heading("Price", text="Price")
        self.table.heading("PVN_Price", text="PVN Price")
        self.table.heading("Quantity", text="Quantity")
        self.table.heading("Origin", text="Origin")

        self.table.column("ID", width=69, anchor="center")
        self.table.column("Title", width=200, anchor="center")
        self.table.column("Property", width=140, anchor="center")
        self.table.column("Price", width=100, anchor="center")
        self.table.column("PVN_Price", width=100, anchor="center")
        self.table.column("Quantity", width=100, anchor="center")
        self.table.column("Origin", width=100, anchor="center")

        self.table.pack(fill='both', expand=True, pady=10, padx=10)


        #==================ACTION BUTTONS==========================


        ttk.Button(frame,text="Save", command=self.save_data).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Edit", command=self.edit_data).grid(row=1, column=2, padx=5)
        ttk.Button(frame, text="Delete", command=self.delete_data).grid(row=2, column=2, padx=5)
        self.property_combo.grid(row=1, column=1, padx=5)

        export_frame = ttk.Frame(self.master)
        export_frame.pack(pady=5, padx=10, anchor="center")
        ttk.Button(export_frame, text="Export PDF", command=self.generate_pdf_report).grid(row=5, column=0, padx=0)
    #================SHOW MESSAGE==========
    def show_message(self, text):
        self.message_label.config(text=text)
        self.message_label.after(5000, lambda: self.message_label.config(text=""))
    
    #================LOAD DATA==========
    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        self.cursor.execute("select id, title, property, price, pvn_price, quantity, origin from data")
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
        price = item["values"][3]
        quantity = item["values"][5]
        origin = item["values"][6]

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)
        self.property_var.set(description)
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, price)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, quantity)
        self.origin_entry.delete(0, tk.END)
        self.origin_entry.insert(0, origin)

        self.show_message(f"Editing record ID {self.editing_id}")
    #================SAVE DATA==========
    def save_data(self):
        title_value = self.title_entry.get().strip()
        property_value = self.property_var.get().strip()
         
        price_user = self.price_entry.get().strip().replace(',', '.')
        if not price_user:
            self.show_message("Please enter a price.")
            return
        price_value = float(price_user)

        quantity_value = self.quantity_entry.get().strip()
        origin_value = self.origin_entry.get().strip()
        if origin_value:
            origin_value = origin_value[0].upper() + origin_value[1:].lower()

        pvn_conn = sqlite3.connect('pvn_rates.db')
        pvn_cursor = pvn_conn.cursor()
        pvn_cursor.execute("SELECT rate FROM pvn_rates WHERE property=?", (property_value,))
        pvn_rate = pvn_cursor.fetchone()[0]
        pvn_conn.close()

        price_with_pvn = round(price_value * (1 + pvn_rate), 2)
        #added_pvn = price_with_pvn - price_value

        if not title_value or not property_value or not quantity_value or not origin_value: 
            self.show_message("Please fill in all fields.")
            return
        
        if not price_value or price_value <= 0:
            self.show_message("Price must be greater than zero.")
            return
        if self.editing_id:
            self.cursor.execute(
                "UPDATE data SET title=?, property=?, price=?, pvn_price=?, quantity=?, origin=? WHERE id=?",
                (title_value, property_value, price_value, price_with_pvn, quantity_value, origin_value, self.editing_id)
            )
            self.show_message("Data updated successfully.")
            self.editing_id = None

        else:
            self.cursor.execute(
                "INSERT INTO data (title, property, price, pvn_price, quantity, origin) VALUES (?, ?, ?, ?, ?, ?)",
                (title_value, property_value, price_value, price_with_pvn, quantity_value, origin_value)
            )
            self.show_message("Data saved successfully.")
        self.conn.commit()
        self.load_data()

        self.title_entry.delete(0, tk.END)
        self.property_var.set("Regular")
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.origin_entry.delete(0, tk.END)

    #================DELETE DATA==========
    def delete_data(self):
        selection = self.table.selection()
        if not selection:
            self.show_message("Please select a record to delete.")
            return
        item = self.table.item(selection[0])
        record_id = item["values"][0]
        self.cursor.execute("DELETE FROM data WHERE id=?", (record_id,))
        self.conn.commit()

        self.load_data()
        self.show_message(f"Item {record_id} deleted successfully.")

    #================PDF REPORTING==========
    def generate_pdf_report(self):
        c = canvas.Canvas("report.pdf", pagesize=A4)
        width, height = A4

        y = height - 1 * inch
        c.setFont("Helvetica-Bold", 18)
        c.drawString(1 * inch, y, "Product Report")

        y -= 0.5 * inch

        self.cursor.execute("SELECT title, property, price FROM data")
        rows = self.cursor.fetchall()

        for title, property_value, price in rows:
            if y < 1 * inch:
                c.showPage()
                y = height - 1 * inch

            c.setFont("Helvetica-Bold", 14)
            c.drawString(1 * inch, y, str(title))

            y -= 0.25 * inch
            c.setFont("Helvetica", 12)
            c.drawString(1.2 * inch, y, f"Type: {property_value}")

            y -= 0.25 * inch
            c.drawString(1.2 * inch, y, f"Price: {price} €")

            y -= 0.4 * inch

        c.save()
        self.show_message("PDF created as report.pdf")
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()