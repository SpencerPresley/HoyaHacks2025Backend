from typing import Type
from pydantic import BaseModel
import random

class _ResumeParserHelper(BaseModel):
    user_int: int = 0
    
    def __init__(self):
        pass
    
    def generate_random_name(self) -> str:
        """Generate a random name.
        
        Returns:
            str: A random name
        """
        name = f"person_{self.user_int}"
        self._increment_user_int()
        return name
    
    def generate_random_email(self) -> str:
        """Generate a random email address.
        
        Returns:
            str: A random email address
        """
        return f"person_{random.randint(1000, 9999)}@example.com"
    
    def generate_random_phone(self) -> str:
        """Generate a random phone number.
        
        Returns:
            str: A random phone number
        """
        return f"{random.randint(1000000000, 9999999999)}"
    
    @classmethod
    def _increment_user_int(
        cls: Type['_ResumeParserHelper']
    ) -> None:
        """Increment the user_int.
        """
        cls.user_int += 1
