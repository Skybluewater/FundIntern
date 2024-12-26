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
        self.rate = 0
        self.buy_date = None
        self.sell_date = None
        self.announcement = kwargs["announcement"] if "announcement" in kwargs else None
        self.announcement_set_handler = kwargs["announcement_set_handler"] if "announcement_set_handler" in kwargs else None
        if "start_date" in kwargs and "end_date" in kwargs:
            self.stock = self.__get_start_end_stock_info(kwargs['start_date'], kwargs['end_date'])
        elif "start_date" in kwargs and "n_days" in kwargs:
            self.stock = self.__get_period_stock_info(kwargs['start_date'], kwargs['n_days'])
        else:
            raise ValueError("start_date and end_date or start_date and n_days must be provided")
    
    def __get_start_end_stock_info(self, start_date: date, end_date: date):
        market_days = MarketDay.get_market_days(start_date, end_date)
        return Stock(stock_code=self.stock_code, start_date=market_days[0], end_date=market_days[-1])
    
    def __get_period_stock_info(self, start_date: date, n_days: int):
        market_days = MarketDay.get_market_days(start_date, n_days)
        return Stock(stock_code=self.stock_code, start_date=market_days[0], end_date=market_days[-1])

    def __is_valid(self):
        if not self.stock or not self.stock.days or len(self.stock.days) == 0:
            return False
        return True
    
    from typing import Union

    def cal_reward_rate(self, **kwargs) -> Union[tuple[float, date, date], None]:
        """
        Calculate the reward rate for a stock.
        This method calculates the rough reward rate for a stock based on its historical price data.
        It determines the best buy and sell dates to maximize the reward rate.
        Args:
            **kwargs: Arbitrary keyword arguments. 
                      - announcement_date (optional): A specific date to start calculating the reward rate from.
                      - valid_date (optional): A specific date to start calculating the reward rate.
        Returns:
            tuple: A tuple containing:
                - reward_rate_rough (float): The calculated rough reward rate.
                - buy_date (datetime.date or None): The date to buy the stock to achieve the reward rate.
                - valid_date (datetime.date or None): The date to sell the stock to achieve the reward rate.
        """
        if not self.__is_valid():
            return None
        reward_rate_rough = 0
        buy_date = None
        sell_date = None
        potential_buy_date = None
        if "announcement_date" and "valid_date" in kwargs:
            announcement_date = kwargs['announcement_date']
            valid_date = kwargs['valid_date']
            lowest_price = self.stock.get_stock_by_date(valid_date).close
            potential_buy_date = valid_date
            for day in self.stock.days:
                if day.date < valid_date:
                    continue
                reward_rate_rough_temp = (day.close - lowest_price) / lowest_price
                if reward_rate_rough_temp > reward_rate_rough:
                    buy_date = potential_buy_date
                    sell_date = day.date
                    reward_rate_rough = reward_rate_rough_temp
        else:
            lowest_price = self.stock.days[0].close
            potential_buy_date = self.stock.days[0].date
            for day in self.stock.days:
                if day.low < lowest_price:
                    lowest_price = day.close
                    potential_buy_date = day.date
                reward_rate_rough_temp = (day.close - lowest_price) / lowest_price
                if reward_rate_rough_temp > reward_rate_rough:
                    buy_date = potential_buy_date
                    sell_date = day.date
                    reward_rate_rough = reward_rate_rough_temp
        self.rate = reward_rate_rough
        self.buy_date = buy_date
        self.sell_date = sell_date
        return reward_rate_rough, buy_date, sell_date

    def get_reward_rate(self, start_date: date, end_date: date):
        return (self.stock.get_stock_by_date(end_date).close - self.stock.get_stock_by_date(start_date).close) / self.stock.get_stock_by_date(start_date).close
    
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
    annoucement_set_handler = AnnouncementSetHandler("上证180.json")
    for annoucement in annoucement_set_handler.get_annoucement():
        annoucement.get_stock_info()
        stock_infos_in = annoucement.stock_infos_in
        print(annoucement.stock_infos_in)
        print("生效日期: " + annoucement.valid_time.date().isoformat())
        print("发布日期: " + annoucement.announcement_time.date().isoformat())
        for i in stock_infos_in["证券代码"]:
            # stock_handler = StockHandler(i, start_date=annoucement.valid_time, end_date=annoucement.valid_time + timedelta(days=10))
            stock_handler = StockHandler(i, start_date=annoucement.announcement_time, n_days=30, 
                                         announcement=annoucement, announcement_set_handler=annoucement_set_handler)
            print(stock_handler.cal_stock())
            last_date = MarketDay.get_market_days(annoucement.valid_time, 30)[-1]
            stock_handler = StockHandler(i, start_date=annoucement.announcement_time, end_date=last_date, 
                                         announcement=annoucement, announcement_set_handler=annoucement_set_handler)
            print(stock_handler.cal_stock())
            print(stock_handler.cal_reward_rate())
        # break
