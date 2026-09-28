from dataclasses import dataclass


@dataclass
class Sweep:
    direction: str
    price: float
    candle: int
    strength: int


class LiquidityEngine:

    def __init__(self):
        pass

    # =====================================
    # BUY-SIDE LIQUIDITY SWEEP
    # =====================================

    def buy_sweep(self, df, highs):

        if len(highs) == 0:
            return None

        last = highs[-1]

        for i in range(last.index + 1, len(df)):

            high = float(df.iloc[i]["high"])
            close = float(df.iloc[i]["close"])

            if high > last.price and close < last.price:

                wick = round(high - last.price, 2)

                strength = min(
                    100,
                    int(wick * 120)
                )

                return Sweep(
                    direction="SELL",
                    price=last.price,
                    candle=i,
                    strength=max(strength, 60)
                )

        return None

    # =====================================
    # SELL-SIDE LIQUIDITY SWEEP
    # =====================================

    def sell_sweep(self, df, lows):

        if len(lows) == 0:
            return None

        last = lows[-1]

        for i in range(last.index + 1, len(df)):

            low = float(df.iloc[i]["low"])
            close = float(df.iloc[i]["close"])

            if low < last.price and close > last.price:

                wick = round(last.price - low, 2)

                strength = min(
                    100,
                    int(wick * 120)
                )

                return Sweep(
                    direction="BUY",
                    price=last.price,
                    candle=i,
                    strength=max(strength, 60)
                )

        return None

    # =====================================
    # RETURN LATEST VALID SWEEP
    # =====================================

    def analyze(self, df, highs, lows):

        buy = self.buy_sweep(df, highs)

        sell = self.sell_sweep(df, lows)

        if buy and sell:

            if buy.candle > sell.candle:
                return buy

            return sell

        if buy:
            return buy

        if sell:
            return sell

        return None


engine = LiquidityEngine()