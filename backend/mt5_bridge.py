import MetaTrader5 as mt5
import pandas as pd


class MT5Bridge:

    def __init__(self):
        self.connected = False

    # ===========================
    # CONNECT
    # ===========================

    def connect(self):

        if self.connected:
            return True

        if not mt5.initialize():
            raise Exception("Could not connect to MetaTrader 5")

        self.connected = True
        return True

    # ===========================
    # DISCONNECT
    # ===========================

    def disconnect(self):

        if self.connected:
            mt5.shutdown()

        self.connected = False

    # ===========================
    # FIND XM SYMBOL
    # ===========================

    def resolve_symbol(self, symbol):

        # Exact match first
        info = mt5.symbol_info(symbol)

        if info is not None:
            if not info.visible:
                mt5.symbol_select(symbol, True)
            return symbol

        # Search every MT5 symbol
        symbols = mt5.symbols_get()

        if symbols is None:
            raise Exception("Could not read MT5 symbols")

        target = symbol.upper()

        for s in symbols:

            name = s.name.upper()

            if target in name:

                mt5.symbol_select(s.name, True)

                return s.name

        raise Exception(f"{symbol} does not exist on this MT5 account")

    # ===========================
    # GET RATES
    # ===========================

    def get_rates(self, symbol, timeframe, candles):

        real_symbol = self.resolve_symbol(symbol)

        rates = mt5.copy_rates_from_pos(
            real_symbol,
            timeframe,
            0,
            candles
        )

        if rates is None or len(rates) == 0:
            raise Exception(f"No data received from {real_symbol}")

        df = pd.DataFrame(rates)

        df["time"] = pd.to_datetime(df["time"], unit="s")

        return df[
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "tick_volume",
            ]
        ]

    # ===========================
    # H1
    # ===========================

    def get_h1(self, symbol="GOLD", candles=300):

        return self.get_rates(
            symbol,
            mt5.TIMEFRAME_H1,
            candles
        )

    # ===========================
    # H4
    # ===========================

    def get_h4(self, symbol="GOLD", candles=200):

        return self.get_rates(
            symbol,
            mt5.TIMEFRAME_H4,
            candles
        )

    # ===========================
    # LIVE PRICE
    # ===========================

    def current_price(self, symbol="GOLD"):

        real_symbol = self.resolve_symbol(symbol)

        tick = mt5.symbol_info_tick(real_symbol)

        if tick is None:
            raise Exception(f"No live price for {real_symbol}")

        return round(float(tick.bid), 2)


bridge = MT5Bridge()