import pandas as pd
import akshare as ak
from datetime import date

class Stock:
    class StockPerDay():
        def __init__(self, date, open, close, high, low, volume):
            self.date = date
            self.open = open
            self.close = close
            self.high = high
            self.low = low
            self.volume = volume
    
    def __init__(self, stock_code: str, **kwargs):
        self.stock_code = stock_code
        
        if "stock_name" in kwargs:
            self.stock_name = kwargs['stock_name']
        else:
            stock_individual_info_em_df = ak.stock_individual_info_em(symbol=stock_code)
            self.stock_name = stock_individual_info_em_df.iloc[1]['value']
        
        if "start_date" not in kwargs or "end_date" not in kwargs:
            raise ValueError("start_date and end_date must be provided")
        else:
            start_date = kwargs['start_date']
            end_date = kwargs['end_date']
            stock_per_day = self.get_stock_per_day(start_date, end_date)
        
        self.days = []
        for index, row in stock_per_day.iterrows():
            self.days.append(self.StockPerDay(row['日期'], row['开盘'], row['收盘'], row['最高'], row['最低'], row['成交量']))
    
    def get_stock_per_day(self, start_date: date, end_date: date):
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date_str, end_date=end_date_str, adjust="")
        return stock_zh_a_hist_df