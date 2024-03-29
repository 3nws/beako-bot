from abc import ABC, abstractmethod
from typing import Any


class Scrape_Series(ABC):
    @abstractmethod
    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def scrape(self) -> Any:
        raise NotImplementedError("scrape method has not been implemented")

    @abstractmethod
    def latest_chapter(self) -> Any:
        raise NotImplementedError("latest_chapter method has not been implemented")
