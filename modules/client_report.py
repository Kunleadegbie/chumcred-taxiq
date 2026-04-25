import pandas as pd
from io import BytesIO

def generate_client_report(data):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    df["cost_price"] = df.get("cost_price", 0)
    df["Profit"] = df["item_cost"] - df["cost_price"]

    summary = {
        "Total Revenue": df["item_cost"].sum(),
        "Total Cost": df["cost_price"].sum(),
        "Gross Profit": df["Profit"].sum()
    }

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        pd.DataFrame([summary]).to_excel(writer, index=False, sheet_name="Summary")

    output.seek(0)
    return output