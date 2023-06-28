import csv
import io
import re
from io import StringIO
from typing import List
import numpy as np
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def get_pdf_output(fp: str) -> io.StringIO:
    output_string = StringIO()
    with open(fp, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for idx, page in enumerate(PDFPage.create_pages(doc)):
            if idx > 10:
                break
            print(f"got page: {idx}")
            interpreter.process_page(page)
    return output_string


def find_data_start_stops(splits: str) -> (List[int], List[int]):
    starts = list()
    stops = list()
    got_start = False
    for idx, split in enumerate(splits):
        if not split.isascii():
            if not got_start:
                starts.append(idx)
                got_start = True
        if (split.isascii()) and (got_start == True):
            stops.append(idx)
            got_start = False
    return starts, stops


def parse_columns(starts: List[int], stops: List[int], splits: List[str]) -> List:
    columns = list()
    for start, stop in zip(starts, stops):
        column = ''.join(re.split(r'\\.....-| \\.....|\\..... | \s', ascii(' '.join(splits[start:stop])))).split(' ')
        column[0] = column[0][1:]
        column[-1] = column[-1][:-1]
        columns.append(column)
    return columns


def format_columns_to_array(columns: List) -> np.ndarray:
    max_len = max(len(x) for x in columns)
    array_data = np.empty((max_len, len(columns)), dtype=object)
    for idx, column in enumerate(columns):
        array_data[:len(column), idx] = column

    return array_data


def write_to_csv(array_data: np.ndarray, out_file: str = "columns.csv"):
    with open(out_file, 'w') as f:
        wr = csv.writer(f, delimiter=',')
        wr.writerows(array_data)


def main(input_file: str, output_file: str):
    output_string = get_pdf_output(input_file)
    splits = re.split('\n', output_string.getvalue())
    starts, stops = find_data_start_stops(splits)
    columns = parse_columns(starts, stops, splits)
    array_data = format_columns_to_array(columns)
    write_to_csv(array_data, output_file)


if __name__ == "__main__":
    main(input_file='./nssats_directory_2018.pdf', output_file='./test.csv')
