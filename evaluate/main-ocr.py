from src.models.ocr.paddleocr_model import PaddleOCRModel
# from src.models.ocr.easyocr_model import EasyOCRModel
# from src.models.ocr.tesseract_model import TeseractModel


if __name__=="__main__":
    # model = EasyOCRModel()
    model = PaddleOCRModel()
    # model = TeseractModel()
    output = model.evaluate("testset")
    print(output)


    