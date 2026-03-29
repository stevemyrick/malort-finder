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

    @property
    def lat(self) -> float | None:
        return self._lat

    @lat.setter
    def lat(self, value: float | None):
        self._lat = value

    @property
    def lng(self) -> float | None:
        return self._lng

    @lng.setter
    def lng(self, value: float | None):
        self._lng = value

    def __repr__(self) -> str:
        """String representation."""
        return f"{self._address} -> {self._stock_count} in stock!"

    def __init__(self, address: str, stock_count: int, lat: float | None = None, lng: float | None = None):
        self._address = address
        self._stock_count = stock_count
        self._lat = lat
        self._lng = lng

    def to_dict(self) -> dict:
        return {
            "address": self._address,
            "stock_count": self._stock_count,
            "lat": self._lat,
            "lng": self._lng,
            "has_stock": self._stock_count > 0,
        }

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

    def to_dict(self) -> dict:
        return {
            "plu": self._price_lookup_code,
            "price": self._price,
            "volume": self._volume,
        }