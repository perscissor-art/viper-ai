from dataclasses import dataclass

@dataclass
class Swing:
    index: int
    price: float
    kind: str


class ICTEngine:

    def __init__(self):
        self.lookback = 2

    # =====================================
    # SWING HIGHS
    # =====================================

    def swing_highs(self, df):

        swings = []

        for i in range(self.lookback, len(df)-self.lookback):

            current = df.iloc[i]["high"]

            left = df.iloc[i-self.lookback:i]["high"]
            right = df.iloc[i+1:i+1+self.lookback]["high"]

            if current > left.max() and current > right.max():

                swings.append(
                    Swing(
                        index=i,
                        price=float(current),
                        kind="HIGH"
                    )
                )

        return swings

    # =====================================
    # SWING LOWS
    # =====================================

    def swing_lows(self, df):

        swings = []

        for i in range(self.lookback, len(df)-self.lookback):

            current = df.iloc[i]["low"]

            left = df.iloc[i-self.lookback:i]["low"]
            right = df.iloc[i+1:i+1+self.lookback]["low"]

            if current < left.min() and current < right.min():

                swings.append(
                    Swing(
                        index=i,
                        price=float(current),
                        kind="LOW"
                    )
                )

        return swings

    # =====================================
    # HH / LH
    # =====================================

    def classify_highs(self, highs):

        labels = []

        if len(highs) < 2:
            return labels

        previous = highs[0]

        for current in highs[1:]:

            if current.price > previous.price:
                label = "HH"
            else:
                label = "LH"

            labels.append({
                "index": current.index,
                "price": current.price,
                "label": label
            })

            previous = current

        return labels

    # =====================================
    # HL / LL
    # =====================================

    def classify_lows(self, lows):

        labels = []

        if len(lows) < 2:
            return labels

        previous = lows[0]

        for current in lows[1:]:

            if current.price > previous.price:
                label = "HL"
            else:
                label = "LL"

            labels.append({
                "index": current.index,
                "price": current.price,
                "label": label
            })

            previous = current

        return labels

    # =====================================
    # BOS BUY
    # =====================================

    def bos_buy(self, df, highs):

        if len(highs) == 0:
            return False

        last_high = highs[-1].price

        return float(df.iloc[-1]["close"]) > last_high

    # =====================================
    # BOS SELL
    # =====================================

    def bos_sell(self, df, lows):

        if len(lows) == 0:
            return False

        last_low = lows[-1].price

        return float(df.iloc[-1]["close"]) < last_low

    # =====================================
    # CHOCH BUY
    # =====================================

    def choch_buy(self, highs, lows):

        if len(highs) == 0 or len(lows) == 0:
            return False

        return (
            highs[-1]["label"] == "HH"
            and
            lows[-1]["label"] == "HL"
        )

    # =====================================
    # CHOCH SELL
    # =====================================

    def choch_sell(self, highs, lows):

        if len(highs) == 0 or len(lows) == 0:
            return False

        return (
            highs[-1]["label"] == "LH"
            and
            lows[-1]["label"] == "LL"
        )

    # =====================================
    # COMPLETE ANALYSIS
    # =====================================

    def analyze(self, df):

        highs = self.swing_highs(df)

        lows = self.swing_lows(df)

        high_labels = self.classify_highs(highs)

        low_labels = self.classify_lows(lows)

        return {

            "highs": highs,

            "lows": lows,

            "high_labels": high_labels,

            "low_labels": low_labels,

            "bos_buy": self.bos_buy(df, highs),

            "bos_sell": self.bos_sell(df, lows),

            "choch_buy": self.choch_buy(
                high_labels,
                low_labels
            ),

            "choch_sell": self.choch_sell(
                high_labels,
                low_labels
            )

        }


engine = ICTEngine()