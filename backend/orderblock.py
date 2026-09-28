from dataclasses import dataclass


@dataclass
class OrderBlock:
    direction: str
    open: float
    high: float
    low: float
    close: float
    candle: int
    strength: int


class OrderBlockEngine:

    def __init__(self):
        self.displacement = 1.5

    # =====================================
    # Candle Type
    # =====================================

    def bullish(self, candle):
        return float(candle["close"]) > float(candle["open"])

    def bearish(self, candle):
        return float(candle["close"]) < float(candle["open"])

    # =====================================
    # Bullish Order Block
    # Last bearish candle before impulse
    # =====================================

    def bullish_ob(self, df):

        blocks = []

        for i in range(1, len(df)-1):

            current = df.iloc[i]
            next_candle = df.iloc[i+1]

            if not self.bearish(current):
                continue

            body = abs(
                float(next_candle["close"]) -
                float(next_candle["open"])
            )

            range_size = (
                float(next_candle["high"]) -
                float(next_candle["low"])
            )

            if body < (range_size / self.displacement):
                continue

            if float(next_candle["close"]) <= float(current["high"]):
                continue

            strength = min(
                100,
                int((body / range_size) * 100)
            )

            blocks.append(
                OrderBlock(
                    direction="BUY",
                    open=float(current["open"]),
                    high=float(current["high"]),
                    low=float(current["low"]),
                    close=float(current["close"]),
                    candle=i,
                    strength=max(strength, 70)
                )
            )

        return blocks

    # =====================================
    # Bearish Order Block
    # Last bullish candle before drop
    # =====================================

    def bearish_ob(self, df):

        blocks = []

        for i in range(1, len(df)-1):

            current = df.iloc[i]
            next_candle = df.iloc[i+1]

            if not self.bullish(current):
                continue

            body = abs(
                float(next_candle["close"]) -
                float(next_candle["open"])
            )

            range_size = (
                float(next_candle["high"]) -
                float(next_candle["low"])
            )

            if body < (range_size / self.displacement):
                continue

            if float(next_candle["close"]) >= float(current["low"]):
                continue

            strength = min(
                100,
                int((body / range_size) * 100)
            )

            blocks.append(
                OrderBlock(
                    direction="SELL",
                    open=float(current["open"]),
                    high=float(current["high"]),
                    low=float(current["low"]),
                    close=float(current["close"]),
                    candle=i,
                    strength=max(strength, 70)
                )
            )

        return blocks

    # =====================================
    # Latest Institutional OB
    # =====================================

    def analyze(self, df):

        buys = self.bullish_ob(df)
        sells = self.bearish_ob(df)

        return {
            "buy": buys[-1] if buys else None,
            "sell": sells[-1] if sells else None
        }


engine = OrderBlockEngine()