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
        self.master.title("Price tag generator")

        self.pvn_rates = ["21%", "12%", "5%"]
        self.unit_types = ["Gb", "Kg", "L", "M"]

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
                price REAL,
                pvn_percent TEXT,
                pvn_price REAL,
                origin TEXT,
                barcode TEXT,
                unit_type TEXT
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
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Price:").grid(row=1, column=0, sticky="w")
        self.price_entry = ttk.Entry(frame, width=30)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="PVN Rate:").grid(row=2, column=0, sticky="w")
        self.pvn_var = tk.StringVar(value="21%")
        self.pvn_dropdown = ttk.Combobox(frame, textvariable=self.pvn_var, values=self.pvn_rates, state="readonly", width=28)
        self.pvn_dropdown.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Unit Type:").grid(row=3, column=0, sticky="w")
        self.unit_type_var = tk.StringVar(value="Kg")
        self.unit_type_entry = ttk.Combobox(frame, textvariable=self.unit_type_var, values=self.unit_types, state="readonly", width=28)
        self.unit_type_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Origin:").grid(row=5, column=0, sticky="w")
        self.origin_entry = ttk.Entry(frame, width=30)
        self.origin_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Barcode:").grid(row=6, column=0, sticky="w")
        self.barcode_entry = ttk.Entry(frame, width=30)
        self.barcode_entry.grid(row=6, column=1, padx=5, pady=5)

        self.message_label = ttk.Label(frame, text="", anchor="w")
        self.message_label.grid(row=0, column=3, padx=(10, 0), sticky="w")
        
        #=============DATABASE===============
        self.table = ttk.Treeview(
            self.master,
            columns=("ID", "Title", "Price", "PVN_Percent", "PVN_Price", "Origin", "Barcode", "Unit_Type"),
            show="headings"
        )
        self.table.heading("ID", text="ID")
        self.table.heading("Title", text="Title")
        self.table.heading("Price", text="Price")
        self.table.heading("PVN_Percent", text="PVN Percent")
        self.table.heading("PVN_Price", text="PVN Price")
        self.table.heading("Origin", text="Origin")
        self.table.heading("Barcode", text="Barcode")
        self.table.heading("Unit_Type", text="Unit Type")

        self.table.column("ID", width=69, anchor="center")
        self.table.column("Title", width=200, anchor="center")
        self.table.column("Price", width=100, anchor="center")
        self.table.column("PVN_Percent", width=100, anchor="center")
        self.table.column("PVN_Price", width=100, anchor="center")
        self.table.column("Origin", width=100, anchor="center")
        self.table.column("Barcode", width=100, anchor="center")
        self.table.column("Unit_Type", width=100, anchor="center")

        self.table.pack(fill='both', expand=True, pady=10, padx=10)


        #==================ACTION BUTTONS==========================


        ttk.Button(frame,text="Save", command=self.save_data).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Edit", command=self.edit_data).grid(row=1, column=2, padx=5)
        ttk.Button(frame, text="Delete", command=self.delete_data).grid(row=2, column=2, padx=5)

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

        self.cursor.execute("select ID, Title, Price, PVN_Percent, PVN_Price, Origin, Barcode, Unit_Type from data")
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
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, item["values"][1])

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, item["values"][2])

        self.origin_entry.delete(0, tk.END)
        self.origin_entry.insert(0, item["values"][5])

        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.insert(0, item["values"][6])

        self.unit_type_entry.set(item["values"][7])

        self.show_message(f"Editing record ID {self.editing_id}")
    #================SAVE DATA==========
    def save_data(self):

        title_entry_value = self.title_entry.get().strip()
        price_entry_value = self.price_entry.get().strip().replace(',', '.')
        pvn_var_value = self.pvn_var.get()

        price_value = float(price_entry_value)
        
        pvn_percent = self.pvn_var.get()
        pvn_rate = float(pvn_percent.strip('%')) / 100
        pvn_price_value = round(price_value * (1 + pvn_rate), 2)

        origin_entry_value = self.origin_entry.get().strip()
        barcode_entry_value = self.barcode_entry.get().strip()
        unit_type_entry_value = self.unit_type_entry.get().strip()

        if not title_entry_value or not origin_entry_value or not barcode_entry_value or not unit_type_entry_value: 
            self.show_message("Please fill in all fields.")
            return

        if self.editing_id:
            self.cursor.execute(
                "UPDATE data SET title=?, price=?, pvn_percent=?, pvn_price=?, origin=?, barcode=?, unit_type=? WHERE id=?",
                (title_entry_value, price_value, pvn_var_value, pvn_price_value, origin_entry_value, barcode_entry_value, unit_type_entry_value, self.editing_id)
            )
            self.show_message("Data updated successfully.")
            self.editing_id = None

        else:
            self.cursor.execute(
                "INSERT INTO data (title, price, pvn_percent, pvn_price, origin, barcode, unit_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title_entry_value, price_value, pvn_var_value, pvn_price_value, origin_entry_value, barcode_entry_value, unit_type_entry_value)
            )
            self.show_message("Data saved successfully.")
        self.conn.commit()
        self.load_data()

        self.title_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.origin_entry.delete(0, tk.END)
        self.barcode_entry.delete(0, tk.END)
        self.unit_type_entry.set('Kg')
        self.pvn_var.set("21%")

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