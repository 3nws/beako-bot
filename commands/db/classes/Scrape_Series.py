from abc import ABC, abstractmethod


class Scrape_Series(ABC):

    @abstractmethod
    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def scrape(self):
        return "scrape() method has not been implemented."

    @abstractmethod
    def latest_chapter(self):
        return "latest_chapter() method has not been implemented."
