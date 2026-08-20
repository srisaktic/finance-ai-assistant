def calculate_ratio(numerator: float, denominator: float, label: str = "") -> dict:
    """Compute a simple ratio between two financial figures (e.g. debt-to-equity, current ratio, margin)."""
    if denominator == 0:
        return {"error": "Cannot divide by zero", "label": label}
    return {
        "label": label,
        "numerator": numerator,
        "denominator": denominator,
        "ratio": round(numerator / denominator, 4),
    }


def calculate_percentage_change(old_value: float, new_value: float, label: str = "") -> dict:
    """Compute percentage change between two values (e.g. revenue growth, stock price change)."""
    if old_value == 0:
        return {"error": "Cannot calculate percentage change from zero", "label": label}
    change_pct = ((new_value - old_value) / old_value) * 100
    return {
        "label": label,
        "old_value": old_value,
        "new_value": new_value,
        "change_pct": round(change_pct, 2),
    }


if __name__ == "__main__":
    # example: Nvidia's debt-to-equity, and a hypothetical revenue growth
    print(calculate_ratio(numerator=11_000, denominator=55_000, label="debt-to-equity"))
    print(calculate_percentage_change(old_value=60_900, new_value=130_500, label="revenue growth"))