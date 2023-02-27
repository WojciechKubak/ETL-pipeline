from abc import ABC, abstractmethod

from typing import Any, Callable
import re


class Validator(ABC):
    def __init__(self) -> None:
        self.errors = {}

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    def errors_to_str(self) -> str:
        return f"{', '.join(f'{key}: {message}' for key, message in self.errors.items())}"
    
    @staticmethod
    def match_regex(regex: str, text: str) -> bool:
        return re.match(regex, text) is not None
    
    @staticmethod
    def validate_key_value(key: str, data: dict[str, Any], 
                        value_condition_fn: Callable[[str], bool]) -> str:
        if key not in data:
            return 'required'
        
        if not value_condition_fn(data[key]):
            return 'not correct'
        
        return ''
