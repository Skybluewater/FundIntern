import akshare as ak

# https://akshare.akfamily.xyz/data/index/index.html#id22
# stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol="sh000001", start_date="20241129", end_date="20241220")
# print(stock_zh_index_daily_em_df)

# https://akshare.akfamily.xyz/data/index/index.html#id23
# index_stock_cons_weight_csindex_df = ak.index_stock_cons_weight_csindex(symbol="000016")
# print(index_stock_cons_weight_csindex_df)

# index_stock_cons_weight_csindex_df = ak.index_stock_cons_weight_csindex(symbol="000016")
# print(index_stock_cons_weight_csindex_df)

import akshare as ak

index_stock_cons_weight_csindex_df = ak.index_stock_cons_weight_csindex(symbol="000016")
print(index_stock_cons_weight_csindex_df)

index_detail_hist_cni_df = ak.index_detail_hist_cni(symbol='000300', date='202201')
print(index_detail_hist_cni_df)

index_detail_hist_cni_df = ak.index_detail_hist_cni(symbol='sh000001', date='202201')
print(index_detail_hist_cni_df)