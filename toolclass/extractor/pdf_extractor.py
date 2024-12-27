from toolclass.extractor.base_extractor import BaseExtractor
from PyPDF2 import PdfReader
from typing import List
import tabula
import pandas as pd
import pdfplumber
import re

class PDFExtractor(BaseExtractor):
    def __init__(self, announcement):
        super().__init__(announcement)

    def extract_stock_info(self, pdf_content):
        """
        extract tables info using tabula and extract core text using pdfplumber https://github.com/jsvine/pdfplumber/issues/242
        """
        def extract_tables():
            # Extract tables from the PDF file using tabula
            tables = tabula.read_pdf(pdf_content, pages='all', multiple_tables=True)
            return tables

        def extract_core_text():
            def curves_to_edges(cs):
                """See https://github.com/jsvine/pdfplumber/issues/127"""
                edges = []
                for c in cs:
                    edges += pdfplumber.utils.rect_to_edges(c)
                return edges

            # Import the PDF.
            pdf = pdfplumber.open(pdf_content)
            core_text_ls: List[str] = []

            for p in pdf.pages:
                 # Table settings.
                ts = {
                    "vertical_strategy": "explicit",
                    "horizontal_strategy": "explicit",
                    "explicit_vertical_lines": curves_to_edges(p.curves + p.edges),
                    "explicit_horizontal_lines": curves_to_edges(p.curves + p.edges),
                    "intersection_y_tolerance": 10,
                }

                # Get the bounding boxes of the tables on the page.
                bboxes = [table.bbox for table in p.find_tables(table_settings=ts)]

                def not_within_bboxes(obj):
                    """Check if the object is in any of the table's bbox."""
                    def obj_in_bbox(_bbox):
                        """See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404"""
                        v_mid = (obj["top"] + obj["bottom"]) / 2
                        h_mid = (obj["x0"] + obj["x1"]) / 2
                        x0, top, x1, bottom = _bbox
                        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
                    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

                core_text_ls.extend(p.filter(not_within_bboxes).extract_text().split("\n"))
            return core_text_ls

        def extract_stock_info():
            index_map = dict()
            index_texts = texts

            if self.announcement != None:
                index_name = self.announcement.announcement_set.index_name
            else:
                index_name = "上证50"
            
            if "部分指数样本调整名单" in texts[0]:
                index_texts = texts[1:]
            
            for idx, name in enumerate(index_texts):
                if "样本调整名单" == name[-7: -1]:
                    pattern = re.compile(r'.+\d+')
                    match = pattern.match(name)
                    if match:
                        index_map[match.group()] = idx
            
            if index_name not in index_map:
                raise ValueError("Index Name Error")
            
            return tables[index_map[index_name]]
        
        tables = extract_tables()
        texts = extract_core_text()
        stock_infos = extract_stock_info()

        stock_infos.columns = stock_infos.iloc[0]
        stock_infos = stock_infos.iloc[1:]
        stock_infos.reset_index(drop=True, inplace=True)
        # Reset index to remove the index column
        stock_infos_out = stock_infos.iloc[:, [0, 1]]
        stock_infos_in = stock_infos.iloc[:, [2, 3]]
        
        return stock_infos_in, stock_infos_out

if __name__ == "__main__":
    with open("14799.pdf", "rb") as f:
        pdf_extractor = PDFExtractor(None)
        print(pdf_extractor.extract_stock_info(f))