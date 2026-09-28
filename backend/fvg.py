from dataclasses import dataclass


@dataclass
class FVG:
    direction: str
    top: float
    bottom: float
    midpoint: float
    size: float
    score: str
    candle: int


class FVGEngine:

    def __init__(self):
        pass

    # =====================================
    # GRADE GAP QUALITY
    # =====================================

    def grade(self, size):

        if size >= 8:
            return "A+"

        if size >= 5:
            return "A"

        if size >= 3:
            return "B"

        return "C"

    # =====================================
    # BULLISH FVG
    # Candle 1 High < Candle 3 Low
    # =====================================

    def bullish(self, df):

        gaps = []

        for i in range(2, len(df)):

            first_high = float(df.iloc[i-2]["high"])
            third_low = float(df.iloc[i]["low"])

            if third_low > first_high:

                top = third_low
                bottom = first_high

                midpoint = round(
                    (top + bottom) / 2,
                    2
                )

                size = round(top - bottom, 2)

                gaps.append(
                    FVG(
                        direction="BUY",
                        top=top,
                        bottom=bottom,
                        midpoint=midpoint,
                        size=size,
                        score=self.grade(size),
                        candle=i
                    )
                )

        return gaps

    # =====================================
    # BEARISH FVG
    # Candle 1 Low > Candle 3 High
    # =====================================

    def bearish(self, df):

        gaps = []

        for i in range(2, len(df)):

            first_low = float(df.iloc[i-2]["low"])
            third_high = float(df.iloc[i]["high"])

            if third_high < first_low:

                top = first_low
                bottom = third_high

                midpoint = round(
                    (top + bottom) / 2,
                    2
                )

                size = round(top - bottom, 2)

                gaps.append(
                    FVG(
                        direction="SELL",
                        top=top,
                        bottom=bottom,
                        midpoint=midpoint,
                        size=size,
                        score=self.grade(size),
                        candle=i
                    )
                )

        return gaps

    # =====================================
    # RETURN LATEST GAP
    # =====================================

    def analyze(self, df):

        bull = self.bullish(df)
        bear = self.bearish(df)

        latest = None

        if bull:
            latest = bull[-1]

        if bear:

            if latest is None:
                latest = bear[-1]

            elif bear[-1].candle > latest.candle:
                latest = bear[-1]

        return latest


engine = FVGEngine()