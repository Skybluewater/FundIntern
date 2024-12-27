# a data class to store infos of the announcement
# including total_cnt, page_size, size, currentPage, status etc
from dataclasses import dataclass
from typing import List, Any
from datetime import datetime, date
from dataclass.serializableI import Serializable
from toolclass.extractor.pdf_extractor import PDFExtractor
from toolclass.extractor.xlsx_extractor import XLSXExtractor
from toolclass.reader.reader import Reader
import json

@dataclass
class Announcement(Serializable):
    headline: str
    announcement_time: datetime
    id: str
    content: str
    file_name: str
    valid_time: datetime
    announcement_set: 'AnnouncementSet'
    stock_infos_in: Any = None
    stock_infos_out: Any = None

    def to_dict(self):
        return {
            "headline": self.headline,
            "ann_time": self.announcement_time.date().isoformat(),
            "id": self.id,
            "content": self.content,
            "file_name": self.file_name,
            "valid_time": self.valid_time.isoformat() if self.valid_time else None,
        }
    
    @classmethod
    def from_dict(cls, dictionary):
        return cls(
            headline=dictionary.get("headline"),
            announcement_time=datetime.fromisoformat(dictionary.get("ann_time")).date(),
            id=dictionary.get("id"),
            content=dictionary.get("content"),
            file_name=dictionary.get("file_name"),
            valid_time=datetime.fromisoformat(dictionary.get("valid_time")).date() if dictionary.get("valid_time") else None,
            announcement_set=None  # This should be set separately if needed
        )
    
    def get_stock_info(self):
        stock_infos_in, stock_infos_out = None, None

        def get_stock_by_file(file_name):
            file_suffix = file_name.split(".")[-1]
            file_content = Reader(file_name).content
            if file_suffix == "pdf":
                pdf_extractor = PDFExtractor(self)    
                stock_infos_in, stock_infos_out = pdf_extractor.extract_stock_info(file_content)
            elif file_suffix == "xlsx":
                xlsx_extractor = XLSXExtractor(self)
                stock_infos_in, stock_infos_out = xlsx_extractor.extract_stock_info(file_content)
            return stock_infos_in, stock_infos_out

        def get_stock_by_net():
            # return announcement_handler(self)
            pass
        
        if self.file_name is None:
            self.stock_infos_in, self.stock_infos_out = get_stock_by_net()
        else:
            self.stock_infos_in, self.stock_infos_out = get_stock_by_file(self.file_name)

@dataclass
class AnnouncementSet(Serializable):
    index_name: str
    total: int
    pageSize: int
    size: int
    currentPage: int
    status: str
    announcements: List[Announcement]

    def to_dict(self):
        return {
            "index_name": self.index_name,
            "total": self.total,
            "pageSize": self.pageSize,
            "size": self.size,
            "currentPage": self.currentPage,
            "status": self.status,
            "announcements": [ann.to_dict() for ann in self.announcements]
        }
    
    @classmethod
    def from_dict(cls, dictionary):
        current_cls = cls(
            index_name=dictionary.get("index_name"),
            total=dictionary.get("total"),
            pageSize=dictionary.get("pageSize"),
            size=dictionary.get("size"),
            currentPage=dictionary.get("currentPage"),
            status=dictionary.get("status"),
            announcements=[Announcement.from_dict(ann) for ann in dictionary.get("announcements")]
        )
        for annoucement in current_cls.announcements:
            annoucement.announcement_set = current_cls
        return current_cls
    
    def get_annoucement(self, **kwargs):
        if "valid_date" in kwargs:
            return self.__get_annoucement_by_valid_date(kwargs['valid_date'])
        if "annoucement_date" in kwargs:
            return self.__get_annoucement_by_annoucement_date(kwargs['annoucement_date'])
        return None

    def __get_annoucement_by_valid_date(self, valid_date: date):
        if isinstance(valid_date, str):
            valid_date = datetime.fromisoformat(valid_date).date()
        elif isinstance(valid_date, datetime):
            valid_date = valid_date.date()
        for annoucement in self.announcements:
            if annoucement.valid_time == valid_date:
                return annoucement
        return None
    
    def __get_annoucement_by_annoucement_date(self, annoucement_date: date):
        for annoucement in self.announcements:
            if annoucement.announcement_time.date() == annoucement_date:
                return annoucement
        return None


if __name__ == "__main__":
    # Test the to_dict and from_dict methods
    # Read the JSON file
    with open('上证50.json', 'r') as file:
        data = json.load(file)

    # Initialize an AnnouncementSet object using from_dict method
    announcement_set = AnnouncementSet.from_dict(data)

    # Print the object to verify
    print(announcement_set)

    announcement = announcement_set.get_annoucement(valid_date=date(2024, 12, 13))
    announcement.get_stock_info()
    print(announcement.stock_infos_in)
    print(announcement.stock_infos_out)