# Lab 7 - Hardened version (fixed after fuzz testing)
# Name: CHINMAI A S | SRN: PES2UG24AM198 | Section: C
import math


def _to_float(value):
    """Convert to a finite float, or return None (rejects '', 'abc', inf, nan)."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def parse_order(text):
    """'garment:kg' -> (Garment, kg) or None for invalid input."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:                 # missing or extra ':'
        return None
    garment = parts[0].strip()
    kg = _to_float(parts[1])
    if not garment or kg is None or kg < 0:
        return None
    return garment.title(), kg


def weight_average(weights_csv):
    """'3,5,8' -> integer average, or None for invalid input."""
    if not isinstance(weights_csv, str):
        return None
    values = []
    for raw in weights_csv.split(','):
        try:
            value = int(raw)            # also raises for '' (e.g. '1,,3')
        except ValueError:
            return None
        if value < 0:
            return None
        values.append(value)
    if not values:                      # never divide by zero
        return None
    return sum(values) // len(values)


def payable_charge(text):
    """'charge|discount' -> charge incl. 18% tax minus discount (>= 0), or None."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    charge, discount = _to_float(parts[0]), _to_float(parts[1])
    if charge is None or discount is None or charge < 0 or discount < 0:
        return None
    total = charge * 1.18 - discount
    if not math.isfinite(total):        # overflow for huge charges
        return None
    return max(total, 0)


def _report(label, result):
    if result is None:
        print(f"{label}: Invalid input, please check the format.")
    else:
        print(f"{label}:", result)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter garment:weight in kg (e.g. regular:6): ")
    _report("Garment and Weight", parse_order(user_input))

    print("\n==== Running weight_average ====")
    user_input = input("Enter garment weights as CSV (e.g. 3,5,8): ")
    _report("Average Weight", weight_average(user_input))

    print("\n==== Running payable_charge ====")
    user_input = input("Enter charge|discount (e.g. 300|40): ")
    _report("Payable Charge", payable_charge(user_input))


if __name__ == "__main__":
    main()
