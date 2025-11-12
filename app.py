import tkinter as tk
import sqlite3

from reportlab.pdfgen import canvas
from tkinter import ttk
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.graphics.barcode import eanbc
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DejaVuSansBook", "dejavu-sans.book.ttf"))

#================PDF GENERATOR==========
class PDFGenerator:
    def __init__(self, filename="test.pdf", page_size=landscape(A4), cols=3, rows=3, margin_mm=5, gutter_mm=0):
        self.filename = filename
        self.page_size = page_size
        self.cols = cols
        self.rows = rows
        self.margin = margin_mm * mm + 4 * mm
        self.gutter = gutter_mm * mm
        self.title_font = "DejaVuSansBook"

    def create(self, items):
        #========CREATE BOXES==========
        c = canvas.Canvas(self.filename, pagesize=self.page_size)
        page_w, page_h = self.page_size

        card_w = (page_w - 6 * self.margin - (self.cols - 1) * self.gutter) / self.cols
        card_h = (page_h - 6 * self.margin - (self.rows - 1) * self.gutter) / self.rows * 0.65
        padding = 4 * mm

        for i, (title, final_price, barcode, origin, unit_type) in enumerate(items):
            col = i % self.cols
            row = (i // self.cols) % self.rows
            if i and col == 0 and row == 0:
                c.showPage()

            x = self.margin + col * (card_w + self.gutter)
            y = page_h - self.margin - (row + 1) * card_h - (row * self.gutter)

            c.setDash(3, 2)
            c.rect(x, y, card_w, card_h)
            c.setDash()

            #=========TITLE=========
            max_title_width = card_w - 2 * padding
            title_font_size = self.get_fitting_font_size(c, title, max_title_width, max_font_size=12, min_font_size=6)
            title_y = y - padding + card_h - padding / title_font_size
            c.setFont(self.title_font, title_font_size)
            c.drawString(x + padding, title_y, title)
            c.setFont("DejaVuSansBook", 32)

            #=========PRICE=========
            price_y = title_y - card_h / 3
            price_text = f"€ {final_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            c.drawCentredString(x + card_w / 1.5, price_y, price_text)

            #=========BARCODE=========
            barcode_area_y = y + padding + 0
            if origin.strip():
                c.setFont("DejaVuSansBook", 9)
                c.drawString(x + padding, barcode_area_y + 32, origin.strip())
            try:
                ean_code = ''.join(filter(str.isdigit, barcode.strip()))
                if len(ean_code) != 12:
                    raise ValueError(f"Invalid EAN-13 data: '{barcode}'")
                bc = eanbc.Ean13BarcodeWidget(ean_code, barHeight=10*mm)

                barcode_drawing = Drawing(0, 0)
                barcode_drawing.add(bc)

                bw = bc.width
                max_bw = card_w * padding
                scale = min(1.1, max_bw / bw)

                c.saveState()
                c.translate(x - 7 + padding, barcode_area_y)
                c.scale(scale, 1.0)
                renderPDF.draw(barcode_drawing, c, 0, 0)
                c.restoreState()

            except Exception as e:
                print(f"Error creating barcode for '{barcode}': {e}")
                c.rect(x + padding, barcode_area_y, 60, 30)


            #=======UNIT INFO=========
            unit = (unit_type or "").strip()
            c.setFont("DejaVuSansBook", 8)
            c.drawRightString(x + card_w - padding, y + padding + 15, f"Mērvienība: {unit}")
            c.drawRightString(x + card_w - padding, y + padding + 5, "Mērvienības cena:")
            c.drawRightString(x + card_w - padding, y + padding - 5, f"{final_price:.2f}€/{unit}")

        c.save()

    def get_fitting_font_size(self, c, text, max_width, max_font_size=11, min_font_size=5):
        size = max_font_size
        while size >= min_font_size:
            if c.stringWidth(text, self.title_font, size) <= max_width:
                return size
            size -= 1
        return min_font_size
    

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1080x720")
        self.master.title("Price tag generator")

        self.pvn_rates = ["21%", "12%", "5%"]
        self.unit_types = ["gb", "kg", "L", "M"]

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
        label = ttk.Label(self.master, text="Product Information", font=("Segoe UI", 10, "bold"))
        label.pack(anchor="w", padx=12, pady=(5, 0))

        frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        frame.pack(pady=(0,10), padx=10, fill='x', ipadx=8, ipady=8)

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
        self.unit_type_var = tk.StringVar(value="kg")
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

        self.table.column("ID", width=50, anchor="center")
        self.table.column("Title", width=280, anchor="center")
        self.table.column("Price", width=120, anchor="center")
        self.table.column("PVN_Percent", width=100, anchor="center")
        self.table.column("PVN_Price", width=110, anchor="center")
        self.table.column("Origin", width=110, anchor="center")
        self.table.column("Barcode", width=150, anchor="center")
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
        self.message_label.config(text=text, font=("Helvetica", 11))
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

        self.pvn_var.set(item["values"][3])

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

        if not price_entry_value:
            self.show_message("Please fill in all fields.")
            return
        
        price_value = float(price_entry_value)
        
        pvn_percent = self.pvn_var.get()
        pvn_rate = float(pvn_percent.strip('%')) / 100
        pvn_price_value = round(price_value * (1 + pvn_rate), 2)

        origin_entry_value = self.origin_entry.get().strip().title()
        barcode_entry_value = self.barcode_entry.get().strip()
        unit_type_entry_value = self.unit_type_entry.get().strip()


        if not title_entry_value or not price_entry_value or not origin_entry_value or not barcode_entry_value or not unit_type_entry_value: 
            self.show_message("Please fill in all fields.")
            return

        if len(barcode_entry_value) != 12 or not barcode_entry_value.isdigit():
            self.show_message("Barcode must be exactly 12 digits.")
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
        self.unit_type_entry.set('kg')
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
        self.cursor.execute("SELECT title, pvn_price, barcode, origin, unit_type FROM data")
        items = self.cursor.fetchall()
        pdf = PDFGenerator(filename="test.pdf", cols=3, rows=3, margin_mm=5, gutter_mm=0)
        pdf.create(items)
        self.show_message("PDF grid layout created.")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()