from decimal import Decimal, ROUND_HALF_UP

class Pricing:
    _tax:Decimal = Decimal("15.00")

    @staticmethod
    def calculate_price(employee_count:int, count_base:int = None)->dict:
        if count_base is not None and isinstance(count_base, int):
            employee_count = employee_count-count_base
        price_tax = Decimal(employee_count) * Pricing._tax
        price_tax = price_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "decimal": price_tax,
            "cents": int(price_tax*100)
        }