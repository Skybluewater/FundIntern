import pandas as pd
import akshare as ak
from datetime import date
from typing import List
from dataclasses import dataclass
from data.serializable import Serializable

@dataclass
class Stock(Serializable):
    @dataclass
    class StockPerDay(Serializable):
        def __init__(self, date, open, close, high, low, volume):
            self.date: date = date
            self.open = open
            self.close = close
            self.high = high
            self.low = low
            self.volume = volume
            self.raw_data = None
        
        def to_dict(self):
            return {
                "日期": self.date.isoformat(),
                "开盘": self.open,
                "收盘": self.close,
                "最高": self.high,
                "最低": self.low,
                "成交量": self.volume
            }
        
        def from_dict(self, dictionary):
            return super().from_dict(dictionary)
    
    def __init__(self, stock_code: str, **kwargs):
        self.stock_code = stock_code
        
        if "stock_name" in kwargs:
            self.stock_name = kwargs['stock_name']
        else:
            try:
                stock_individual_info_em_df = ak.stock_individual_info_em(symbol=stock_code)
                self.stock_name = stock_individual_info_em_df.iloc[1]['value']
            except Exception as e:
                print(f"Failed to retrieve stock individual info: {e}")
        
        if "start_date" not in kwargs or "end_date" not in kwargs:
            raise ValueError("start_date and end_date must be provided")
        else:
            start_date = kwargs['start_date']
            end_date = kwargs['end_date']
            stock_per_day = self.__get_stock_per_day(start_date, end_date)
            self.raw_data = stock_per_day
        self.days: List[Stock.StockPerDay] = []
        for index, row in stock_per_day.iterrows():
            self.days.append(self.StockPerDay(row['日期'], row['开盘'], row['收盘'], row['最高'], row['最低'], row['成交量']))
    
    def get_stock_by_date(self, date: date):
        for day in self.days:
            if day.date == date:
                return day
        raise ValueError(f"Stock data not found for date: {date}")

    def __get_stock_per_day(self, start_date: date, end_date: date):
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        try:
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date_str, end_date=end_date_str, adjust="")
        except Exception as e:
            print(f"Failed to retrieve stock history: {e}")
            return pd.DataFrame()
        return stock_zh_a_hist_df
    
    def is_valid(self):
        return self.days is not None and len(self.days) > 0

    def to_dict(self):
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "days": [day.to_dict() for day in self.days]
        }
    
    def from_dict(self, dictionary):
        return super().from_dict(dictionary)

if __name__ == "__main__":
    stock = Stock("000001", start_date=date(2021, 1, 1), end_date=date(2021, 1, 10))
    print(stock.to_dict())
    #checksshkey