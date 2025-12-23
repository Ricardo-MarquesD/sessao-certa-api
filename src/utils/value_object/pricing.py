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
    
    @staticmethod
    def calculate_commission(price: Decimal, percentage: Decimal)->Decimal:
        if not isinstance(price, Decimal):
            raise ValueError("price must be a Decimal")
        if not isinstance(percentage, Decimal):
            raise ValueError("percentage must be a Decimal")
        
        commission_value = price * percentage
        commission_value = commission_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return commission_value