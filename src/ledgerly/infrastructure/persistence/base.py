from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """데이터 저장소의 공통 인터페이스입니다."""
    
    @abstractmethod
    def save(self, entity: T) -> None:
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        pass
