from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class PaginatedResponse(Generic[T]):
    data: list[T]
    next_cursor: str | None
    has_more: bool
    total_count: int | None = None

    def to_dict(self):
        return{
            "data": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data],
            "pagination-info":{
                "next_cursor": self.next_cursor,
                "has_more": self.has_more,
                "total_count": self.total_count
            }
        }