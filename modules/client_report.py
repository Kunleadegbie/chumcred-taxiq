import pandas as pd
from io import BytesIO

def generate_client_report(data):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    # Remove system columns
    df = df.drop(columns=["id", "user_id", "client_id"], errors='ignore')

    df["cost_price"] = df.get("cost_price", 0)
    df["Profit"] = df["item_cost"] - df["cost_price"]

    # Rename columns
    df = df.rename(columns={
        "month": "Month",
        "year": "Year",
        "beneficiary_name": "Customer",
        "beneficiary_tin": "TIN",
        "item": "Item",
        "item_cost": "Selling Price",
        "cost_price": "Cost Price",
        "item_description": "Description"
    })

    # Totals
    total_revenue = df["Selling Price"].sum()
    total_cost = df["Cost Price"].sum()
    total_profit = df["Profit"].sum()

    summary = pd.DataFrame([{
        "Total Revenue": total_revenue,
        "Total Cost": total_cost,
        "Total Profit": total_profit
    }])

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        summary.to_excel(writer, index=False, sheet_name="Summary")

    output.seek(0)
    return output