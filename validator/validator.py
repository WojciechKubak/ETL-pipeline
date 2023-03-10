from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Any, Self, Callable
from numbers import Number

from collections import defaultdict

import re


@dataclass
class Validator(ABC):
    """
    Base class for data validators. 

    This class defines the common interface and behavior for all data validators.
    """
    errors: dict[str, list] = field(
        default_factory=lambda: defaultdict(list), init=False)

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates the input data and returns the validated data if successful.

        Args:
            data (dict[str, Any]): The data to validate.

        Returns:
            dict[str, Any]: The validated data.

        Raises:
            ValueError: If any validation errors occur.
        """
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
        """
        This method returns a string representation of the error messages.

        Returns:
            str: The error messages as a string.
        """
        return ', '.join(f'{key}: {message}' 
                for key, message in self.errors.items())
    

@dataclass
class RecordValidator(Validator):
    """
    Validator for records with constraints.

    This class validates a dictionary of records against a set of constraints.
    """
    _constraints: dict[dict[str, Any]]

    def _check_constraint(self, key: str, data: dict[str, Any], 
        constraint: dict[str, Any]) -> None:
        """
        Checks a single constraint against a record.

        Args:
            key (str): The key of the record to check the constraint against.
            data (dict[str, Any]): The record to check the constraint against.
            constraint (dict[str, Any]): The constraint to check.

        Raises:
            ValueError: If the constraint is not satisfied.
        """

        # Check if the key is in the record.
        if not (value_to_validate := data.get(key)):
            self.errors[key] = 'key not found'
            return 
                
        # Iterate over the constraint keys and values and check if the constraint is satisfied.
        for constraint_name, constraint_values in constraint.items():
            # Check if the constraint is of type 'type'.
            match constraint_name:
                case 'type':
                    if not self.check_instance(constraint_values, value_to_validate):
                        self.errors[key].append('incorrect type')
                        return 
                # Check if the constraint is of type 'regex'.
                case 'regex':
                    for i, expression in enumerate(constraint_values, start=1):
                        if not self.match_regex(expression, value_to_validate):
                            self.errors[key].append(f'does not match regex number {i}')
                # Check if the constraint is of type 'condition'.
                case 'condition':
                    for i, condition in enumerate(constraint_values, start=1):
                        if not self.check_condition(condition, value_to_validate):
                            self.errors[key].append(f'does not match condition number: {i}')
                # Raise an error if the constraint is not recognized.
                case _:
                    raise ValueError('Constraint not found')
                
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates a dictionary of records against the set of constraints.

        Args:
            data (dict[str, Any]): The dictionary of records to validate.

        Returns:
            dict[str, Any]: The validated dictionary of records.

        Raises:
            ValueError: If the constraints are not satisfied or no input data is provided.
        """

        # Raise a ValueError if input data is empty.
        if not data:
            raise ValueError("No input data provided.")

        # Reset the errors dictionary.
        self.errors = defaultdict(list)

        # Iterate over the constraints and check each record against its constraints.
        for key, constraint in self._constraints.items():
            self._check_constraint(key, data, constraint) 

        # Raise a ValueError if there are any errors in the errors dictionary.
        if len(self.errors) > 0:
            raise ValueError(self.errors_to_str())
        
        return data


@dataclass(frozen=True, order=True)
class ConstraintsBuilder:
    """
    Builder for record constraints.

    This class provides an API for building constraints for records.
    """
    _constraints: dict[str, dict[str, list[Any]]] = field(
        default_factory=lambda: defaultdict(dict), init=False)
    
    def _add_condition_check(self, constraint_type: str, condition_name: str, 
            key: str, condition: Callable[[Any], bool]) -> None:
        """
        Add a condition check to a record constraint.

        Args:
            constraint_type (str): The type of the constraint (e.g. "numeric", "list", "bool").
            condition_name (str): The name of the condition being checked.
            key (str): The key of the record being validated.
            condition (Callable[[Any], bool]): A callable that takes a value and returns a bool indicating whether the value satisfies the condition.

        Returns:
            None
        """
        if condition_name not in self._constraints[key]:
            self._constraints[key][condition_name] = []
        self._constraints[key][condition_name].append(condition)
        self._constraints[key]['type'] = constraint_type
    
    def add_regex(self, key: str, regex: str) -> Self:
        """
        Add a boolean condition check to a record.

        Args:
            key (str): The key of the record being validated.
            condition (Callable[[bool], bool]): A callable that takes a boolean value and returns a bool indicating whether the value satisfies the condition.

        Returns:
            Self: A reference to the ConstraintsBuilder object to enable method chaining.
        """
        if 'regex' not in self._constraints[key]:
            self._constraints[key]['regex'] = []
        self._constraints[key]['regex'].append(regex)
        self._constraints[key]['type'] = 'str'
        return self

    def add_value_check(self, key: str, condition: Callable[[Number], bool]) -> Self:
        """
        Add a value check to the validator.
    
        Args:
            key (str): The key to validate.
            condition (Callable[[Number], bool]): The condition that the value must meet.

        Returns:
            Self: The validator instance.
        """
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



    
