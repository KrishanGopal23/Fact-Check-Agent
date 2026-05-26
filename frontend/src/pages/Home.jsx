import { useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { FiAlertCircle, FiDownload, FiFilter } from "react-icons/fi";
import Footer from "../components/Footer.jsx";
import Hero from "../components/Hero.jsx";
import LoadingScreen from "../components/LoadingScreen.jsx";
import Navbar from "../components/Navbar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatsCards from "../components/StatsCards.jsx";
import UploadBox from "../components/UploadBox.jsx";
import { statusDesign } from "../constants/statusDesign.js";
import { factCheckPdf, getErrorMessage } from "../services/api.js";

const filters = [
  "ALL",
  "VERIFIED",
  "INACCURATE",
  "FALSE",
  "OUTDATED",
  "MISLEADING",
  "INSUFFICIENT_EVIDENCE",
];

function saveDownload(contents, filename, mimeType) {
  const blob = new Blob([contents], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function csvValue(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

export default function Home() {
  const [report, setReport] = useState(null);
  const [state, setState] = useState("idle");
  const [error, setError] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [filter, setFilter] = useState("ALL");
  const resultRef = useRef(null);

  async function handleAnalyze(file) {
    setError("");
    setReport(null);
    setFilter("ALL");
    setState("loading");
    setUploadProgress(0);
    try {
      const data = await factCheckPdf(file, setUploadProgress);
      setReport(data);
      setState("complete");
      window.setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth" }), 80);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
      setState("error");
    }
  }

  const displayedResults = useMemo(() => {
    if (!report) return [];
    return filter === "ALL"
      ? report.results
      : report.results.filter((result) => result.verdict === filter);
  }, [filter, report]);

  function downloadJson() {
    saveDownload(
      JSON.stringify(report, null, 2),
      "fact-check-report.json",
      "application/json;charset=utf-8",
    );
  }

  function downloadCsv() {
    const header = ["Claim", "Verdict", "Confidence", "Corrected fact", "Explanation", "Sources"];
    const rows = report.results.map((result) => [
      result.claim.claim,
      result.verdict,
      result.confidence,
      result.corrected_fact,
      result.explanation,
      result.sources.map((source) => source.url).join(" | "),
    ]);
    const csv = [header, ...rows].map((row) => row.map(csvValue).join(",")).join("\n");
    saveDownload(csv, "fact-check-report.csv", "text/csv;charset=utf-8");
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="grid-lines pointer-events-none absolute inset-x-0 top-0 h-[780px]" />
      <div className="relative">
        <Navbar />
        <Hero />
        <main className="px-6 lg:px-8">
          <UploadBox
            busy={state === "loading"}
            onAnalyze={handleAnalyze}
            uploadProgress={uploadProgress}
          />

          {state === "loading" && <LoadingScreen />}

          {error && (
            <motion.div
              className="mx-auto mt-7 flex max-w-4xl items-start gap-3 rounded-2xl border border-[#E0488D]/30 bg-[#F0D6E3] p-5 text-[#7b1c4f]"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <FiAlertCircle className="mt-0.5 shrink-0 text-[#C93A7A]" size={20} />
              <div>
                <p className="font-medium">Analysis could not be completed</p>
                <p className="mt-1 text-sm text-[#7b1c4f]/80">{error}</p>
              </div>
            </motion.div>
          )}

          {report && (
            <section className="mx-auto mt-14 w-full max-w-7xl" ref={resultRef}>
              <div className="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#6A43C6]">
                    Verification report
                  </p>
                  <h2 className="mt-3 text-3xl font-semibold text-[#1f2138]">
                    {report.document.filename}
                  </h2>
                  <p className="mt-2 text-sm text-[#6b6f8f]">
                    {report.document.pages} pages analyzed | Risk level:{" "}
                    <span className="font-semibold text-[#1f2138]">{report.summary.risk_level}</span>
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    className="flex items-center gap-2 rounded-xl border border-[#C9B6F7] bg-white px-4 py-3 text-sm text-[#1f2138] hover:bg-[#EEEAF4]"
                    onClick={downloadCsv}
                    type="button"
                  >
                    <FiDownload /> CSV
                  </button>
                  <button
                    className="flex items-center gap-2 rounded-xl border border-[#C9B6F7] bg-white px-4 py-3 text-sm text-[#1f2138] hover:bg-[#EEEAF4]"
                    onClick={downloadJson}
                    type="button"
                  >
                    <FiDownload /> JSON
                  </button>
                </div>
              </div>

              <StatsCards summary={report.summary} />

              <div className="glass mt-6 rounded-2xl p-5 text-sm leading-7 text-[#4b4f6f]">
                <span className="mr-3 rounded-full bg-[#EEEAF4] px-3 py-1 text-xs font-semibold text-[#6A43C6]">
                  Summary
                </span>
                {report.summary.narrative}
              </div>

              {report.results.length === 0 ? (
                <div className="glass mt-8 rounded-2xl p-9 text-center text-[#6b6f8f]">
                  No independently verifiable factual claims were extracted from this PDF.
                </div>
              ) : (
                <>
                  <div className="subtle-scrollbar mt-9 flex items-center gap-2 overflow-x-auto pb-2">
                    <FiFilter className="mr-2 shrink-0 text-[#8a8fb0]" />
                    {filters.map((option) => (
                      <button
                        className={`shrink-0 rounded-full border px-4 py-2 text-xs font-medium transition ${
                          filter === option
                            ? "border-[#7A2FE0] bg-[#EEEAF4] text-[#6A43C6]"
                            : "border-[#E7E9F5] text-[#6b6f8f] hover:border-[#C9B6F7]"
                        }`}
                        key={option}
                        onClick={() => setFilter(option)}
                        type="button"
                      >
                        {option === "ALL" ? "All claims" : statusDesign[option].label}
                      </button>
                    ))}
                  </div>
                  <div className="mt-4 space-y-4">
                    {displayedResults.map((result, index) => (
                      <ResultCard result={result} index={index} key={result.claim.id} />
                    ))}
                    {displayedResults.length === 0 && (
                      <p className="rounded-2xl border border-[#E7E9F5] p-8 text-center text-[#6b6f8f]">
                        No claims match this verdict filter.
                      </p>
                    )}
                  </div>
                </>
              )}
            </section>
          )}
        </main>
        <Footer />
      </div>
    </div>
  );
}
