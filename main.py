import akshare as ak
from extractor import Extractor
from announcement import Announcement

announcement = Announcement(None)
extractor = Extractor(announcement)
announcement.extractor = extractor

stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol="sh000001")
print(stock_zh_index_daily_df)
stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)
#https://akshare.akfamily.xyz/data/stock/stock.html#id21
stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="")
print(stock_zh_a_hist_df)