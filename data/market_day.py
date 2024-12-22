import os
import pandas as pd
from datetime import date
from bisect import bisect_left, bisect_right

class BaseMarketDay:
    _instance = None
    _market_days = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BaseMarketDay, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def __get_market_day():
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'market_day.csv')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as f:
                BaseMarketDay._market_days = pd.read_csv(f)
        else:
            import akshare as ak
            today = date.today().isoformat().replace("-" , "")
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date=today, adjust="")
            dates = stock_zh_a_hist_df['日期']
            dates.to_csv(file_path, index=False, header=False, encoding='utf-8')
    
    @staticmethod
    def get_market_days(start_date: date, period: int):
        if BaseMarketDay._market_days is None:
            BaseMarketDay.__get_market_day()

        start_date_str = start_date.isoformat()
        
    
    @staticmethod
    def get_market_days(start_date: date, *args):
        if BaseMarketDay._market_days is None:
            BaseMarketDay.__get_market_day()
        assert len(args) == 1, "Invalid number of arguments"
        if isinstance(args[0], int):
            start_date_str = start_date.isoformat()
            period = args[0]
            dates = BaseMarketDay._market_days['日期']
        
            # Perform binary search to find the start date index
            left = bisect_left(dates, start_date_str)

            # Get the period dates
            end_index = min(left + period, len(dates))
            return dates[left:end_index].tolist()
        elif isinstance(args[0], date):
            end_date = args[0]
            start_date_str = start_date.isoformat()
            end_date_str = end_date.isoformat()
            dates = BaseMarketDay._market_days['日期']

            # Perform binary search to find the start date index
            left = bisect_left(dates, start_date_str)
            right = bisect_right(dates, end_date_str)

            return dates[left:right].tolist()
        else:
            raise ValueError("Invalid argument type")


class MarketDay(BaseMarketDay):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    market_day = MarketDay()
    print(market_day.get_market_days(date(2021, 1, 5), 10))
    print(market_day.get_market_days(date(2021, 1, 5), date(2021, 1, 15)))