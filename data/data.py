# a data class to store infos of the announcement
# including total_cnt, page_size, size, currentPage, status etc
from dataclasses import dataclass
from typing import List, Any
from datetime import datetime

@dataclass
class Announcement:
    headline: str
    ann_time: datetime
    id: str
    content: str
    pdf: str
    valid_time: datetime
    ann_set: 'AnnouncementSet'

    def to_dict(self):
        return {
            "headline": self.headline,
            "ann_time": self.ann_time.date().isoformat(),
            "id": self.id,
            "content": self.content,
            "pdf": self.pdf,
            # "valid_time": self.valid_time.date().isoformat(),
        }
    

@dataclass
class AnnouncementSet:
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
