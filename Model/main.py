import copy
import re
import tempfile
from pathlib import Path
from typing import List, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import PyPDF2
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from paddleocr import PaddleOCR, PPStructure
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, T5ForConditionalGeneration, T5Tokenizer, MarianMTModel, MarianTokenizer
from utils import fw_fill_ja, fw_fill_vi
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms import transforms
import torch
import random
import cv2
import os

seed = 1234
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

CATEGORIES2LABELS = {
    0: "bg",
    1: "text",
    2: "title",
    3: "list",
    4: "table",
    5: "figure"
}
MODEL_PATH = "model_196000.pth"
def get_instance_segmentation_model(num_classes):
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )
    return model

class InputPdf(BaseModel):
    """Input PDF file."""
    input_pdf: UploadFile = Field(..., title="Input PDF file")


class TranslateApi:
    """Translator API class.

    Attributes
    ----------
    app: FastAPI
        FastAPI instance
    temp_dir: tempfile.TemporaryDirectory
        Temporary directory for storing translated PDF files
    temp_dir_name: Path
        Path to the temporary directory
    font: ImageFont
        Font for drawing text on the image
    layout_model: PPStructure
        Layout model for detecting text blocks
    ocr_model: PaddleOCR
        OCR model for detecting text in the text blocks
    translate_model: MarianMTModel
        Translation model for translating text
    translate_tokenizer: MarianTokenizer
        Tokenizer for the translation model
    """
    DPI = 300
    FONT_SIZE_VIETNAMESE = 40
    FONT_SIZE_JAPANESE = 32

    def __init__(self):
        self.app = FastAPI()
        self.app.add_api_route(
            "/translate_pdf/",
            self.translate_pdf,
            methods=["POST"],
            response_class=FileResponse,
        )
        self.app.add_api_route(
            "/clear_temp_dir/",
            self.clear_temp_dir,
            methods=["GET"],
        )

        self.__load_models()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = Path(self.temp_dir.name)
        self.num_classes = len(CATEGORIES2LABELS.keys())
        self.pub_model = get_instance_segmentation_model(self.num_classes)

        if os.path.exists(MODEL_PATH):
            self.checkpoint_path = MODEL_PATH
        else:
            raise Exception("Model weights not found.")

        assert os.path.exists(self.checkpoint_path)
        checkpoint = torch.load(self.checkpoint_path, map_location='cpu')
        self.pub_model.load_state_dict(checkpoint['model'])
        self.pub_model.eval()

    def run(self):
        """Run the API server"""
        uvicorn.run(self.app, host="0.0.0.0", port=8090)

    async def translate_pdf(self, language: str, input_pdf: UploadFile = File(...)) -> FileResponse:
        """API endpoint for translating PDF files.

        Parameters
        ----------
        input_pdf: UploadFile
            Input PDF file

        Returns
        -------
        FileResponse
            Translated PDF file
        """
        input_pdf_data = await input_pdf.read()
        self._translate_pdf(input_pdf_data, language, self.temp_dir_name)

        return FileResponse(
            self.temp_dir_name / "translated.pdf", media_type="application/pdf"
        )

    async def clear_temp_dir(self):
        """API endpoint for clearing the temporary directory."""
        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = Path(self.temp_dir.name)
        return {"message": "temp dir cleared"}
    
    def _repeated_substring(self, s: str):
        n = len(s)
        temp = s.replace("(", "")
        temp = temp.replace(")", "")
        for i in range(10, n // 2 + 1):
            pattern = temp[:i]
            matches = [match for match in re.finditer(pattern, temp)]
            if len(matches) >= 15:
                return True
        for i in range(n // 2 + 11, n):
            pattern = temp[n // 2 + 1:i]
            matches = [match for match in re.finditer(pattern, temp)]
            if len(matches) >= 15:
                return True
        return False

    def _translate_pdf(self, pdf_path_or_bytes: Union[Path, bytes], language: str, output_dir: Path) -> None:
        """Backend function for translating PDF files.

        Translation is performed in the following steps:
            1. Convert the PDF file to images
            2. Detect text blocks in the images
            3. For each text block, detect text and translate it
            4. Draw the translated text on the image
            5. Save the image as a PDF file
            6. Merge all PDF files into one PDF file

        At 3, this function does not translate the text after
        the references section. Instead, saves the image as it is.

        Parameters
        ----------
        pdf_path_or_bytes: Union[Path, bytes]
            Path to the input PDF file or bytes of the input PDF file
        output_dir: Path
            Path to the output directory
        """
        if isinstance(pdf_path_or_bytes, Path):
            pdf_images = convert_from_path(pdf_path_or_bytes, dpi=self.DPI)
        else:
            pdf_images = convert_from_bytes(pdf_path_or_bytes, dpi=self.DPI)
        print("Language:", language)
        pdf_files = []
        reached_references = False
        for i, image in tqdm(enumerate(pdf_images)):
            output_path = output_dir / f"{i:03}.pdf"
            if not reached_references:
                img, original_img, reached_references = self.__translate_one_page(
                    image=image,
                    language=language,
                    reached_references=reached_references,
                )
                fig, ax = plt.subplots(1, 2, figsize=(20, 14))
                ax[0].imshow(original_img)
                ax[1].imshow(img)
                ax[0].axis("off")
                ax[1].axis("off")
                plt.tight_layout()
                plt.savefig(output_path, format="pdf", dpi=self.DPI)
                plt.close(fig)
            else:
                (
                    image.convert("RGB")
                    .resize((int(1400 / image.size[1] * image.size[0]), 1400))
                    .save(output_path, format="pdf")
                )

            pdf_files.append(str(output_path))

        self.__merge_pdfs(pdf_files)

    def __load_models(self):
        """Backend function for loading models.

        Called in the constructor.
        Load the layout model, OCR model, translation model and font.
        """
        self.font_ja = ImageFont.truetype(
            "Source Han Serif CN Light.otf",
            size=self.FONT_SIZE_JAPANESE,
        )
        self.font_vi = ImageFont.truetype(
            "AlegreyaSans-Regular.otf",
            size=self.FONT_SIZE_VIETNAMESE,
        )

        # self.layout_model = PPStructure(table=False, ocr=False, lang="en")
        self.ocr_model = PaddleOCR(ocr=True, lang="en", ocr_version="PP-OCRv3")
        
        self.translate_model_ja = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-jap").to("cuda")
        self.translate_tokenizer_ja = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-jap")
        
        self.translate_model_vi = AutoModelForSeq2SeqLM.from_pretrained("VietAI/envit5-translation").to("cuda")
        self.translate_tokenizer_vi = AutoTokenizer.from_pretrained("VietAI/envit5-translation")
        
#         self.translate_model_vi = T5ForConditionalGeneration.from_pretrained("NlpHUST/t5-en-vi-small").to("cuda")
#         self.translate_tokenizer_vi = T5Tokenizer.from_pretrained("NlpHUST/t5-en-vi-small")

    def __translate_one_page(
        self,
        image: Image.Image,
        language: str,
        reached_references: bool,
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        """Translate one page of the PDF file.

        There are some heuristics to clean-up the results of translation:
            1. Remove newlines, tabs, brackets, slashes, and pipes
            2. Reject the result if there are few Japanese characters
            3. Skip the translation if the text block has only one line

        Parameters
        ----------
        image: Image.Image
            Image of the page
        reached_references: bool
            Whether the references section has been reached.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, bool]
            Translated image, original image,
            and whether the references section has been reached.
        """
        ori_img = np.array(image)
        temp = Image.fromarray(ori_img)
        image_path = "output_image.png"
        temp.save(image_path)
        original_img = copy.deepcopy(ori_img)
        img = cv2.imread(image_path)
        rat = 1000 / img.shape[0]
        # print("rat:", rat)
        img = cv2.resize(img, None, fx=rat, fy=rat)
        
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor()
        ])
        
        img = transform(img)
        with torch.no_grad():
            prediction = self.pub_model([img])
        
        img = torch.squeeze(img, 0).permute(1, 2, 0).mul(255).numpy().astype(np.uint8)
        overlay = img.copy()
        alpha = 0.5
        img = cv2.addWeighted(img, alpha, overlay, 1 - alpha, 0)

        for pred in prediction:
            for idx, _ in enumerate(pred['masks']):
                if pred['scores'][idx].item() < 0.7:
                    continue

                box = list(map(int, pred["boxes"][idx].tolist()))
                label = CATEGORIES2LABELS[pred["labels"][idx].item()]
                print("box: {}, label: {}".format(box, label))

                new_box_0 = int(box[0] / rat)
                new_box_1 = int(box[1] / rat)
                new_box_2 = int(box[2] / rat)
                new_box_3 = int(box[3] / rat)
                # thickness = -1
                if label == "text":
                    # print("label:", label)
                    temp_img = ori_img[new_box_1:new_box_3, new_box_0:new_box_2]

                    ocr_results = list(map(lambda x: x[0], self.ocr_model(temp_img)[1]))

                    if len(ocr_results) > 1:
                        text = " ".join(ocr_results)
                        text = re.sub(r"\n|\t|\[|\]|\/|\|", " ", text)
                        print("OCR results:", text)
                        translated_text = self.__translate(text, language)
                        translated_text = re.sub(r"\n|\t|\[|\]|\/|\|", " ", translated_text)

                        # if almost all characters in translated text are not japanese characters, skip
                        if language == "ja":
                            if len(
                                re.findall(
                                    r"[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF]",
                                    translated_text,
                                )
                            ) > 0.8 * len(translated_text):
                                print("skipped")
                                continue
                        
                        # if text is too short, skip
                        if len(translated_text) < 20:
                            print("skipped")
                            continue
                        
                        # for VietAI/envit5-translation
                        if language == "vi":
                            translated_text = translated_text.replace("vi: ", "")
                            translated_text = translated_text.replace("vi ", "")
                            translated_text = translated_text.strip()
                            
                        print("CHECK REPETITION:",  self._repeated_substring(translated_text))
                        if language == "ja":
                            if self._repeated_substring(translated_text):
                                print("REPEATED TEXT Detected!")
                                processed_text = fw_fill_ja(
                                    text,
                                    width=int(
                                        (new_box_2 - new_box_0) / (self.FONT_SIZE_JAPANESE / 2)
                                    )
                                    - 1,
                                )
                            else:
                                processed_text = fw_fill_ja(
                                    translated_text,
                                    width=int(
                                        (new_box_2 - new_box_0) / (self.FONT_SIZE_JAPANESE / 2)
                                    )
                                    - 1,
                                )
                        else:
                            if self._repeated_substring(translated_text):
                                print("REPEATED TEXT Detected!")
                                processed_text = fw_fill_vi(
                                    text,
                                    width=int(
                                        (new_box_2 - new_box_0) / (self.FONT_SIZE_VIETNAMESE / 2)
                                    )
                                    - 1,
                                )
                            else:
                                processed_text = fw_fill_vi(
                                    translated_text,
                                    width=int(
                                        (new_box_2 - new_box_0) / (self.FONT_SIZE_VIETNAMESE / 2)
                                    )
                                    - 1,
                                )

                        print("Processed_text:\n", processed_text)
                        new_block = Image.new(
                            "RGB",
                            (
                                new_box_2 - new_box_0,
                                new_box_3 - new_box_1,
                            ),
                            color=(255, 255, 255),
                        )
                        draw = ImageDraw.Draw(new_block)
                        if language == "ja":
                            draw.text(
                                (0, 0),
                                text=processed_text,
                                font=self.font_ja,
                                fill=(0, 0, 0),
                            )
                        else:
                            draw.text(
                                (0, 0),
                                text=processed_text,
                                font=self.font_vi,
                                fill=(0, 0, 0),
                            )
                        
                        new_block = np.array(new_block)
                        ori_img[
                            int(new_box_1) : int(new_box_3),
                            int(new_box_0) : int(new_box_2),
                        ] = new_block
                else:
                    try:
                        title = self.ocr_model(img)[1][0][0]
                    except IndexError:
                        continue
                    if title.lower() == "references" or title.lower() == "reference":
                        reached_references = True
            return ori_img, original_img, reached_references

    def __translate(self, text: str, language: str) -> str:
        """Translate text using the translation model.

        If the text is too long, it will be splited with
        the heuristic that each sentence should be within 448 characters.

        Parameters
        ----------
        text: str
            Text to be translated.

        Returns
        -------
        str
            Translated text.
        """
        texts = self.__split_text(text, 448)

        translated_texts = []
        for i, t in enumerate(texts):
            if language == "ja":
                inputs = self.translate_tokenizer_ja(t, return_tensors="pt").input_ids.to(
                    "cuda"
                )
                outputs = self.translate_model_ja.generate(inputs, max_length=512)
                res = self.translate_tokenizer_ja.decode(outputs[0], skip_special_tokens=True)
            else:
                inputs = self.translate_tokenizer_vi(t, return_tensors="pt").input_ids.to(
                    "cuda"
                )
                outputs = self.translate_model_vi.generate(inputs, max_length=512)
                res = self.translate_tokenizer_vi.decode(outputs[0], skip_special_tokens=True)
            
            # skip weird translations
            if language == "ja" and res.startswith("「この版"):
                continue

            translated_texts.append(res)
        print("Translation:\n", translated_texts)
        return " ".join(translated_texts)

    def __split_text(self, text: str, text_limit: int = 448) -> List[str]:
        """Split text into chunks of sentences within text_limit.

        Parameters
        ----------
        text: str
            Text to be split.
        text_limit: int
            Maximum length of each chunk. Defaults to 448.

        Returns
        -------
        List[str]
            List of text chunks,
            each of which is shorter than text_limit.
        """
        if len(text) < text_limit:
            return [text]

        sentences = text.rstrip().split(". ")
        sentences = [s + ". " for s in sentences[:-1]] + sentences[-1:]
        result = []
        current_text = ""
        for sentence in sentences:
            if len(current_text) + len(sentence) < text_limit:
                current_text += sentence
            else:
                if current_text:
                    result.append(current_text)
                while len(sentence) >= text_limit:
                    # better to look for a white space at least?
                    result.append(sentence[:text_limit - 1])
                    sentence = sentence[text_limit - 1:].lstrip()
                current_text = sentence
        if current_text:
            result.append(current_text)
        return result

    def __merge_pdfs(self, pdf_files: List[str]) -> None:
        """Merge translated PDF files into one file.

        Merged file will be stored in the temp directory
        as "translated.pdf".

        Parameters
        ----------
        pdf_files: List[str]
            List of paths to translated PDF files stored in
            the temp directory.
        """
        pdf_merger = PyPDF2.PdfMerger()

        for pdf_file in sorted(pdf_files):
            pdf_merger.append(pdf_file)
        pdf_merger.write(self.temp_dir_name / "translated.pdf")


if __name__ == "__main__":
    translate_api = TranslateApi()
    translate_api.run()
