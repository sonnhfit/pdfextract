import pdfminer
import cv2
import os
import numpy as np
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdf2image import convert_from_path


def convert_pdf_to_nunpy_image(pdf_path):
    """
    :param pdf_path: đường dẫn file pdf
    :return: Trả về list ảnh ở dạng numpy array đây là dạng ảnh của opencv
    """
    # 500 ở đây là 500pdi
    pages = convert_from_path(pdf_path, 500)
    print(type(pages))
    result = map(np.array, pages)
    return list(result)


def parse_obj(lt_objs, MEDIA_Y1):
    list_codinate = []
    # loop over the object list
    for obj in lt_objs:
        sub_region = {}
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            subbox_tex = obj.get_text()
            sub_region['cordinate'] = [int(obj.x0), int(MEDIA_Y1 - obj.y0), int(obj.x1), int(MEDIA_Y1 - obj.y1)]
            sub_region['text'] = subbox_tex
            list_codinate.append(sub_region)
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs)
    return list_codinate


def get_text_box(pdf_path):
    """
    :return: trả về list các box theo từng page ở dạng như thế này
    với region là danh sách tọa độ củ các block text
    còn media box là tọa độ size của từng page điểm x0=0, y0=0
    [
      { #page 1
        "region": [
            {
                "cordinate": [x0, y0, x1, y1]
                "text": "day la text"
             },
             {
                "cordinate": [x0, y0, x1, y1]
                "text": "day la text"
             },
             {
                "cordinate": [x0, y0, x1, y1]
                "text": "day la text"
             }
          ],
        "media_box":[
            x1, y1
          ]
      },
      { #page 2
        "region": [
                    {
                        "cordinate": [x0, y0, x1, y1]
                        "text": "day la text"
                     },
                     {
                        "cordinate": [x0, y0, x1, y1]
                        "text": "day la text"
                     },
                     {
                        "cordinate": [x0, y0, x1, y1]
                        "text": "day la text"
                     }
                  ],
                "media_box":[
                    x1, y1
                  ]
      }
    ]
    """
    fp = open(pdf_path, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    list_all_box = []
    # loop over all pages in the document
    for page in PDFPage.create_pages(document):
        list_item = {}
        interpreter.process_page(page)
        layout = device.get_result()
        media_texbox = (int(page.mediabox[2]), int(page.mediabox[3]))
        MEDIA_Y1 = int(page.mediabox[3])
        sub_box = parse_obj(layout._objs, MEDIA_Y1)
        list_item['region'] = sub_box
        list_item['media_box'] = media_texbox
        list_all_box.append(list_item)

    return list_all_box
