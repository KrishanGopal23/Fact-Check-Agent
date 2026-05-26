import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { FiArrowRight, FiFileText, FiUploadCloud, FiX } from "react-icons/fi";

const MAX_BYTES = 10 * 1024 * 1024;

function formatBytes(size) {
  if (size < 1024 * 1024) {
    return `${Math.round(size / 1024)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export default function UploadBox({ busy, onAnalyze, uploadProgress }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState("");

  function validateAndSet(nextFile) {
    setValidationError("");
    if (!nextFile) {
      return;
    }
    if (nextFile.type !== "application/pdf" && !nextFile.name.toLowerCase().endsWith(".pdf")) {
      setValidationError("Upload a PDF file to begin analysis.");
      return;
    }
    if (nextFile.size > MAX_BYTES) {
      setValidationError("PDF files must be 10 MB or smaller.");
      return;
    }
    setFile(nextFile);
  }

  function handleDrop(event) {
    event.preventDefault();
    if (busy) return;
    setDragActive(false);
    validateAndSet(event.dataTransfer.files[0]);
  }

  return (
    <motion.section
      id="upload"
      className="glass mx-auto w-full max-w-4xl rounded-[2rem] p-5 sm:p-8"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-[#1f2138]">Audit a PDF document</h2>
        <p className="mt-2 text-sm leading-6 text-[#6b6f8f]">
          PDF only, up to 10 MB. Uploaded content is processed for this report and is not cached by
          the API.
        </p>
      </div>
      <div
        className={`relative rounded-2xl border-2 border-dashed px-6 py-11 text-center transition ${
          dragActive
            ? "border-[#7A2FE0] bg-[#E7E9F5]"
            : "border-[#E7E9F5] bg-white/80 hover:border-[#C9B6F7]"
        }`}
        onDragEnter={(event) => {
          event.preventDefault();
          if (!busy) setDragActive(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          setDragActive(false);
        }}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          className="sr-only"
          type="file"
          accept=".pdf,application/pdf"
          disabled={busy}
          onChange={(event) => validateAndSet(event.target.files[0])}
        />
        <FiUploadCloud className="mx-auto mb-4 text-[#7A2FE0]" size={39} />
        <p className="text-base font-medium text-[#1f2138]">Drop a PDF here</p>
        <p className="mt-2 text-sm text-[#7a7fa6]">or</p>
        <button
          className="mt-4 rounded-xl border border-[#C9B6F7] bg-white px-5 py-2.5 text-sm font-medium text-[#1f2138] transition hover:bg-[#EEEAF4] disabled:cursor-not-allowed disabled:opacity-50"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
          type="button"
        >
          Browse files
        </button>
      </div>

      {validationError && (
        <p className="mt-4 rounded-xl border border-[#E0488D]/30 bg-[#F0D6E3] px-4 py-3 text-sm text-[#C93A7A]">
          {validationError}
        </p>
      )}

      {file && (
        <div className="mt-5 flex flex-col gap-4 rounded-2xl border border-[#E7E9F5] bg-white p-4 sm:flex-row sm:items-center">
          <div className="flex min-w-0 grow items-center gap-3">
            <FiFileText className="shrink-0 text-[#3D63F0]" size={25} />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-[#1f2138]">{file.name}</p>
              <p className="mt-0.5 text-xs text-[#7a7fa6]">{formatBytes(file.size)}</p>
            </div>
            {!busy && (
              <button
                aria-label="Remove selected file"
                className="ml-auto rounded-lg p-2 text-[#7a7fa6] hover:bg-[#EEEAF4] hover:text-[#1f2138] sm:hidden"
                onClick={() => setFile(null)}
                type="button"
              >
                <FiX />
              </button>
            )}
          </div>
          <button
            className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#3D63F0] via-[#7A2FE0] to-[#E0488D] px-5 py-3 text-sm font-semibold text-white shadow-md shadow-[#7A2FE0]/25 transition hover:from-[#3456d8] hover:via-[#6a28c6] hover:to-[#c63f7c] disabled:cursor-wait disabled:opacity-60"
            disabled={busy}
            onClick={() => onAnalyze(file)}
            type="button"
          >
            {busy
              ? uploadProgress < 100
                ? `Uploading ${uploadProgress}%`
                : "Analyzing..."
              : "Run fact-check"}
            {!busy && <FiArrowRight />}
          </button>
        </div>
      )}
    </motion.section>
  );
}
