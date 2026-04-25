from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_receipt(data):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "RECEIPT")

    # Company
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, "Chumcred Limited")

    # Data
    y = 740
    c.drawString(50, y, f"Client: {data.get('client_name')}")
    y -= 20
    c.drawString(50, y, f"Customer: {data.get('beneficiary_name')}")
    y -= 20
    c.drawString(50, y, f"Date: {datetime.now().strftime('%d %b %Y')}")
    y -= 30

    c.drawString(50, y, f"Item: {data.get('item')}")
    y -= 20
    c.drawString(50, y, f"Description: {data.get('item_description')}")
    y -= 20

    amount = float(data.get("item_cost", 0))
    vat = amount * 0.075
    total = amount + vat

    y -= 20
    c.drawString(50, y, f"Amount: ₦{amount:,.2f}")
    y -= 20
    c.drawString(50, y, f"VAT (7.5%): ₦{vat:,.2f}")
    y -= 20
    c.drawString(50, y, f"Total: ₦{total:,.2f}")

    y -= 40
    c.drawString(50, y, "Thank you for your business.")

    c.save()

    buffer.seek(0)
    return buffer