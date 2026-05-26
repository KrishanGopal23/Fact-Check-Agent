import { FiGithub } from "react-icons/fi";


export default function Navbar() {
  return (
    <header className="bg-gradient-to-r from-[#3F51B5] via-[#6A43C6] to-[#C93A7A] shadow-lg shadow-[#6A43C6]/20">
      <nav className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5 text-white lg:px-8">
        <div className="flex items-center gap-3">
  <div className="h-10 w-10 overflow-hidden rounded-full border border-white/20">
    <img
      src="/logo.png"
      alt="Fact-Check logo"
      className="h-full w-full scale-125 object-cover"
    />
  </div>

  <div>
    <p className="text-xl font-semibold tracking-wide">
      Fact-Check Agent
    </p>
    <p className="text-xs text-white/75">
      Evidence-first verification
    </p>
  </div>
</div>
        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-7 text-sm text-white/80 sm:flex">
            <a className="transition hover:text-white" href="#workflow">
              Workflow
            </a>
            <a className="transition hover:text-white" href="#upload">
              Analyze PDF
            </a>
            <span className="rounded-full border border-white/35 bg-white/20 px-3 py-1.5 text-xs font-medium text-white">
              Live web evidence
            </span>
          </div>
          <a
            aria-label="View GitHub repository"
            className="group inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/30 bg-white/15 text-white/80 transition hover:bg-white/25 hover:text-white"
            href="https://github.com/KrishanGopal23/Fact-Check-Agent"
            rel="noreferrer"
            target="_blank"
            title="View GitHub repository"
          >
            <FiGithub size={18} />
          </a>
        </div>
      </nav>
    </header>
  );
}
