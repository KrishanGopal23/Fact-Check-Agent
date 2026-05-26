import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { FiChevronDown, FiExternalLink, FiFileText } from "react-icons/fi";
import { statusDesign } from "../constants/statusDesign.js";

export default function ResultCard({ result, index }) {
  const [expanded, setExpanded] = useState(result.verdict !== "VERIFIED");
  const design = statusDesign[result.verdict];

  return (
    <motion.article
      className="glass overflow-hidden rounded-2xl"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.24) }}
    >
      <button
        aria-expanded={expanded}
        className="flex w-full flex-col gap-4 p-5 text-left sm:flex-row sm:items-start sm:justify-between"
        onClick={() => setExpanded((open) => !open)}
        type="button"
      >
        <div className="min-w-0">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${design.pill}`}>
              {design.label}
            </span>
            <span className="rounded-full bg-[#EEEAF4] px-3 py-1 text-xs text-[#6b6f8f]">
              {result.claim.category}
            </span>
            {result.claim.page_number && (
              <span className="flex items-center gap-1 text-xs text-[#8a8fb0]">
                <FiFileText /> Page {result.claim.page_number}
              </span>
            )}
          </div>
          <p className="text-base leading-7 text-[#1f2138]">{result.claim.claim}</p>
        </div>
        <div className="flex shrink-0 items-center gap-3 text-sm text-[#6b6f8f]">
          <span>
            <strong className="font-semibold text-[#1f2138]">{result.confidence}%</strong> confidence
          </span>
          <FiChevronDown
            className={`transition ${expanded ? "rotate-180" : ""}`}
            aria-hidden="true"
          />
        </div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="border-t border-[#E7E9F5] px-5 pb-6 pt-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8a8fb0]">
                Assessment
              </p>
              <p className="mt-2 text-sm leading-7 text-[#4b4f6f]">{result.explanation}</p>
              {result.corrected_fact && (
                <div className="mt-4 rounded-xl border border-[#C9B6F7]/60 bg-[#EEEAF4] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#6A43C6]">
                    Corrected fact
                  </p>
                  <p className="mt-2 text-sm leading-7 text-[#3b3f5c]">{result.corrected_fact}</p>
                </div>
              )}
              <p className="mb-3 mt-6 text-xs font-semibold uppercase tracking-[0.18em] text-[#8a8fb0]">
                Evidence sources
              </p>
              {result.sources.length === 0 ? (
                <p className="text-sm text-[#6b6f8f]">No usable source evidence was retrieved.</p>
              ) : (
                <div className="space-y-3">
                  {result.sources.map((source) => (
                    <a
                      className="block rounded-xl border border-[#E7E9F5] bg-white p-4 transition hover:border-[#C9B6F7]"
                      href={source.url}
                      key={source.url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm font-medium text-[#1f2138]">{source.title}</p>
                        <FiExternalLink className="mt-1 shrink-0 text-[#8a8fb0]" />
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-xs text-[#8a8fb0]">
                        <span>{source.domain}</span>
                        <span className="rounded-full border border-[#C9B6F7] px-2 py-0.5 text-[#6A43C6]">
                          {source.authority}
                        </span>
                      </div>
                      <p className="mt-3 line-clamp-3 text-sm leading-6 text-[#6b6f8f]">
                        {source.snippet}
                      </p>
                    </a>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
