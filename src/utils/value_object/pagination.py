from dataclasses import dataclass
from typing import Generic, TypeVar
import base64
import json

T = TypeVar('T')

@dataclass
class PaginatedResponse(Generic[T]):
    data: list[T]
    cursor: str | None
    has_more: bool
    total_count: int | None = None

    def to_dict(self):
        return{
            "data": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data],
            "pagination-info":{
                "ursor": self.cursor,
                "has_more": self.has_more,
                "total_count": self.total_count
            }
        }
    
class CursorEncoder:
    @staticmethod
    def encode(field_value: any, field_name: str = "id")->str:
        cursor = {field_name: str(field_value)}
        json_cursor = json.dumps(cursor)
        return base64.urlsafe_b64encode(json_cursor.encode()).decode()
    
    @staticmethod
    def decode(cursor: str)->dict:
        try:
            json_cursor = base64.urlsafe_b64decode(cursor.encode()).decode()
            return json.loads(json_cursor)
        except Exception:
            raise ValueError("Invalid cursor format")