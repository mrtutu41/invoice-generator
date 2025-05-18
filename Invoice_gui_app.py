import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import sqlite3
import os
import pytesseract
from PIL import ImageGrab
import pyautogui
from datetime import datetime

# Configure Tesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Database setup
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        date TEXT,
        company_name TEXT,
        company_address TEXT,
        client_name TEXT,
        items TEXT,
        total REAL
    )
""")
conn.commit()

root = tk.Tk()
root.title("Invoice Generator")
root.geometry("850x650")
root.configure(bg="#f5f5f5")

data_entries = []

# --- Header ---
header = tk.Label(root, text="🧾 Invoice Generator", font=("Helvetica", 20, "bold"), bg="#3F51B5", fg="white", pady=10)
header.pack(fill="x")

# --- Form Frame ---
form_frame = tk.Frame(root, bg="white", padx=20, pady=15)
form_frame.pack(padx=20, pady=10, fill="x")

tk.Label(form_frame, text="Company Name:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
company_name_entry = tk.Entry(form_frame, width=30)
company_name_entry.grid(row=0, column=1, padx=5)

tk.Label(form_frame, text="Company Address:", bg="white").grid(row=0, column=2, sticky="e", padx=5)
company_address_entry = tk.Entry(form_frame, width=30)
company_address_entry.grid(row=0, column=3, padx=5)

tk.Label(form_frame, text="Client Name:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
client_entry = tk.Entry(form_frame, width=30)
client_entry.grid(row=1, column=1, padx=5)

tk.Label(form_frame, text="Date:", bg="white").grid(row=1, column=2, sticky="e", padx=5)
date_entry = tk.Entry(form_frame, width=30)
date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
date_entry.grid(row=1, column=3, padx=5)

tk.Label(form_frame, text="Invoice #:", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
invoice_entry = tk.Entry(form_frame, width=30)
invoice_entry.grid(row=2, column=1, padx=5)

# --- Items Table ---
item_frame = tk.Frame(root, bg="#f9f9f9", padx=10)
item_frame.pack(fill="x", padx=20, pady=10)

tk.Label(item_frame, text="Item Description:", bg="#f9f9f9").grid(row=0, column=0)
item_entry = tk.Entry(item_frame, width=40)
item_entry.grid(row=0, column=1, padx=5)

tk.Label(item_frame, text="Amount:", bg="#f9f9f9").grid(row=0, column=2)
amount_entry = tk.Entry(item_frame, width=20)
amount_entry.grid(row=0, column=3, padx=5)

def refresh_table():
    for widget in display_frame.winfo_children():
        widget.destroy()
    for i, (desc, amt) in enumerate(data_entries):
        tk.Label(display_frame, text=desc, anchor="w", bg="white").grid(row=i, column=0, sticky="w", padx=10)
        tk.Label(display_frame, text=amt, anchor="e", bg="white").grid(row=i, column=1, sticky="e", padx=10)

def add_item():
    desc = item_entry.get()
    amt = amount_entry.get()
    if desc and amt:
        data_entries.append((desc, amt))
        item_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        refresh_table()

display_frame = tk.Frame(root, bg="white")
display_frame.pack(fill="both", padx=20, pady=5)

# --- Action Buttons ---
action_frame = tk.Frame(root, bg="#f5f5f5")
action_frame.pack(pady=10)

def export_pdf():
    invoice_id = invoice_entry.get() or f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    filename = f"invoices/{invoice_id}.pdf"
    os.makedirs("invoices", exist_ok=True)
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, company_name_entry.get())
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, company_address_entry.get())
    c.drawString(50, height - 90, f"Invoice #: {invoice_entry.get()}")
    c.drawString(50, height - 105, f"Date: {date_entry.get()}")
    c.drawString(50, height - 120, f"Billed To: {client_entry.get()}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 150, "Description")
    c.drawString(400, height - 150, "Amount")

    y = height - 170
    total = 0
    for desc, amt in data_entries:
        c.setFont("Helvetica", 10)
        c.drawString(50, y, desc)
        c.drawRightString(500, y, f"${amt}")
        try:
            total += float(amt)
        except:
            pass
        y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 10, "Total")
    c.drawRightString(500, y - 10, f"${total:.2f}")
    c.save()

    # Save to DB
    cursor.execute("""
        INSERT INTO invoices (invoice_no, date, company_name, company_address, client_name, items, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_id,
        date_entry.get(),
        company_name_entry.get(),
        company_address_entry.get(),
        client_entry.get(),
        str(data_entries),
        total
    ))
    conn.commit()

    messagebox.showinfo("Success", f"Invoice saved and exported as {filename}")

def scan_screen_and_fill():
    img = pyautogui.screenshot()
    text = pytesseract.image_to_string(img)
    lines = text.strip().splitlines()
    if lines:
        client_entry.delete(0, tk.END)
        client_entry.insert(0, lines[0])
        if len(lines) > 1:
            item_entry.delete(0, tk.END)
            item_entry.insert(0, lines[1])

tk.Button(action_frame, text="➕ Add Item", command=add_item, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
tk.Button(action_frame, text="📸 Scan Screen", command=scan_screen_and_fill, bg="#607D8B", fg="white").grid(row=0, column=1, padx=10)
tk.Button(action_frame, text="📄 Export to PDF", command=export_pdf, bg="#2196F3", fg="white").grid(row=0, column=2, padx=10)

# --- Footer ---
footer = tk.Label(root, text="Created by MrTutu · Invoice Generator · 2025", bg="#3F51B5", fg="white", pady=10)
footer.pack(fill="x", side="bottom")

root.mainloop()
