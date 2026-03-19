from typing import Optional


class Address:
    def __init__(
        self,
        street: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        country: str = "USA",
    ):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"

    def __repr__(self) -> str:
        return f"Address(city={self.city}, state={self.state}, zip_code={self.zip_code})"
