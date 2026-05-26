import { motion } from "framer-motion";
import { FiLoader } from "react-icons/fi";

const steps = [
  "Reading PDF text",
  "Extracting factual claims with Gemini",
  "Searching live sources with Tavily",
  "Comparing evidence and generating report",
];

export default function LoadingScreen() {
  return (
    <motion.section
      className="glass mx-auto mt-8 w-full max-w-4xl rounded-[2rem] p-6 sm:p-8"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center gap-3">
        <FiLoader className="animate-spin text-[#6A43C6]" size={23} />
        <div>
          <p className="font-medium text-[#1f2138]">Analyzing your document</p>
          <p className="text-sm text-[#6b6f8f]">Retrieval time depends on the number of claims found.</p>
        </div>
      </div>
      <div className="mt-7 h-1.5 overflow-hidden rounded-full bg-[#E7E9F5]">
        <motion.div
          className="h-full w-1/3 rounded-full bg-gradient-to-r from-[#3D63F0] via-[#7A2FE0] to-[#E0488D]"
          animate={{ x: ["-100%", "300%"] }}
          transition={{ duration: 1.55, ease: "easeInOut", repeat: Infinity }}
        />
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-2">
        {steps.map((step) => (
          <div className="flex items-center gap-3 text-sm" key={step}>
            <span className="h-2 w-2 rounded-full bg-[#C9B6F7]" />
            <span className="text-[#6b6f8f]">{step}</span>
          </div>
        ))}
      </div>
      <p className="mt-6 text-xs text-[#8a8fb0]">
        Results appear once the server completes the full evidence audit.
      </p>
    </motion.section>
  );
}
