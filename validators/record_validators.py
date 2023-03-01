from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Union, Any, Self, Callable
from decimal import Decimal
import re


class Validator(ABC):
    def __init__(self) -> None:
        self.errors = {}

    @abstractmethod
    # Transparent validation
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    @staticmethod
    def match_regex(regex: str, text: str) -> bool:
        return re.match(regex, text) is not None

    @staticmethod
    def check_value_condition(condition: Callable[[Union[int, float, Decimal]], bool], 
            value: Callable[[Union[int, float, Decimal]], bool]) -> bool:
        return condition(value)
    
    @staticmethod
    def validate_key_value(key: str, data: dict[str, Any], 
            condition: Callable[[Any], bool]) -> str:
        if key not in data:
            return 'key not found'
        
        if not condition(data[key]):
            return 'not correct'
        
        return ''

    def errors_to_str(self) -> str:
        return ', '.join(f'{key}: {message}' 
                for key, message in self.errors)
    

class RecordValidator(Validator):
    def __init__(self, constraints: dict[dict[str, Any]]) -> None:
        super().__init__()
        self._constraints = constraints

    def check_constraint(self, key: str, data: dict[str, Any], 
            constraint: dict[str, Any]) -> dict[str, Any]:
        ...

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        return data


@dataclass(frozen=True, order=True)
class ConstraintsBuilder:
    _constraints: dict[dict[str, Any]] = field(
        default_factory=dict, init=False)
    
    def add_regex(self, key: str, regex: str) -> Self:
        self._constraints[key] = {
            'type': 'str',
            'regex': regex
        }
        return self

    def add_value_check(self, key: str, 
                condition: Callable[[Union[int, float, Decimal]], bool]) -> Self:
        self._constraints[key] = {
            'type': 'numeric',
            'condition': condition
        }
        return self

    def build(self) -> dict[dict[str, Any]]:
        return self._constraints
        

def main() -> None:
    constraints = ConstraintsBuilder()\
        .add_regex('name', r'^[A-Z][a-z]+$')\
        .add_value_check('USD', lambda x: 0 <= x <= 10)\
        .build()

if __name__ == '__main__':
    main()



    
