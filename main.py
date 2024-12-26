from data.announcement import Announcement, AnnouncementSet
from handler.stock_handler import StockHandler, AnnouncementSetHandler
from data.market_day import MarketDay

annoucement_set_handler = AnnouncementSetHandler("上证50.json")
for annoucement in annoucement_set_handler.get_annoucement():
    annoucement.get_stock_info()
    stock_infos_in = annoucement.stock_infos_in
    print(annoucement.stock_infos_in)
    print("生效日期: " + annoucement.valid_time.isoformat())
    print("发布日期: " + annoucement.announcement_time.isoformat())
    for i in stock_infos_in["证券代码"]:
        stock_handler = StockHandler(i, start_date=annoucement.announcement_time, n_days=30, 
                                        announcement=annoucement, announcement_set_handler=annoucement_set_handler)
        print(stock_handler.cal_reward_rate(buy_date=annoucement.announcement_time))
