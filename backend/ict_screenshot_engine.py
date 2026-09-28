from dataclasses import dataclass

# ==========================================================
# INPUT CANDLE
# ==========================================================

@dataclass
class Candle:
    x: int
    open: float
    high: float
    low: float
    close: float


# ==========================================================
# OUTPUT
# ==========================================================

@dataclass
class TradeSetup:
    signal: str

    confidence: int

    entry: float
    stop_loss: float
    take_profit: float

    grade: str

    bos: bool
    choch: bool
    liquidity: bool
    fvg: bool
    order_block: bool

    premium_discount: str

    status: str


# ==========================================================
# ICT ENGINE
# ==========================================================

class ICTScreenshotEngine:

    # ------------------------------------------------------
    # SWING HIGH
    # ------------------------------------------------------

    def swing_high(self, candles, lookback=6):

        highs = [
            c.high
            for c in candles[-lookback:]
        ]

        return max(highs)

    # ------------------------------------------------------
    # SWING LOW
    # ------------------------------------------------------

    def swing_low(self, candles, lookback=6):

        lows = [
            c.low
            for c in candles[-lookback:]
        ]

        return min(lows)

    # ------------------------------------------------------
    # BOS
    # ------------------------------------------------------

    def detect_bos(self, candles):

        if len(candles) < 8:
            return False

        previous = self.swing_high(
            candles[:-1]
        )

        return candles[-1].high > previous

    # ------------------------------------------------------
    # CHOCH
    # ------------------------------------------------------

    def detect_choch(self, candles):

        if len(candles) < 8:
            return False

        previous = self.swing_low(
            candles[:-1]
        )

        return candles[-1].low < previous

    # ------------------------------------------------------
    # LIQUIDITY SWEEP
    # ------------------------------------------------------

    def detect_liquidity(self, candles):

        if len(candles) < 5:
            return False

        highs = [
            c.high
            for c in candles[-4:]
        ]

        top = max(highs)

        return abs(
            candles[-1].high - top
        ) < 1.5

    # ------------------------------------------------------
    # FAIR VALUE GAP
    # ------------------------------------------------------

    def detect_fvg(self, candles):

        if len(candles) < 3:
            return None

        a = candles[-3]
        c = candles[-1]

        if c.low > a.high:

            return (
                "BUY",
                round(
                    (a.high + c.low) / 2,
                    2
                )
            )

        if c.high < a.low:

            return (
                "SELL",
                round(
                    (a.low + c.high) / 2,
                    2
                )
            )

        return None

    # ------------------------------------------------------
    # ORDER BLOCK
    # ------------------------------------------------------

    def detect_ob(self, candles):

        if len(candles) < 4:
            return None

        last = candles[-2]

        if last.close < last.open:

            return (
                "BUY",
                last.low,
                last.high
            )

        return (
            "SELL",
            last.low,
            last.high
        )

    # ------------------------------------------------------
    # PREMIUM / DISCOUNT
    # ------------------------------------------------------

    def premium_discount(self, candles):

        hi = max(
            c.high
            for c in candles[-20:]
        )

        lo = min(
            c.low
            for c in candles[-20:]
        )

        equilibrium = (hi + lo) / 2

        if candles[-1].close < equilibrium:
            return "DISCOUNT"

        return "PREMIUM"

    # ------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------

    def confidence(
        self,
        bos,
        choch,
        liq,
        fvg,
        ob
    ):

        score = 50

        if bos:
            score += 15

        if choch:
            score += 15

        if liq:
            score += 10

        if fvg:
            score += 5

        if ob:
            score += 5

        return min(score, 100)

    # ------------------------------------------------------
    # GRADE
    # ------------------------------------------------------

    def grade(self, score):

        if score >= 90:
            return "A+"

        if score >= 80:
            return "A"

        if score >= 65:
            return "B"

        return "C"

    # ======================================================
    # MAIN ANALYSIS
    # ======================================================

    def analyze(self, candles):

        if len(candles) < 20:

            return TradeSetup(

                signal="WAIT",

                confidence=0,

                entry=0,
                stop_loss=0,
                take_profit=0,

                grade="-",

                bos=False,
                choch=False,
                liquidity=False,
                fvg=False,
                order_block=False,

                premium_discount="-",

                status="Not enough candles"

            )

        bos = self.detect_bos(candles)

        choch = self.detect_choch(candles)

        liq = self.detect_liquidity(candles)

        fvg = self.detect_fvg(candles)

        ob = self.detect_ob(candles)

        zone = self.premium_discount(candles)

        score = self.confidence(
            bos,
            choch,
            liq,
            fvg is not None,
            ob is not None
        )

        grade = self.grade(score)

        # ================================
        # BUY
        # ================================

        if (
            fvg
            and
            fvg[0] == "BUY"
            and
            zone == "DISCOUNT"
        ):

            entry = fvg[1]

            sl = min(
                c.low
                for c in candles[-5:]
            )

            risk = entry - sl

            tp = round(
                entry + (risk * 2),
                2
            )

            return TradeSetup(

                signal="BUY",

                confidence=score,

                entry=entry,
                stop_loss=sl,
                take_profit=tp,

                grade=grade,

                bos=bos,
                choch=choch,
                liquidity=liq,
                fvg=True,
                order_block=True,

                premium_discount=zone,

                status="Bullish ICT setup"

            )

        # ================================
        # SELL
        # ================================

        if (
            fvg
            and
            fvg[0] == "SELL"
            and
            zone == "PREMIUM"
        ):

            entry = fvg[1]

            sl = max(
                c.high
                for c in candles[-5:]
            )

            risk = sl - entry

            tp = round(
                entry - (risk * 2),
                2
            )

            return TradeSetup(

                signal="SELL",

                confidence=score,

                entry=entry,
                stop_loss=sl,
                take_profit=tp,

                grade=grade,

                bos=bos,
                choch=choch,
                liquidity=liq,
                fvg=True,
                order_block=True,

                premium_discount=zone,

                status="Bearish ICT setup"

            )

        return TradeSetup(

            signal="WAIT",

            confidence=score,

            entry=0,
            stop_loss=0,
            take_profit=0,

            grade=grade,

            bos=bos,
            choch=choch,
            liquidity=liq,
            fvg=False,
            order_block=ob is not None,

            premium_discount=zone,

            status="No A+ setup"

        )


engine = ICTScreenshotEngine()