from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_receipt(data_list, client_name):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    primary_color = colors.HexColor("#0B6E4F")

    # HEADER
    c.setFillColor(primary_color)
    c.rect(0, height - 80, width, 80, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, client_name)
    c.drawRightString(width - 50, height - 50, "RECEIPT")

    # META
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    receipt_no = f"RCPT-{datetime.now().strftime('%Y%m%d%H%M')}"
    c.drawString(50, height - 110, f"Receipt No: {receipt_no}")
    c.drawRightString(width - 50, height - 110, f"Date: {datetime.now().strftime('%d %b %Y')}")

    # CUSTOMER
    customer_name = data_list[0].get("beneficiary_name")
    y = height - 150
    c.drawString(50, y, f"Customer: {customer_name}")

    y -= 30

    # TABLE HEADER
    c.setFillColor(primary_color)
    c.rect(50, y, width - 100, 20, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)

    c.drawString(55, y + 5, "Item")
    c.drawString(250, y + 5, "Amount")
    c.drawString(350, y + 5, "VAT")
    c.drawString(450, y + 5, "Total")

    y -= 30

    # DATA ROWS
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    total_amount = 0
    total_vat = 0

    for row in data_list:

        amount = float(row.get("item_cost", 0))
        vat = amount * 0.075
        total = amount + vat

        total_amount += amount
        total_vat += vat

        c.drawString(55, y, row.get("item"))
        c.drawRightString(300, y, f"N{amount:,.2f}")
        c.drawRightString(420, y, f"N{vat:,.2f}")
        c.drawRightString(550, y, f"N{total:,.2f}")

        y -= 20

    # TOTAL
    grand_total = total_amount + total_vat

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(550, y, f"TOTAL: N{grand_total:,.2f}")

    # FOOTER
    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, y, "Thank you for your business.")

    c.save()
    buffer.seek(0)

    return buffer