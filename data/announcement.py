# a data class to store infos of the announcement
# including total_cnt, page_size, size, currentPage, status etc
from dataclasses import dataclass
from typing import List, Any
from datetime import datetime
from data.serializable import Serializable
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

    def to_dict(self):
        return {
            "headline": self.headline,
            "ann_time": self.announcement_time.date().isoformat(),
            "id": self.id,
            "content": self.content,
            "file_name": self.file_name,
            "valid_time": self.valid_time.date().isoformat() if self.valid_time else None,
        }
    
    @classmethod
    def from_dict(cls, dictionary):
        return cls(
            headline=dictionary.get("headline"),
            announcement_time=datetime.fromisoformat(dictionary.get("ann_time")),
            id=dictionary.get("id"),
            content=dictionary.get("content"),
            file_name=dictionary.get("file_name"),
            valid_time=datetime.fromisoformat(dictionary.get("valid_time")) if dictionary.get("valid_time") else None,
            announcement_set=None  # This should be set separately if needed
        )

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


if __name__ == "__main__":
    # Test the to_dict and from_dict methods
    # Read the JSON file
    with open('./上证50.json', 'r') as file:
        data = json.load(file)

    # Initialize an AnnouncementSet object using from_dict method
    announcement_set = AnnouncementSet.from_dict(data)

    # Print the object to verify
    print(announcement_set)
