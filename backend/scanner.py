from datetime import datetime

from mt5_bridge import bridge
from ict_engine import engine as ict
from liquidity import engine as liquidity
from fvg import engine as fvg
from orderblock import engine as orderblock
from premium_discount import engine as premium_discount
from htf_engine import engine as htf
from risk import engine as risk_engine


class ViperScanner:

    # =====================================
    # NEW YORK RANGE (13:00–14:00)
    # =====================================

    def ny_range(self, df):

        session = df[
            (df["time"].dt.hour >= 13) &
            (df["time"].dt.hour < 14)
        ]

        if len(session) == 0:
            return None

        return {
            "high": float(session["high"].max()),
            "low": float(session["low"].min()),
            "open": float(session.iloc[0]["open"])
        }

    # =====================================
    # TRADE ONLY AFTER 15:15
    # =====================================

    def session_ready(self):

        now = datetime.now()

        minutes = now.hour * 60 + now.minute

        return minutes >= (15 * 60 + 15)

    # =====================================
    # CONFIDENCE SCORE
    # =====================================

    def confidence(self, bos, choch, sweep, gap, ob):

        score = 50

        if bos:
            score += 10

        if choch:
            score += 10

        if sweep:
            score += 10

        if gap:
            score += 10

        if ob:
            score += 10

        return min(score, 100)

    # =====================================
    # WAIT RESPONSE
    # =====================================

    def wait(
        self,
        symbol,
        current,
        trend,
        zone,
        status
    ):

        return {

            "symbol": symbol,

            "signal": "WAIT",

            "confidence": 0,

            "entry": 0,

            "stop_loss": 0,

            "take_profit": 0,

            "lot_size": 0.01,

            "risk_amount": 0,

            "rr": "0",

            "bos": False,

            "choch": False,

            "sweep": False,

            "fvg": False,

            "order_block": False,

            "grade": "-",

            "premium_discount": zone,

            "h4_trend": trend,

            "current_price": current,

            "status": status

        }

    # =====================================
    # MAIN SCANNER
    # =====================================

    def scan(
        self,
        symbol,
        balance=1000,
        risk=1
    ):

        bridge.connect()

        try:

            h1 = bridge.get_h1(symbol, 300)

            h4 = bridge.get_h4(symbol, 200)

            current = bridge.current_price(symbol)

            trend = htf.trend(h4)

            zone = premium_discount.analyze(h1)

            if not self.session_ready():

                return self.wait(
                    symbol,
                    current,
                    trend.trend,
                    zone["zone"],
                    "Waiting for New York session"
                )

            opening = self.ny_range(h1)

            if opening is None:

                return self.wait(
                    symbol,
                    current,
                    trend.trend,
                    zone["zone"],
                    "Opening range unavailable"
                )

            structure = ict.analyze(h1)

            sweep = liquidity.analyze(
                h1,
                structure["highs"],
                structure["lows"]
            )

            gap = fvg.analyze(h1)

            blocks = orderblock.analyze(h1)

            # =====================================
            # BUY MODEL
            # =====================================

            if (

                trend.trend == "BULLISH"

                and

                zone["buy_allowed"]

                and

                current > opening["high"]

                and

                structure["bos_buy"]

                and

                gap is not None

                and

                gap.direction == "BUY"

                and

                sweep is not None

                and

                sweep.direction == "BUY"

                and

                blocks["buy"] is not None

            ):

                entry = gap.midpoint

                stop = round(
                    min(
                        sweep.price,
                        blocks["buy"].low
                    ) - 0.30,
                    2
                )

                tp = round(
                    entry + (
                        abs(entry-stop) * 2
                    ),
                    2
                )

                risk_data = risk_engine.calculate(
                    balance,
                    risk,
                    entry,
                    stop
                )

                return {

                    "symbol": symbol,

                    "signal": "BUY",

                    "confidence": self.confidence(
                        True,
                        structure["choch_buy"],
                        True,
                        True,
                        True
                    ),

                    "entry": entry,

                    "stop_loss": stop,

                    "take_profit": tp,

                    "lot_size": risk_data.lot,

                    "risk_amount": risk_data.risk_amount,

                    "rr": "1:2",

                    "bos": True,

                    "choch": structure["choch_buy"],

                    "sweep": True,

                    "fvg": True,

                    "order_block": True,

                    "grade": gap.score,

                    "premium_discount": zone["zone"],

                    "h4_trend": trend.trend,

                    "current_price": current,

                    "status": "A+ New York BUY"

                }

            # =====================================
            # SELL MODEL
            # =====================================

            if (

                trend.trend == "BEARISH"

                and

                zone["sell_allowed"]

                and

                current < opening["low"]

                and

                structure["bos_sell"]

                and

                gap is not None

                and

                gap.direction == "SELL"

                and

                sweep is not None

                and

                sweep.direction == "SELL"

                and

                blocks["sell"] is not None

            ):

                entry = gap.midpoint

                stop = round(
                    max(
                        sweep.price,
                        blocks["sell"].high
                    ) + 0.30,
                    2
                )

                tp = round(
                    entry - (
                        abs(stop-entry) * 2
                    ),
                    2
                )

                risk_data = risk_engine.calculate(
                    balance,
                    risk,
                    stop,
                    entry
                )

                return {

                    "symbol": symbol,

                    "signal": "SELL",

                    "confidence": self.confidence(
                        True,
                        structure["choch_sell"],
                        True,
                        True,
                        True
                    ),

                    "entry": entry,

                    "stop_loss": stop,

                    "take_profit": tp,

                    "lot_size": risk_data.lot,

                    "risk_amount": risk_data.risk_amount,

                    "rr": "1:2",

                    "bos": True,

                    "choch": structure["choch_sell"],

                    "sweep": True,

                    "fvg": True,

                    "order_block": True,

                    "grade": gap.score,

                    "premium_discount": zone["zone"],

                    "h4_trend": trend.trend,

                    "current_price": current,

                    "status": "A+ New York SELL"

                }

            # =====================================
            # WAIT
            # =====================================

            return self.wait(
                symbol,
                current,
                trend.trend,
                zone["zone"],
                "No valid institutional setup"
            )

        finally:

            bridge.disconnect()


scanner = ViperScanner()