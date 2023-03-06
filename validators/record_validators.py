from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Union, Any, Self, Callable
from decimal import Decimal
import re


@dataclass(frozen=True, order=True)
class Validator(ABC):
    errors: dict[str, str] = field(default_factory=dict, init=False)

    @abstractmethod
    # Transparent validation
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    @staticmethod
    def match_regex(regex: str, text: str) -> bool:
        return re.match(regex, text) is not None

    @staticmethod
    def check_value_condition(condition: Callable[[Union[int, float, Decimal]], bool], 
            value: Union[int, float, Decimal]) -> bool:
        return condition(value)
    
    @staticmethod
    def match_type(data_type: type, text: Any) -> bool:
        return isinstance(text, data_type)
    
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
                for key, message in self.errors.items())
    

@dataclass(frozen=True, order=True)
class RecordValidator(Validator):
    _constraints: dict[dict[str, Any]]

    def _check_constraint(self, key: str, data: dict[str, Any], 
            constraint: dict[str, Any]) -> None:
        for constraint_name, constraint_value in constraint.items():

            value_to_validate = data[key]

            match constraint_name:
                case 'type':
                    if not self.match_type(constraint_value, value_to_validate):
                        self.errors[key] = 'not specified type.'
                case 'regex':
                    if not self.match_regex(constraint_value, value_to_validate):
                        self.errors[key] = 'no match for regex.'
                case 'condition':
                   if not self.check_value_condition(constraint_value, value_to_validate):
                       self.errors[key] = 'no match for expression.'
                case _:
                    raise ValueError('Constraint not found.')
                

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        # self.errors = {}

        for key, constraint in self._constraints.items():
            self._check_constraint(key, data, constraint) 

        if len(self.errors) > 0:
            raise ValueError(self.errors_to_str())
        
        return data


@dataclass(frozen=True, order=True)
class ConstraintsBuilder:
    _constraints: dict[dict[str, Any]] = field(
        default_factory=dict, init=False)
    
    def add_regex(self, key: str, regex: str) -> Self:
        self._constraints[key] = {
            'type': str,
            'regex': regex
        }
        return self

    def add_value_check(self, key: str, 
                condition: Callable[[Union[int, float, Decimal]], bool]) -> Self:
        self._constraints[key] = {
            'type': float,
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
    
    rv = RecordValidator(constraints)

    example_record = {
        'name': 'Wojtek',
        'USD': 4.67,
    }

    print(
        rv.validate(example_record)
    )

if __name__ == '__main__':
    main()



    
