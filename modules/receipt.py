from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime


def generate_receipt(data):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # ---------------- HEADER ----------------
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 50, "RECEIPT")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Chumcred Limited")

    # ---------------- META ----------------
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 110, f"Receipt No: RCPT-{datetime.now().strftime('%Y%m%d%H%M')}")
    c.drawString(350, height - 110, f"Date: {datetime.now().strftime('%d %b %Y')}")

    # ---------------- CLIENT INFO ----------------
    y = height - 150
    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Client: {data.get('client_name')}")
    y -= 20
    c.drawString(50, y, f"Customer: {data.get('beneficiary_name')}")
    y -= 30

    # ---------------- TABLE HEADER ----------------
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Amount")
    c.drawString(350, y, "VAT (7.5%)")
    c.drawString(450, y, "Total")

    y -= 10
    c.line(50, y, 550, y)

    # ---------------- VALUES ----------------
    c.setFont("Helvetica", 11)

    item = data.get("item")
    amount = float(data.get("item_cost", 0))
    vat = amount * 0.075
    total = amount + vat

    y -= 20
    c.drawString(50, y, str(item))

    # RIGHT ALIGN NUMBERS
    c.drawRightString(300, y, f"N{amount:,.2f}")
    c.drawRightString(420, y, f"N{vat:,.2f}")
    c.drawRightString(550, y, f"N{total:,.2f}")

    # ---------------- TOTAL SECTION ----------------
    y -= 40
    c.line(300, y, 550, y)

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(550, y, f"TOTAL: N{total:,.2f}")

    # ---------------- FOOTER ----------------
    y -= 50
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Thank you for your business.")

    c.save()
    buffer.seek(0)

    return buffer