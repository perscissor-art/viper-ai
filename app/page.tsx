"use client";

import { useRef, useState } from "react";

type ScanResult = {
  signal?: string;
  confidence?: number;
  entry?: number;
  stop_loss?: number;
  take_profit?: number;
  grade?: string;
  status?: string;

  candles_detected?: number;
  calibration?: number;

  bos?: boolean;
  choch?: boolean;
  liquidity?: boolean;
  fvg?: boolean;
  order_block?: boolean;
  premium_discount?: string;

  symbol?: string;
  lot_size?: number;
  risk_amount?: number;
  rr?: string;
  h4_trend?: string;
  current_price?: number;

  error?: boolean;
  message?: string;
};

export default function Home() {
  const [symbol, setSymbol] = useState("GOLD");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);

  const [loading, setLoading] = useState(false);
  const [liveLoading, setLiveLoading] = useState(false);

  const fileInput = useRef<HTMLInputElement>(null);

  const getApiUrl = () => {
    const configured = process.env.NEXT_PUBLIC_API_URL;

    if (!configured) {
      return "http://127.0.0.1:8000";
    }

    if (
      configured.startsWith("http://") ||
      configured.startsWith("https://")
    ) {
      return configured;
    }

    return `https://${configured}`;
  };

  const API_URL = getApiUrl();

  function chooseFile() {
    fileInput.current?.click();
  }

  function handleFile(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];

    if (!selected) {
      return;
    }

    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
  }

  async function analyzeScreenshot() {
    if (!file) {
      alert("Choose an MT5 screenshot first.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      setResult(data);

    } catch (error) {
      console.error(error);

      setResult({
        error: true,
        message:
          "Could not connect to VIPER AI backend.",
      });
    }

    setLoading(false);
  }

  async function scanLiveMarket() {
    setLiveLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/scan/${symbol}?balance=1000&risk=1`
      );

      const data = await response.json();

      setResult(data);

    } catch (error) {
      console.error(error);

      setResult({
        error: true,
        message:
          "Could not connect to MT5 scanner.",
      });
    }

    setLiveLoading(false);
  }

  const signal = result?.signal || "WAIT";

  const signalClass =
    signal === "BUY"
      ? "text-green-400"
      : signal === "SELL"
      ? "text-red-500"
      : "text-yellow-400";

  const boxClass =
    "rounded-3xl bg-[#11151C] border border-red-900/30 p-5";

  return (
    <main className="min-h-screen bg-[#07090C] text-white px-4 py-6">

      <div className="max-w-md mx-auto">

        {/* HEADER */}

        <div className={boxClass}>

          <div className="flex justify-between items-center">

            <div>
              <h1 className="text-3xl font-black tracking-wide">
                VIPER{" "}
                <span className="text-red-500">
                  AI
                </span>
              </h1>

              <p className="text-xs text-gray-400 mt-1">
                ICT Market Scanner
              </p>
            </div>

            <div className="text-right">

              <div className="flex items-center gap-2">

                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />

                <span className="text-xs text-green-400">
                  ONLINE
                </span>

              </div>

              <p className="text-[10px] text-gray-500 mt-1">
                VIPER v1.1
              </p>

            </div>

          </div>

        </div>

        {/* MARKET */}

        <div className="mt-4 rounded-2xl bg-[#11151C] border border-red-900/30 p-4">

          <p className="text-xs text-gray-400 mb-2">
            Market
          </p>

          <select
            value={symbol}
            onChange={(e) =>
              setSymbol(e.target.value)
            }
            className="w-full rounded-xl bg-[#0B0F14] p-3 border border-gray-700 outline-none"
          >

            <option value="GOLD">
              GOLD
            </option>

            <option value="US100Cash">
              US100Cash
            </option>

            <option value="EURUSD">
              EURUSD
            </option>

          </select>

          <button
            onClick={scanLiveMarket}
            disabled={liveLoading}
            className="w-full mt-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 rounded-xl py-3 font-bold transition"
          >
            {liveLoading
              ? "SCANNING MT5..."
              : "SCAN LIVE MARKET"}
          </button>

        </div>

        {/* SCREENSHOT */}

        <div className="mt-4 rounded-3xl bg-[#11151C] border border-red-900/30 p-5">

          <div className="flex justify-between items-center mb-4">

            <div>
              <h2 className="font-bold text-lg">
                Screenshot Scanner
              </h2>

              <p className="text-xs text-gray-500 mt-1">
                Upload your M5 MT5 chart
              </p>
            </div>

            <div className="text-red-500 text-xl">
              🐍
            </div>

          </div>

          <input
            ref={fileInput}
            type="file"
            accept="image/*"
            onChange={handleFile}
            className="hidden"
          />

          {!preview ? (

            <button
              onClick={chooseFile}
              className="w-full border border-dashed border-red-900/60 rounded-2xl p-8 text-center hover:border-red-500 transition"
            >

              <div className="text-4xl mb-3">
                📸
              </div>

              <p className="font-bold">
                Choose MT5 Screenshot
              </p>

              <p className="text-xs text-gray-500 mt-2">
                Best results with a clear M5 chart
              </p>

            </button>

          ) : (

            <div>

              <div className="rounded-2xl overflow-hidden border border-gray-800 bg-black">

                <img
                  src={preview}
                  alt="MT5 chart preview"
                  className="w-full object-contain max-h-[420px]"
                />

              </div>

              <button
                onClick={analyzeScreenshot}
                disabled={loading}
                className="w-full mt-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 rounded-xl py-3 font-bold transition"
              >
                {loading
                  ? "ANALYZING CHART..."
                  : "ANALYZE WITH VIPER AI"}
              </button>

              <button
                onClick={chooseFile}
                className="w-full mt-2 text-xs text-gray-400 hover:text-white"
              >
                Choose a different screenshot
              </button>

            </div>

          )}

        </div>

        {/* ERROR */}

        {result?.error && (

          <div className="mt-4 rounded-2xl border border-red-900 bg-red-950/30 p-4">

            <p className="text-red-400 font-bold">
              VIPER ERROR
            </p>

            <p className="text-sm text-gray-300 mt-1">
              {result.message}
            </p>

          </div>

        )}

        {/* RESULT */}

        {result && !result.error && (

          <>

            {/* SIGNAL */}

            <div className={`mt-4 ${boxClass}`}>

              <div className="flex justify-between items-center">

                <div>

                  <p className="text-xs text-gray-400">
                    VIPER SIGNAL
                  </p>

                  <h2
                    className={`text-5xl font-black ${signalClass}`}
                  >
                    {signal}
                  </h2>

                </div>

                <div className="text-right">

                  <p className="text-xs text-gray-400">
                    GRADE
                  </p>

                  <p className="text-3xl font-black text-red-400">
                    {result.grade || "-"}
                  </p>

                </div>

              </div>

              <div className="mt-5">

                <div className="flex justify-between text-sm mb-2">

                  <span>
                    Confidence
                  </span>

                  <span>
                    {result.confidence ?? 0}%
                  </span>

                </div>

                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">

                  <div
                    className="h-full bg-red-500 transition-all"
                    style={{
                      width: `${Math.min(
                        result.confidence ?? 0,
                        100
                      )}%`,
                    }}
                  />

                </div>

              </div>

            </div>

            {/* TRADE LEVELS */}

            <div className={`mt-4 ${boxClass}`}>

              <h3 className="text-red-400 font-bold mb-4">
                Trade Levels
              </h3>

              <div className="space-y-3 text-sm">

                <div className="flex justify-between">

                  <span className="text-gray-400">
                    Entry
                  </span>

                  <span className="font-bold">
                    {result.entry || "-"}
                  </span>

                </div>

                <div className="flex justify-between">

                  <span className="text-gray-400">
                    Stop Loss
                  </span>

                  <span className="font-bold text-red-400">
                    {result.stop_loss || "-"}
                  </span>

                </div>

                <div className="flex justify-between">

                  <span className="text-gray-400">
                    Take Profit
                  </span>

                  <span className="font-bold text-green-400">
                    {result.take_profit || "-"}
                  </span>

                </div>

              </div>

            </div>

            {/* ICT CONFLUENCE */}

            <div className={`mt-4 ${boxClass}`}>

              <h3 className="text-red-400 font-bold mb-4">
                ICT Confluence
              </h3>

              <div className="grid grid-cols-2 gap-3">

                <Confluence
                  name="BOS"
                  active={result.bos}
                />

                <Confluence
                  name="CHOCH"
                  active={result.choch}
                />

                <Confluence
                  name="Liquidity"
                  active={result.liquidity}
                />

                <Confluence
                  name="FVG"
                  active={result.fvg}
                />

                <Confluence
                  name="Order Block"
                  active={result.order_block}
                />

                <Confluence
                  name="Premium/Discount"
                  active={
                    result.premium_discount !== "-"
                  }
                />

              </div>

              <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between text-sm">

                <span className="text-gray-400">
                  Market Zone
                </span>

                <span className="font-bold">
                  {result.premium_discount || "-"}
                </span>

              </div>

            </div>

            {/* VISION QUALITY */}

            {result.candles_detected !== undefined && (

              <div className={`mt-4 ${boxClass}`}>

                <h3 className="text-red-400 font-bold mb-4">
                  Vision Diagnostics
                </h3>

                <div className="grid grid-cols-2 gap-4 text-sm">

                  <div>

                    <p className="text-gray-500">
                      Candles
                    </p>

                    <p className="font-bold">
                      {result.candles_detected}
                    </p>

                  </div>

                  <div>

                    <p className="text-gray-500">
                      Calibration
                    </p>

                    <p className="font-bold">
                      {result.calibration ?? 0}%
                    </p>

                  </div>

                </div>

              </div>

            )}

            {/* STATUS */}

            <div className={`mt-4 ${boxClass}`}>

              <h3 className="text-red-400 font-bold mb-2">
                VIPER Status
              </h3>

              <p className="text-sm text-gray-300">
                {result.status || "Analysis complete"}
              </p>

            </div>

          </>

        )}

        {/* FOOTER */}

        <div className="text-center mt-6 pb-6">

          <p className="text-[10px] text-gray-600">
            VIPER AI • ICT Screenshot Scanner
          </p>

        </div>

      </div>

    </main>
  );
}

function Confluence({
  name,
  active,
}: {
  name: string;
  active?: boolean;
}) {

  return (

    <div className="rounded-xl bg-[#0B0F14] border border-gray-800 p-3 flex justify-between items-center">

      <span className="text-xs text-gray-300">
        {name}
      </span>

      <span
        className={
          active
            ? "text-green-400 font-bold"
            : "text-gray-600"
        }
      >
        {active ? "✓" : "—"}
      </span>

    </div>

  );
}