from dataclasses import dataclass
import cv2
import numpy as np
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

@dataclass
class Calibration:
    chart_left: int
    chart_right: int
    chart_top: int
    chart_bottom: int
    price_top: float
    price_bottom: float
    confidence: int

class VisionCalibrator:

    def find_price_labels(self, rgb):
        data = pytesseract.image_to_data(
            rgb,
            config="--psm 6",
            output_type=pytesseract.Output.DICT
        )

        labels = []

        for i in range(len(data["text"])):

            txt = data["text"][i].strip()

            if not txt:
                continue

            match = re.search(r"\d+\.\d+", txt)

            if not match:
                continue

            price = float(match.group())

            labels.append({
                "price": price,
                "x": data["left"][i],
                "y": data["top"][i]
            })

        return labels

    def calibrate(self, image):

        rgb = np.array(image)

        h, w, _ = rgb.shape

        labels = self.find_price_labels(rgb)

        if len(labels) < 2:

            return Calibration(
                0,0,0,0,
                0,0,
                0
            )

        labels = sorted(labels, key=lambda x: x["y"])

        top = labels[0]
        bottom = labels[-1]

        return Calibration(
            chart_left=int(w*0.05),
            chart_right=int(w*0.82),
            chart_top=int(h*0.08),
            chart_bottom=int(h*0.90),
            price_top=top["price"],
            price_bottom=bottom["price"],
            confidence=90
        )

engine = VisionCalibrator()