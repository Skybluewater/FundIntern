from extractor.base_extractor import BaseExtractor
import pandas as pd

class XLSXExtractor(BaseExtractor):
    def __init__(self, announcement):
        super().__init__(announcement)
    
    def extract_stock_info(self, file_handler):
        index_name = self.announcement.announcement_set.index_name
        # index_name = "上证50"

        def handle_sheet(sheet_name):
            # Read the excel file from BytesIO
            excel_data = pd.read_excel(file_handler, sheet_name=sheet_name)
            # filter table rows using index_name
            mask = excel_data['指数简称'].str.contains(index_name)
            filtered_data = excel_data[mask]
            # Filter columns using column names
            filtered_data = filtered_data[['证券代码', '证券简称']]
            # Reset index to remove the index column
            filtered_data.reset_index(drop=True, inplace=True)
            # Rename columns
            filtered_data.columns = ['证券代码', '证券简称']
            return filtered_data
        
        # Return the filtered data as a pandas DataFrame
        
        stock_infos_in = handle_sheet("调入")
        stock_infos_out = handle_sheet("调出")
        stock_infos_in['证券代码'] = stock_infos_in['证券代码'].astype(str)
        stock_infos_out['证券代码'] = stock_infos_out['证券代码'].astype(str)
        return stock_infos_in, stock_infos_out


if __name__ == "__main__":
    with open("14501.xlsx", "rb") as f:
        pdf_extractor = XLSXExtractor(None)
        pdf_extractor.extract_stock_info(f)