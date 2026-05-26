import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 240000,
});

export async function factCheckPdf(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/fact-check", formData, {
    onUploadProgress: (event) => {
      if (event.total) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
  return response.data;
}

export function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.code === "ECONNABORTED") {
    return "Analysis timed out. Try a shorter document or run it again.";
  }
  return "The verification service could not be reached. Please try again.";
}
