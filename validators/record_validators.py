from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Any, Self, Callable
from numbers import Number

from collections import defaultdict

import re


@dataclass
class Validator(ABC):
    errors: dict[str, list] = field(
        default_factory=lambda: defaultdict(list), init=False)

    @abstractmethod
    # Transparent validation
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    @staticmethod
    def match_regex(regex: str, text: str) -> bool:
        return re.match(regex, text) is not None

    @staticmethod
    def check_condition(condition: Callable[[Any], bool], obj: Any) -> bool:
        return condition(obj)
    
    @staticmethod
    def check_instance(obj: str, element: Any) -> bool:
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
        
        for constraint_name, constraint_values in constraint.items():
            match constraint_name:
                case 'type':
                    if not self.check_instance(constraint_values, value_to_validate):
                        self.errors[key].append('incorrect type')
                        return 
                case 'regex':
                    for i, expression in enumerate(constraint_values, start=1):
                        if not self.match_regex(expression, value_to_validate):
                            self.errors[key].append(f'does not match regex number {i}')
                case 'condition':
                    for i, condition in enumerate(constraint_values, start=1):
                        if not self.check_condition(condition, value_to_validate):
                            self.errors[key].append(f'does not match condition number: {i}')
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
    _constraints: dict[str, dict[str, list[Any]]] = field(
        default_factory=lambda: defaultdict(dict), init=False)
    
    def _add_condition_check(self, constraint_type: str, condition_name: str, 
            key: str, condition: Callable[[Any], bool]) -> None:
        if condition_name not in self._constraints[key]:
            self._constraints[key][condition_name] = []
        self._constraints[key][condition_name].append(condition)
        self._constraints[key]['type'] = constraint_type
    
    def add_regex(self, key: str, regex: str) -> 'ConstraintsBuilder':
        if 'regex' not in self._constraints[key]:
            self._constraints[key]['regex'] = []
        self._constraints[key]['regex'].append(regex)
        self._constraints[key]['type'] = 'str'
        return self

    def add_value_check(self, key: str, condition: Callable[[Number], bool]) -> Self:
        self._add_condition_check('numeric', 'condition', key, condition)
        return self
    
    def add_list_check(self, key: str, condition: Callable[[list[Any]], bool]) -> Self:
        self._add_condition_check('list', 'condition', key, condition)
        return self
    
    def add_bool_check(self, key: str, condition: Callable[[bool], bool]) -> Self:
        self._add_condition_check('bool', 'condition', key, condition)
        return self
    
    def build(self) -> dict[str, dict[str, Any]]:
        return dict(self._constraints)



    
