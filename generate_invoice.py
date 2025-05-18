# generate_invoice.py
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_invoice(data, output_dir="invoices"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)

    c = canvas.Canvas(filepath, pagesize=LETTER)
    width, height = LETTER

    # Company Logo (optional)
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 80, width=80, preserveAspectRatio=True, mask='auto')

    # Company Name
    c.setFont("Helvetica-Bold", 16)
    c.drawString(140, height - 50, data["company_name"])

    # Invoice Info
    c.setFont("Helvetica", 10)
    c.drawString(400, height - 50, f"Invoice #: {data['invoice_number']}")
    c.drawString(400, height - 65, f"Date: {data['date']}")

    # Bill To
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 120, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 135, data["bill_to"])

    # Line Items
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, height - 170, "Description")
    c.drawString(300, height - 170, "Quantity")
    c.drawString(380, height - 170, "Unit Price")
    c.drawString(470, height - 170, "Total")

    c.setFont("Helvetica", 10)
    y = height - 190
    total_amount = 0
    for item in data["items"]:
        total = item["quantity"] * item["unit_price"]
        total_amount += total

        c.drawString(40, y, item["description"])
        c.drawRightString(340, y, str(item["quantity"]))
        c.drawRightString(420, y, f"${item['unit_price']:.2f}")
        c.drawRightString(510, y, f"${total:.2f}")
        y -= 20

    # Total
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(510, y - 20, f"Total: ${total_amount:.2f}")

    c.showPage()
    c.save()

    return filepath
