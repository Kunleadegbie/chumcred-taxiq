from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_receipt(data):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    primary_color = colors.HexColor("#0B6E4F")   # deep green (premium feel)
    accent_color = colors.HexColor("#F4A261")    # soft orange accent

    # ---------------- HEADER ----------------
    c.setFillColor(primary_color)
    c.rect(0, height - 80, width, 80, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)

    # ✅ Replace company name with CLIENT NAME
    c.drawString(50, height - 50, data.get("client_name", "Client"))

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 50, height - 50, "RECEIPT")

    # ---------------- META ----------------
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    receipt_no = f"RCPT-{datetime.now().strftime('%Y%m%d%H%M')}"
    c.drawString(50, height - 110, f"Receipt No: {receipt_no}")
    c.drawRightString(width - 50, height - 110, f"Date: {datetime.now().strftime('%d %b %Y')}")

    # ---------------- CUSTOMER INFO ----------------
    y = height - 150

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Customer: {data.get('beneficiary_name')}")
    y -= 25

    # ---------------- TABLE HEADER ----------------
    c.setFillColor(primary_color)
    c.rect(50, y - 15, width - 100, 20, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)

    c.drawString(55, y - 10, "Item")
    c.drawString(250, y - 10, "Amount")
    c.drawString(350, y - 10, "VAT (7.5%)")
    c.drawString(450, y - 10, "Total")

    y -= 35

    # ---------------- VALUES ----------------
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)

    item = data.get("item")
    amount = float(data.get("item_cost", 0))
    vat = amount * 0.075
    total = amount + vat

    c.drawString(55, y, str(item))

    c.drawRightString(300, y, f"N{amount:,.2f}")
    c.drawRightString(420, y, f"N{vat:,.2f}")
    c.drawRightString(550, y, f"N{total:,.2f}")

    # ---------------- TOTAL SECTION ----------------
    y -= 40

    c.setStrokeColor(accent_color)
    c.setLineWidth(1.5)
    c.line(300, y, 550, y)

    y -= 25

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(primary_color)
    c.drawRightString(550, y, f"TOTAL: N{total:,.2f}")

    # ---------------- FOOTER ----------------
    y -= 60

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawString(50, y, "Thank you for your business.")

    c.save()
    buffer.seek(0)

    return buffer