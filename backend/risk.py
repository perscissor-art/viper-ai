from dataclasses import dataclass

@dataclass
class RiskResult:
    lot: float
    risk_amount: float
    stop_pips: float


class RiskEngine:

    def __init__(self):
        pass

    # -----------------------------------
    # Calculate lot size
    # -----------------------------------
    def calculate(
        self,
        balance,
        risk_percent,
        entry,
        stop
    ):

        risk_amount = (
            balance * risk_percent
        ) / 100

        distance = abs(entry - stop)

        if distance <= 0:

            return RiskResult(
                lot=0.01,
                risk_amount=round(risk_amount,2),
                stop_pips=0
            )

        # XM GOLD approximation:
        # 1 lot ≈ $100 per $1 move
        value_per_lot = 100

        lot = risk_amount / (
            distance * value_per_lot
        )

        lot = max(0.01, round(lot,2))

        return RiskResult(
            lot=lot,
            risk_amount=round(risk_amount,2),
            stop_pips=round(distance,2)
        )


engine = RiskEngine()