from abc import ABC, abstractmethod
from typing import List
from core.models import AttendanceRow


class IReportParsingStrategy(ABC):

    @property
    @abstractmethod
    def report_type(self) -> str:
        pass

    @abstractmethod
    def identify(self, raw_text: str) -> bool:
        pass

    @abstractmethod
    def parse(self, raw_text: str) -> List[AttendanceRow]:
        pass