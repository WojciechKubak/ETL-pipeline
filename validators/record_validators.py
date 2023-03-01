from abc import ABC, abstractmethod
from typing import Any, Union
import re
from decimal import Decimal


class Validator(ABC):
    def __init__(self) -> None:
        self.errors = {}

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    def errors_to_str(self) -> str:
        return ', '.join([f'{key}: {message}' for key, message in self.errors.items()])
    
    @abstractmethod
    def match_regex(regex: str, text: str) -> bool:
        return re.match(regex, text) is not None
    
    @abstractmethod
    def is_not_negative(value: Union[int, float, Decimal]) -> bool:
        return value >= 0
    
    @abstractmethod
    def is_selected_type(element: Any, type: Any) -> bool:
        return isinstance(element, type)
    


class CurrencyRatesBuilder(Validator):
    ...
