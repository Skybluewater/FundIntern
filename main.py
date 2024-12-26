from data.announcement import Announcement, AnnouncementSet
from handler.stock_handler import StockHandler, AnnouncementSetHandler
from data.market_day import MarketDay

def parse_args():
        import argparse
        parser = argparse.ArgumentParser(description="Fetch and process announcements.")
        parser.add_argument("--name", type=str, required=True, help="Index name to search for announcements.")
        return parser.parse_args()

args = parse_args()

annoucement_set_handler = AnnouncementSetHandler(f"{args.name}.json")
for annoucement in annoucement_set_handler.get_annoucement():
    annoucement.get_stock_info()
    stock_infos_in = annoucement.stock_infos_in
    print(annoucement.stock_infos_in)
    print("生效日期: " + annoucement.valid_time.isoformat())
    print("发布日期: " + annoucement.announcement_time.isoformat())
    for i in stock_infos_in["证券代码"]:
        print(f"Processing stock {i}")
        stock_handler = StockHandler(i, start_date=annoucement.announcement_time, n_days=30, 
                                        announcement=annoucement, announcement_set_handler=annoucement_set_handler)
        rate, buy_date, sell_date = stock_handler.cal_reward_rate(buy_date=annoucement.announcement_time)
        end_date = stock_handler.stock.days[-1].date
        valid_date = annoucement.valid_time
        if buy_date is None and sell_date is None:
            buy_date = annoucement.announcement_time
            sell_date = annoucement.announcement_time
        
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Use Arial Unicode MS font for Chinese characters
        plt.rcParams['axes.unicode_minus'] = False  # Ensure minus sign is displayed correctly
        # Plot the stock data
        plt.figure(figsize=(10, 6))
        plt.plot(stock_handler.stock.raw_data['日期'], stock_handler.stock.raw_data['收盘'], marker='o')
        plt.xlabel('日期')
        plt.ylabel('收盘价')
        stock_name = stock_handler.stock.stock_name
        plt.title(f'{i}-{stock_name} {buy_date.isoformat()}至{end_date.isoformat()}收盘价走势')
        # Emphasize the begin date and end date
        plt.axvline(x=buy_date, color='g', linestyle='--', label='买入')
        plt.axvline(x=sell_date, color='r', linestyle='--', label=f'卖出, 收益率{rate:.2%}')
        plt.axvline(x=valid_date, color='b', linestyle='--', label=f'生效日')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        # Save the plot
        plot_filename = f'{i}_{stock_name}_{buy_date.isoformat()}_{end_date.isoformat()}_{rate:.2%}.png'
        import os
        cwd = os.getcwd()
        plot_filepath = os.path.join(cwd, args.name, plot_filename)
        os.makedirs(os.path.dirname(plot_filepath), exist_ok=True)
        plt.savefig(plot_filepath)
        plt.close()