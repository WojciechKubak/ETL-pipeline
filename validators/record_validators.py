from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Any, Self, Callable
from decimal import Decimal
from numbers import Number
from collections import defaultdict
import re


@dataclass
class Validator(ABC):
    errors: dict[str, list] = field(default_factory=lambda: defaultdict(list), init=False)

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
    def check_type(obj: str, element: Any) -> bool:
        match obj:
            case 'numeric':
                return isinstance(element, Number)
            case 'str':
                return isinstance(element, str)
            case 'bool':
                return isinstance(element, bool)
            case 'list':
                return isinstance(element, list)
        return False

    def errors_to_str(self) -> str:
        return ', '.join(f'{key}: {message}' 
                for key, message in self.errors.items())
    

@dataclass
class RecordValidator(Validator):
    _constraints: dict[dict[str, Any]]

    def _check_constraint(self, key: str, data: dict[str, Any], 
            constraint: dict[str, Any]) -> None:
        if not (value_to_validate := data.get(key)):
            self.errors[key] = 'key not found'
            return 
        
        for constraint_name, constraint_value in constraint.items():
            match constraint_name:
                case 'type':
                    if not self.check_type(constraint_value, value_to_validate):
                        self.errors[key].append('incorrect type')
                        return 
                case 'regex':
                    if not self.match_regex(constraint_value, value_to_validate):
                        self.errors[key].append('no match for regex')
                case 'condition':
                   if not self.check_value_condition(constraint_value, value_to_validate):
                       self.errors[key].append('does not meet the condition')
                case _:
                    raise ValueError('Constraint not found')
                
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        self.errors = defaultdict(list)

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
    
    def add_list_check(self, key: str, condition: Callable[[list[Any]], bool]) -> Self:
        self._constraints[key] = {
            'type': 'list',
            'condition': condition
        }
        return self
    
    def add_bool_check(self, key: str, condition: Callable[[bool], bool]) -> Self:
        self._constraints[key] = {
            'type': 'bool',
            'condition': condition
        }
        return self

    def build(self) -> dict[dict[str, Any]]:
        return self._constraints
        

def main() -> None:
    constraints = ConstraintsBuilder()\
        .add_regex('name', r'^[A-Z][a-z]+$')\
        .add_value_check('value', lambda x: x > 5)\
        .add_value_check('value', lambda x: 0 <= x <= 10)\
        .add_list_check('products', lambda x: len(x) > 4)\
        .add_bool_check('is_active', lambda x: not x)\
        .build()
    
    record = {
        'name': 'Wojtus',
        'value': 11,
        'products': [1, 2, 3],
        'is_active': True
    }


    rv = RecordValidator(constraints)

    print(
        rv.validate(record)
    )
    

if __name__ == '__main__':
    main()



    
