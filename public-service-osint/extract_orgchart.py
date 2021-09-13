from pprint import pprint

from pdfquery import PDFQuery

import pdfminer
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

import sys


TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]


def extract_page_layouts(file):
    """
    Extracts LTPage objects from a pdf file.
    modified from: http://www.degeneratestate.org/posts/2016/Jun/15/extracting-tabular-data-from-pdfs/
    Tests show that using PDFQuery to extract the document is ~ 5 times faster than pdfminer.
    """
    laparams = LAParams()

    with open(file, mode='rb') as pdf_file:
        print("Open document %s" % pdf_file.name)
        document = PDFQuery(pdf_file).doc


        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        layouts = []
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layouts.append(device.get_result())

    return layouts


def get_text_objects(page_layout):

    texts = []

    # seperate text and rectangle elements
    for elem in current_page:
        if isinstance(elem, pdfminer.layout.LTTextBox):
            texts.append(elem)
    return texts


def flatten(lst):
    """Flattens a list of lists"""
    return [item for sublist in lst for item in sublist]


def extract_characters(element):
    """
    Recursively extracts individual characters from
    text elements.
    """
    if isinstance(element, pdfminer.layout.LTChar):
        return [element]

    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
        return flatten([extract_characters(e) for e in element])

    if isinstance(element, list):
        return flatten([extract_characters(l) for l in element])

    return []


def arrange_and_extract_text(characters, margin=0.5):
    rows = sorted(list(set(c.bbox[1] for c in characters)), reverse=True)

    row_texts = []
    for row in rows:

        sorted_row = sorted([c for c in characters if c.bbox[1] == row], key=lambda c: c.bbox[0])

        col_idx = 0
        row_text = []
        for idx, char in enumerate(sorted_row[:-1]):
            if (sorted_row[idx + 1].bbox[0] - char.bbox[2]) > margin:
                col_text = "".join([c.get_text() for c in sorted_row[col_idx:idx + 1]])
                col_idx = idx + 1
                row_text.append(col_text)
            elif idx == len(sorted_row) - 2:
                col_text = "".join([c.get_text() for c in sorted_row[col_idx:]])
                row_text.append(col_text)
        row_texts.append(row_text)
    return row_texts



if __name__ == "__main__":

    data_dir = 'data/'


    page_layouts = extract_page_layouts(sys.argv[1])
    print("Number of pages: %d" % len(page_layouts))

    current_page = page_layouts[0]
    text_objects =  get_text_objects(current_page)
    for elem in current_page:
        print(elem)
    characters = extract_characters(text_objects)
    text = arrange_and_extract_text(characters)
