from dataclasses import dataclass

from vision_calibrator import engine as calibrator
from candle_reconstructor import engine as reconstructor
from ict_screenshot_engine import engine as ict


@dataclass
class VisionResult:
    signal: str
    confidence: int

    entry: float
    stop_loss: float
    take_profit: float

    grade: str
    status: str

    candles_detected: int
    calibration_confidence: int

    bos: bool
    choch: bool
    liquidity: bool
    fvg: bool
    order_block: bool

    premium_discount: str


class VisionEngine:

    def analyze(self, image):

        # ---------------------------------
        # STEP 1 : CALIBRATION
        # ---------------------------------

        calibration = calibrator.calibrate(image)

        if calibration.confidence < 60:

            return VisionResult(
                signal="WAIT",
                confidence=0,

                entry=0,
                stop_loss=0,
                take_profit=0,

                grade="-",
                status="Calibration failed",

                candles_detected=0,
                calibration_confidence=calibration.confidence,

                bos=False,
                choch=False,
                liquidity=False,
                fvg=False,
                order_block=False,

                premium_discount="-"
            )

        # ---------------------------------
        # STEP 2 : RECONSTRUCT CANDLES
        # ---------------------------------

        candles = reconstructor.detect(
            image,
            calibration
        )

        if len(candles) < 20:

            return VisionResult(
                signal="WAIT",
                confidence=0,

                entry=0,
                stop_loss=0,
                take_profit=0,

                grade="-",
                status="Not enough candles detected",

                candles_detected=len(candles),
                calibration_confidence=calibration.confidence,

                bos=False,
                choch=False,
                liquidity=False,
                fvg=False,
                order_block=False,

                premium_discount="-"
            )

        # ---------------------------------
        # STEP 3 : ICT ANALYSIS
        # ---------------------------------

        trade = ict.analyze(candles)

        return VisionResult(

            signal=trade.signal,

            confidence=trade.confidence,

            entry=trade.entry,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,

            grade=trade.grade,
            status=trade.status,

            candles_detected=len(candles),

            calibration_confidence=calibration.confidence,

            bos=trade.bos,
            choch=trade.choch,
            liquidity=trade.liquidity,
            fvg=trade.fvg,
            order_block=trade.order_block,

            premium_discount=trade.premium_discount

        )


engine = VisionEngine()