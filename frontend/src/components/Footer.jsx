import { FiShield } from "react-icons/fi";

export default function Footer() {
  return (
    <footer className="mx-auto mt-20 flex w-full max-w-7xl flex-col justify-between gap-3 border-t border-[#E7E9F5] px-6 py-8 text-sm text-[#8a8fb0] sm:flex-row lg:px-8">
      <p className="flex items-center gap-2">
        <FiShield /> Fact-Check Agent
      </p>
      <p>Verdicts should be reviewed alongside the linked source evidence.</p>
    </footer>
  );
}
