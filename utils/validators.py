def validate_vat_input(name, tin, item, cost, desc):
    return all([name, tin, item, desc]) and cost > 0