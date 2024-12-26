from data.announcement import Announcement, AnnouncementSet
from handler.stock_handler import StockHandler, AnnouncementSetHandler
from data.market_day import MarketDay

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Fetch and process announcements.")
    parser.add_argument("--name", type=str, required=True, help="Index name to search for announcements.")
    parser.add_argument("--save_image", type=str, help="Valid date of the announcement.")
    parser.add_argument("--index", type=str, help="Index code to compare.")
    return parser.parse_args()

args = parse_args()

def save_image_per_stock(stock_code, stock_handler, buy_date, sell_date, valid_date, start_date, end_date, rate, index_handler: StockHandler):
    # Init plot settings
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Use Arial Unicode MS font for Chinese characters
    plt.rcParams['axes.unicode_minus'] = False  # Ensure minus sign is displayed correctly
    
    # Plot the stock data
    plt.figure(dpi=800, figsize=(15, 6))

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    line4, = ax1.plot(stock_handler.stock.raw_data['日期'], stock_handler.stock.raw_data['收盘'], marker='o', color='b', label='股票收盘价')
    line5, = ax2.plot(index_handler.stock.raw_data['日期'], index_handler.stock.raw_data['收盘'], marker='x', color='r', label='指数收盘价')
    ax1.set_xlabel('日期')
    ax1.set_ylabel('股票收盘价', color='b')
    ax2.set_ylabel('指数收盘价', color='r')
    stock_name = stock_handler.stock.stock_name
    
    plt.title(f'{stock_code}-{stock_name} {buy_date.isoformat()}至{end_date.isoformat()}收盘价走势')

    index_rate = index_handler.get_reward_rate(buy_date, sell_date)
    # Emphasize the begin date and end date
    line1 = ax1.axvline(x=buy_date, color='g', linestyle='--', label='买入日{}'.format(buy_date.isoformat()))
    line2 = ax1.axvline(x=sell_date, color='r', linestyle='--', label=f'卖出日{sell_date.isoformat()}, 股票收益率{rate:.2%}')
    line3 = ax1.axvline(x=valid_date, color='b', linestyle='--', label=f'生效日{valid_date.isoformat()}, 指数收益率{index_rate:.2%}')
    
    plt.legend(handles=[line1, line2, line3])
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    plot_filename = f'{stock_code}_{stock_name}_{start_date.isoformat()}_{end_date.isoformat()}_{rate:.2%}.png'
    import os
    cwd = os.getcwd()
    plot_filepath = os.path.join(cwd, args.name, plot_filename)
    os.makedirs(os.path.dirname(plot_filepath), exist_ok=True)
    plt.savefig(plot_filepath)
    plt.close()

def get_per_stock_reward_rate(stock_code, annoucement: Announcement, annoucement_set_handler: AnnouncementSetHandler, index_handler: StockHandler):
    print(f"Processing stock {stock_code}")
    stock_handler = StockHandler(stock_code, start_date=annoucement.announcement_time, n_days=30, 
                                    announcement=annoucement, announcement_set_handler=annoucement_set_handler)
    rate, buy_date, sell_date = stock_handler.cal_reward_rate(announcement_date=annoucement.announcement_time,
                                                                valid_date=annoucement.valid_time)
    start_date = stock_handler.stock.days[0].date
    end_date = stock_handler.stock.days[-1].date
    valid_date = annoucement.valid_time
    if buy_date is None:
        buy_date = annoucement.valid_time
    if sell_date is None:
        sell_date = annoucement.valid_time
    
    save_image_per_stock(stock_code, stock_handler, buy_date, sell_date, valid_date, start_date, end_date, rate, index_handler)
    return stock_handler, rate, buy_date, sell_date

def get_stock_reward_rate(annoucement: Announcement, annoucement_set_handler: AnnouncementSetHandler):
    annoucement.get_stock_info()
    stock_infos_in = annoucement.stock_infos_in
    print(annoucement.stock_infos_in)
    print("生效日期: " + annoucement.valid_time.isoformat())
    print("发布日期: " + annoucement.announcement_time.isoformat())
    index_handler = StockHandler(args.index, start_date=annoucement.announcement_time, n_days=30, 
                                    announcement=annoucement, announcement_set_handler=annoucement_set_handler)
    for i in stock_infos_in["证券代码"]:
        get_per_stock_reward_rate(i, annoucement, annoucement_set_handler, index_handler)
        

def main():
    annoucement_set_handler = AnnouncementSetHandler(f"{args.name}.json")
    for annoucement in annoucement_set_handler.get_annoucement():
        get_stock_reward_rate(annoucement, annoucement_set_handler)

if __name__ == "__main__":
    main()
