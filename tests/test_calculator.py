from src.tools.calculator import calculate_ratio, calculate_percentage_change


def test_calculate_ratio_basic():
    result = calculate_ratio(numerator=50, denominator=100, label="test-ratio")
    assert result["ratio"] == 0.5
    assert result["label"] == "test-ratio"


def test_calculate_ratio_divide_by_zero():
    result = calculate_ratio(numerator=50, denominator=0, label="test-ratio")
    assert "error" in result


def test_calculate_percentage_change_basic():
    result = calculate_percentage_change(old_value=100, new_value=150, label="growth")
    assert result["change_pct"] == 50.0


def test_calculate_percentage_change_from_zero():
    result = calculate_percentage_change(old_value=0, new_value=150, label="growth")
    assert "error" in result