import { motion } from "framer-motion";
import { FiCheckCircle, FiDatabase, FiSearch } from "react-icons/fi";

const signals = [
  { icon: FiDatabase, title: "Extract", detail: "Stats, dates, and technical claims" },
  { icon: FiSearch, title: "Retrieve", detail: "Current web evidence and sources" },
  { icon: FiCheckCircle, title: "Decide", detail: "Verdicts with supported corrections" },
];

export default function Hero() {
  return (
    <section className="mx-auto grid w-full max-w-7xl gap-12 px-6 pb-12 pt-12 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-18 lg:pt-20">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <p className="mb-6 inline-flex rounded-full border border-[#F0D6E3] bg-[#F0D6E3] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[#C93A7A]">
          Truth layer for document claims
        </p>
        <h1 className="gradient-text max-w-3xl text-5xl font-semibold leading-[1.08] tracking-tight sm:text-6xl">
          Check every factual claim before it ships.
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-8 text-[#4b4f6f]">
          Upload a PDF and receive a sourced audit of its statistics, dates, financial figures,
          and technical assertions using Gemini analysis and live Tavily retrieval.
        </p>
      </motion.div>

      <motion.div
        id="workflow"
        className="glass relative overflow-hidden rounded-3xl p-5 sm:p-7"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.08 }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-[#E7E9F5] via-white to-[#F3E4EC]" />
        <div className="relative space-y-4">
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.2em] text-[#7a7fa6]">
            Verification pipeline
          </p>
          {signals.map(({ icon: Icon, title, detail }, index) => (
            <div
              className="flex items-center gap-4 rounded-2xl border border-white/70 bg-white/80 p-4"
              key={title}
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#E7E9F5] text-[#6A43C6]">
                <Icon size={19} />
              </div>
              <div className="grow">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-[#1f2138]">{title}</p>
                  <span className="text-xs text-[#9aa0bf]">0{index + 1}</span>
                </div>
                <p className="mt-1 text-sm text-[#666b8b]">{detail}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
