import { motion } from "framer-motion";
import { FiAlertTriangle, FiCheckCircle, FiTarget, FiTrendingUp } from "react-icons/fi";

export default function StatsCards({ summary }) {
  const corrections = summary.false + summary.inaccurate + summary.outdated + summary.misleading;
  const cards = [
    { label: "Claims checked", value: summary.total_claims, icon: FiTarget, accent: "text-[#3D63F0]" },
    { label: "Verified", value: summary.verified, icon: FiCheckCircle, accent: "text-[#7A2FE0]" },
    { label: "Needs correction", value: corrections, icon: FiAlertTriangle, accent: "text-[#E0488D]" },
    { label: "Avg. confidence", value: `${summary.average_confidence}%`, icon: FiTrendingUp, accent: "text-[#6A43C6]" },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(({ label, value, icon: Icon, accent }, index) => (
        <motion.div
          className="glass rounded-2xl p-5"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          key={label}
        >
          <Icon className={accent} size={19} />
          <p className="mt-5 text-3xl font-semibold text-[#1f2138]">{value}</p>
          <p className="mt-1 text-sm text-[#6b6f8f]">{label}</p>
        </motion.div>
      ))}
    </div>
  );
}
