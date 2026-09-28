from dataclasses import dataclass


@dataclass
class Trend:
    trend: str
    last_high: float
    last_low: float
    ema50: float
    ema200: float
    strength: int


class HTFEngine:

    def __init__(self):
        self.swing = 2

    # =====================================
    # EMA
    # =====================================

    def ema(self, series, period):

        return series.ewm(
            span=period,
            adjust=False
        ).mean()

    # =====================================
    # SWING HIGHS
    # =====================================

    def highs(self, df):

        values = []

        for i in range(
            self.swing,
            len(df)-self.swing
        ):

            current = df.iloc[i]["high"]

            left = df.iloc[
                i-self.swing:i
            ]["high"]

            right = df.iloc[
                i+1:i+1+self.swing
            ]["high"]

            if (
                current > left.max()
                and
                current > right.max()
            ):

                values.append(float(current))

        return values

    # =====================================
    # SWING LOWS
    # =====================================

    def lows(self, df):

        values = []

        for i in range(
            self.swing,
            len(df)-self.swing
        ):

            current = df.iloc[i]["low"]

            left = df.iloc[
                i-self.swing:i
            ]["low"]

            right = df.iloc[
                i+1:i+1+self.swing
            ]["low"]

            if (
                current < left.min()
                and
                current < right.min()
            ):

                values.append(float(current))

        return values

    # =====================================
    # TREND
    # =====================================

    def trend(self, df):

        data = df.copy()

        data["ema50"] = self.ema(
            data["close"],
            50
        )

        data["ema200"] = self.ema(
            data["close"],
            200
        )

        ema50 = float(
            data.iloc[-1]["ema50"]
        )

        ema200 = float(
            data.iloc[-1]["ema200"]
        )

        highs = self.highs(data)
        lows = self.lows(data)

        last_high = highs[-1] if highs else 0
        last_low = lows[-1] if lows else 0

        current = float(
            data.iloc[-1]["close"]
        )

        # =================================
        # BULLISH
        # =================================

        if (
            ema50 > ema200
            and
            current > ema50
        ):

            strength = min(
                100,
                int(abs(ema50-ema200)*100)
            )

            return Trend(
                trend="BULLISH",
                last_high=round(last_high,2),
                last_low=round(last_low,2),
                ema50=round(ema50,2),
                ema200=round(ema200,2),
                strength=max(strength,70)
            )

        # =================================
        # BEARISH
        # =================================

        if (
            ema50 < ema200
            and
            current < ema50
        ):

            strength = min(
                100,
                int(abs(ema50-ema200)*100)
            )

            return Trend(
                trend="BEARISH",
                last_high=round(last_high,2),
                last_low=round(last_low,2),
                ema50=round(ema50,2),
                ema200=round(ema200,2),
                strength=max(strength,70)
            )

        # =================================
        # RANGE
        # =================================

        return Trend(
            trend="RANGE",
            last_high=round(last_high,2),
            last_low=round(last_low,2),
            ema50=round(ema50,2),
            ema200=round(ema200,2),
            strength=40
        )


engine = HTFEngine()