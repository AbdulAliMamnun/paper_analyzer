const pdfFile = document.getElementById("pdfFile");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");

const renderedEl = document.getElementById("rendered");
const rawEl = document.getElementById("raw");

const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");

let lastMarkdown = "";

function setStatus(msg) {
  statusEl.textContent = msg || "";
}

function setError(msg) {
  errorEl.textContent = msg || "";
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze";
}

function renderMarkdown(md) {
  lastMarkdown = md || "";

  // Render markdown safely
  const html = marked.parse(lastMarkdown);
  renderedEl.innerHTML = DOMPurify.sanitize(html);

  rawEl.textContent = lastMarkdown;

  const hasOutput = lastMarkdown.trim().length > 0;
  copyBtn.disabled = !hasOutput;
  downloadBtn.disabled = !hasOutput;
}

async function analyzePDF(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch("/api/analyze-pdf", {
    method: "POST",
    body: form
  });

  // Try JSON; if not JSON, show text
  const contentType = res.headers.get("content-type") || "";
  if (!res.ok) {
    if (contentType.includes("application/json")) {
      const err = await res.json();
      throw new Error(err.detail ? JSON.stringify(err.detail) : JSON.stringify(err));
    } else {
      const txt = await res.text();
      throw new Error(txt || "Request failed.");
    }
  }

  return await res.json();
}

analyzeBtn.addEventListener("click", async () => {
  setError("");
  setStatus("");

  const file = pdfFile.files && pdfFile.files[0];
  if (!file) {
    setError("Please choose a PDF first.");
    return;
  }
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    setError("Only PDF files are supported.");
    return;
  }

  try {
    setLoading(true);
    setStatus(`Uploading ${file.name}...`);
    renderMarkdown(""); // clear output

    setStatus("Extracting + analyzing (may take a moment)...");
    const data = await analyzePDF(file);

    const md = data.overall_markdown || "";
    renderMarkdown(md);

    setStatus(`OK • ${file.name}`);
  } catch (e) {
    setStatus("");
    setError(`Error: ${e.message}`);
    renderMarkdown("");
  } finally {
    setLoading(false);
  }
});

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(lastMarkdown);
    setStatus("Copied to clipboard.");
    setTimeout(() => setStatus(""), 1200);
  } catch {
    setError("Copy failed (browser permissions).");
  }
});

downloadBtn.addEventListener("click", () => {
  const blob = new Blob([lastMarkdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "analysis.md";
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
});
