import os
import pandas as pd
import matplotlib.pyplot as plt
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

# Init plot settings
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Use Arial Unicode MS font for Chinese characters
plt.rcParams['axes.unicode_minus'] = False  # Ensure minus sign is displayed correctly
# plt.figure(dpi=800, figsize=(15, 6))

def save_image_per_stock(stock_code, stock_handler, buy_date, sell_date, valid_date, start_date, end_date, rate, index_handler: StockHandler):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    line4, = ax1.plot(stock_handler.stock.raw_data['日期'], stock_handler.stock.raw_data['收盘'], marker='o', color='b', label='股票收盘价')
    line5, = ax2.plot(index_handler.stock.raw_data['日期'], index_handler.stock.raw_data['收盘'], marker='x', color='r', label='指数收盘价')
    ax1.set_xlabel('日期')
    ax1.set_ylabel('股票收盘价', color='b')
    ax2.set_ylabel('指数收盘价', color='r')
    stock_name = stock_handler.stock.stock_name
    
    plt.title(f'{stock_code}-{stock_name} {buy_date.isoformat()}至{end_date.isoformat()}收盘价走势')

    index_rate = index_handler.rate
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
    cwd = os.getcwd()
    plot_filepath = os.path.join(cwd, args.name, plot_filename)
    os.makedirs(os.path.dirname(plot_filepath), exist_ok=True)
    plt.savefig(plot_filepath)
    plt.close()

def get_per_stock_reward_rate(stock_code, annoucement: Announcement, annoucement_set_handler: AnnouncementSetHandler, index_handler: StockHandler, **kwargs):
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

def get_per_stock_reward_rate_by_date(stock_code, annoucement: Announcement, annoucement_set_handler: AnnouncementSetHandler, index_handler: StockHandler, end_date, **kwargs):
    print(f"Processing stock {stock_code}")
    if "stock_handler" in kwargs:
        stock_handler = kwargs["stock_handler"]
    else:
        stock_handler = StockHandler(stock_code, start_date=annoucement.announcement_time, n_days=30, 
                                     announcement=annoucement, announcement_set_handler=annoucement_set_handler)
    rate = stock_handler.get_reward_rate(start_date=annoucement.valid_time, end_date=end_date)
    return stock_handler, rate

def get_stock_reward_rate(annoucement: Announcement, annoucement_set_handler: AnnouncementSetHandler, **kwargs):
    annoucement.get_stock_info()
    
    stock_infos_in = annoucement.stock_infos_in
    stock_dic = {}

    print(annoucement.stock_infos_in)
    print("生效日期: " + annoucement.valid_time.isoformat())
    print("发布日期: " + annoucement.announcement_time.isoformat())
    index_handler = StockHandler(args.index, start_date=annoucement.announcement_time, n_days=30, 
                                    announcement=annoucement, announcement_set_handler=annoucement_set_handler)
    index_handler.cal_reward_rate(announcement_date=annoucement.announcement_time, valid_date=annoucement.valid_time)
    for i in stock_infos_in["证券代码"]:
        stock_handler, rate, *_ = get_per_stock_reward_rate(i, annoucement, annoucement_set_handler, index_handler)
        stock_dic[i] = (stock_handler, rate)
    
    """
    Calculate the reward rate of the index by weight
    """

    days = []
    for day in index_handler.stock.days:
        if day.date >= annoucement.valid_time:
            days.append(day.date)
    
    if "weights" in kwargs and kwargs["weights"] is not None:
        # weights should be a dictionary, key: stock code, value: rate
        weights = kwargs["weights"]
    else:
        weights = {i: 1 / len(stock_infos_in["证券代码"]) for i in stock_infos_in["证券代码"]}
    
    def cal_best_rate():
        best_rate = 0
        for key, val in stock_dic.items():
            stock_handler, rate = val
            best_rate += rate * weights[key]
        return best_rate
    
    best_rate = cal_best_rate()
    max_index_rate = 0
    max_stock_rate = 0

    print(f"最佳收益率: {best_rate:.2%}")
    
    # Calculate the reward rate of the index
    reward_record_table = pd.DataFrame(columns=["n_days", "date", "stock_reward_rate", "index_reward_rate"])

    def cal_rate_per_day(end_date):
        rate = 0
        for key, val in stock_dic.items():
            stock_handler, _ = val
            rate += get_per_stock_reward_rate_by_date(key, annoucement, annoucement_set_handler, index_handler, end_date, stock_handler=stock_handler)[1] * weights[key]
        return rate
    
    for idx, day in enumerate(days):
        stock_reward_rate = cal_rate_per_day(day)
        index_reward_rate = index_handler.get_reward_rate(annoucement.valid_time, day)
        max_index_rate = max(max_index_rate, index_reward_rate)
        max_stock_rate = max(max_stock_rate, stock_reward_rate)
        print(f"N = {idx} {day.isoformat()} 股票收益率: {stock_reward_rate:.2%}, 指数收益率: {index_reward_rate:.2%}")    
        reward_record_table.loc[idx] = {"n_days": idx, "date": day, "stock_reward_rate": stock_reward_rate, "index_reward_rate": index_reward_rate}

    csv_filename = f'{annoucement.valid_time.isoformat()}_{index_handler.stock.days[-1].date.isoformat()}.csv'
    cwd = os.getcwd()
    csv_filepath = os.path.join(cwd, args.name, csv_filename)
    os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
    reward_record_table.to_csv(csv_filepath, index=False, header=True)

    def save_to_png():
        line1, = plt.plot(reward_record_table["n_days"], reward_record_table["stock_reward_rate"], marker='o')
        line2, = plt.plot(reward_record_table["n_days"], reward_record_table["index_reward_rate"], marker='x')
        plt.xlabel('N交易日')
        plt.ylabel('收益率')
        plt.title(f'{annoucement.valid_time.isoformat()}至{index_handler.stock.days[-1].date.isoformat()}收益率走势')
        plt.legend(handles=[line1, line2], labels=[f'股票收益率, 最高为{max_stock_rate:.2%}', f'指数收益率, 最高为{max_index_rate:.2%}'])
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(csv_filepath.replace(".csv", ".png"))
        plt.close()
    
    save_to_png()
    return index_handler, best_rate, max_index_rate
        

def main():
    annoucement_set_handler = AnnouncementSetHandler(f"{args.name}.json")
    weights = None
    reward_table = pd.DataFrame(columns=["valid_date", "end_date", "best_rate", "max_index_rate"])
    for annoucement in annoucement_set_handler.get_annoucement():
        if os.path.exists(annoucement.file_name.split(".")[0] + ".csv"):
            with open(annoucement.file_name.split(".")[0] + ".csv", "r") as f:
                weights = {line.split(",")[0]: float(line.split(",")[1]) for line in f}
        else:
            weights = None
        index_handler, best_rate, max_index_rate = get_stock_reward_rate(annoucement, annoucement_set_handler, weights=weights)
        reward_table.loc[len(reward_table)] = [annoucement.valid_time, index_handler.stock.days[-1].date, best_rate, max_index_rate]
    reward_table.to_csv(f'{args.name}_reward_table.csv', index=False, header=True)

if __name__ == "__main__":
    main()
