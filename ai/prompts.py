def vat_analysis_prompt(data):
    return f"""
    You are a Nigerian tax expert.

    Analyze VAT records below:
    {data}

    Provide:
    - Total revenue
    - VAT payable
    - Risks
    - Recommendations
    """