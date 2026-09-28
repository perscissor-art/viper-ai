import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class Candle:
    x: int
    open: float
    high: float
    low: float
    close: float

class CandleReconstructor:

    def detect(self, image, calibration):

        rgb = np.array(image)

        gray = cv2.cvtColor(
            rgb,
            cv2.COLOR_RGB2GRAY
        )

        chart = gray[
            calibration.chart_top:calibration.chart_bottom,
            calibration.chart_left:calibration.chart_right
        ]

        blur = cv2.GaussianBlur(
            chart,
            (3,3),
            0
        )

        edges = cv2.Canny(
            blur,
            40,
            120
        )

        contours,_ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        candles=[]

        chart_height = (
            calibration.chart_bottom -
            calibration.chart_top
        )

        price_range = (
            calibration.price_top -
            calibration.price_bottom
        )

        def pixel_to_price(y):

            ratio = y / chart_height

            return round(
                calibration.price_top -
                (ratio * price_range),
                2
            )

        for c in contours:

            x,y,w,h = cv2.boundingRect(c)

            if h < 10:
                continue

            if w < 2:
                continue

            if h / max(w,1) < 2:
                continue

            high = pixel_to_price(y)

            low = pixel_to_price(y+h)

            body_top = y + h*0.35
            body_bottom = y + h*0.65

            open_price = pixel_to_price(body_top)
            close_price = pixel_to_price(body_bottom)

            candles.append(

                Candle(

                    x=x,

                    open=open_price,

                    high=high,

                    low=low,

                    close=close_price

                )

            )

        candles.sort(
            key=lambda c:c.x
        )

        return candles

engine = CandleReconstructor()