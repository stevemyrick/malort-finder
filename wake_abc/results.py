"""Definition of inventory results."""

class Location:
    """Defines a location result."""

    @property
    def address(self) -> str:
        """The address of the location."""
        return self._address
    
    @property
    def stock_count(self) -> int:
        """The amount in stock."""
        return self._stock_count
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self._address} -> {self._stock_count} in stock!"

    def __init__(self, address: str, stock_count: int):
        self._address = address
        self._stock_count = stock_count

class Product:
    """Defines a product."""

    @property
    def price_lookup_code(self) -> str:
        """The price lookup code."""
        return self._price_lookup_code
    
    @property
    def price(self) -> float:
        """The price in USD."""
        return self._price
    
    @property
    def volume(self) -> float:
        """The volume in liters."""
        return self._volume
    
    def __repr__(self) -> str:
        """String representation."""
        return f"PLU {self._price_lookup_code}: ${self._price} for {self._volume}L"

    def __init__(self, price_lookup_code: str, price: float, volume: float):
        self._price_lookup_code = price_lookup_code
        self._price = price
        self._volume = volume