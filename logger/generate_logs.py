from typing import Callable, Any
import os
from datetime import datetime


class Logger:
    def __init__(self, filename: str, log_dir: str = '../logs'):
        self.filename = filename
        self.log_dir = log_dir

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def __call__(self, func: Callable) -> Callable:
        
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            operation_success = False
            error_message = ''

            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                operation_success = True
            except Exception as e:
                error_message += str(e)
            
            end_time = datetime.now()
            operation_time = (end_time - start_time).total_seconds()

            log_message = f"{start_time.strftime('%Y-%m-%d %H:%M:%S')}: " \
                        f"{func.__name__} - "\
                        f"{'Success' if operation_success else 'Failure'} - "\
                        f"Error: {error_message if error_message else ''}"\
                        f"Time taken: {operation_time}s\n"
            
            with open(f'{os.path.join(self.log_dir, self.filename)}', 'a') as txt_writer:
                txt_writer.write(log_message)
            
            return result
        
        return wrapper