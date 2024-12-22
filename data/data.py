# a data class to store infos of the announcement
# including total_cnt, page_size, size, currentPage, status etc
from dataclasses import dataclass
from typing import List, Any
from datetime import datetime
from data.serializable import Serializable

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
    
    def from_dict(self, dictionary):
        pass

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
    
    def from_dict(self, dictionary):
        pass
