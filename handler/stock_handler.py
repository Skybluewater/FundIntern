from data.announcement import Announcement, AnnouncementSet
from data.stock import Stock
from data.market_day import MarketDay
from datetime import date, timedelta
from reader.reader import Reader

class AnnouncementSetHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.reader = Reader(file_path)
        self.annoucement_set = AnnouncementSet.from_dict(self.reader.content)
    
    def get_annoucement(self, **kwargs):
        if kwargs:
            if "announcement_time" in kwargs:
                for annoucement in self.annoucement_set.announcements:
                    if annoucement.announcement_time.date() == kwargs['announcement_time']:
                        yield annoucement
            elif "valid_time" in kwargs:
                for annoucement in self.annoucement_set.announcements:
                    if annoucement.valid_time.date() == kwargs['valid_time']:
                        yield annoucement
        else:
            for annoucement in self.annoucement_set.announcements:
                yield annoucement


class AnnouncementHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.reader = Reader(file_path)
        self.annoucement = Announcement.from_dict(self.reader.content)


class StockHandler:
    def __init__(self, stock_code, **kwargs):
        self.stock_code = stock_code
        self.stock = None
        self.announcement = None
        self.announcement_set = None
        if "start_date" in kwargs and "end_date" in kwargs:
            self.stock = self.__get_start_end_stock_info(kwargs['start_date'], kwargs['end_date'])
        elif "start_date" in kwargs and "n_days" in kwargs:
            self.stock = self.__get_period_stock_info(kwargs['start_date'], kwargs['n_days'])
    
    def __get_start_end_stock_info(self, start_date: date, end_date: date):
        market_days = MarketDay.get_market_days(start_date, end_date)
        return Stock(stock_code=self.stock_code, start_date=market_days[0], end_date=market_days[-1])
    
    def __get_period_stock_info(self, start_date: date, n_days: int):
        market_days = MarketDay.get_market_days(start_date, n_days)
        return Stock(stock_code=self.stock_code, start_date=market_days[0], end_date=market_days[-1])

    def __is_valid(self):
        if not self.stock or not self.stock.days or len(self.stock.days) == 0:
            return False
        if not self.announcement:
            return False
        return True
    
    def cal_stock(self):
        if not self.stock.is_valid():
            return None
        highest_date = self.stock.days[0].date
        highest_price = self.stock.days[0].high
        lowest_date = self.stock.days[0].date
        lowest_price = self.stock.days[0].low
        for i in self.stock.days:
            if i.high > highest_price:
                highest_date = i.date
                highest_price = i.high
            if i.low < lowest_price:
                lowest_date = i.date
                lowest_price = i.low
        return highest_date, highest_price, lowest_date, lowest_price

if __name__ == "__main__":
    annoucement_set_handler = AnnouncementSetHandler("上证50.json")
    for annoucement in annoucement_set_handler.get_annoucement(valid_time=date(2022, 12, 9)):
        annoucement.get_stock_info()
        stock_infos_in = annoucement.stock_infos_in
        print(annoucement.stock_infos_in)
        for i in stock_infos_in["证券代码"]:
            # stock_handler = StockHandler(i, start_date=annoucement.valid_time, end_date=annoucement.valid_time + timedelta(days=10))
            stock_handler = StockHandler(i, start_date=annoucement.announcement_time, n_days=30)
            print(stock_handler.cal_stock())
            last_date = MarketDay.get_market_days(annoucement.valid_time, 30)[-1]
            stock_handler = StockHandler(i, start_date=annoucement.announcement_time, end_date=last_date)
            print(stock_handler.cal_stock())
        # break
