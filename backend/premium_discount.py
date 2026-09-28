from dataclasses import dataclass


@dataclass
class DealingRange:
    high: float
    low: float
    equilibrium: float
    current_price: float
    zone: str


class PremiumDiscountEngine:

    def __init__(self):
        self.minimum_candles = 20

    # =====================================
    # FIND DEALING RANGE
    # =====================================

    def find_range(self, df):

        if df is None:
            return None

        if len(df) < self.minimum_candles:
            return None

        # Use recent market structure rather than
        # the entire historical dataset.
        recent = df.tail(100)

        high = float(recent["high"].max())
        low = float(recent["low"].min())

        if high <= low:
            return None

        return high, low

    # =====================================
    # CALCULATE EQUILIBRIUM
    # =====================================

    def calculate(self, df):

        dealing_range = self.find_range(df)

        if dealing_range is None:
            return None

        high, low = dealing_range

        equilibrium = (high + low) / 2

        current_price = float(
            df.iloc[-1]["close"]
        )

        # =================================
        # PREMIUM
        # =================================

        if current_price > equilibrium:

            zone = "PREMIUM"

        # =================================
        # DISCOUNT
        # =================================

        elif current_price < equilibrium:

            zone = "DISCOUNT"

        # =================================
        # EQUILIBRIUM
        # =================================

        else:

            zone = "EQUILIBRIUM"

        return DealingRange(

            high=round(high, 2),

            low=round(low, 2),

            equilibrium=round(
                equilibrium,
                2
            ),

            current_price=round(
                current_price,
                2
            ),

            zone=zone
        )

    # =====================================
    # BUY FILTER
    # =====================================

    def buy_allowed(self, zone):

        if zone is None:
            return False

        return zone.zone == "DISCOUNT"

    # =====================================
    # SELL FILTER
    # =====================================

    def sell_allowed(self, zone):

        if zone is None:
            return False

        return zone.zone == "PREMIUM"

    # =====================================
    # DISTANCE FROM EQUILIBRIUM
    # =====================================

    def distance_from_equilibrium(self, zone):

        if zone is None:
            return 0

        distance = abs(
            zone.current_price
            - zone.equilibrium
        )

        return round(distance, 2)

    # =====================================
    # COMPLETE ANALYSIS
    # =====================================

    def analyze(self, df):

        zone = self.calculate(df)

        if zone is None:

            return {
                "available": False,
                "zone": "UNKNOWN",
                "high": 0,
                "low": 0,
                "equilibrium": 0,
                "current_price": 0,
                "buy_allowed": False,
                "sell_allowed": False
            }

        return {

            "available": True,

            "zone": zone.zone,

            "high": zone.high,

            "low": zone.low,

            "equilibrium": zone.equilibrium,

            "current_price": zone.current_price,

            "buy_allowed": self.buy_allowed(
                zone
            ),

            "sell_allowed": self.sell_allowed(
                zone
            ),

            "distance_from_equilibrium":
                self.distance_from_equilibrium(
                    zone
                )
        }


engine = PremiumDiscountEngine()