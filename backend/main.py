from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pdfplumber
import io
from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.services.gemini_client import generate_text
from backend.services.format_output import format_output

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------
load_dotenv()

app = FastAPI(title="Paper Analyzer", version="1.0.0")

# Serve frontend at /app (so API routes remain clean under /api/*)
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

# Optional: redirect root to the UI
@app.get("/", include_in_schema=False)
def ui():
    return FileResponse("frontend/index.html")

# ------------------------------------------------------------
# Response model
# ------------------------------------------------------------
class AnalyzePDFResponse(BaseModel):
    model: str
    overall_markdown: str


# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 6000, max_chunks: int = 10) -> list[str]:
    text = (text or "").strip()
    chunks = []
    i = 0
    while i < len(text) and len(chunks) < max_chunks:
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        i += chunk_size
    return chunks


def extract_pdf_text_bytes(pdf_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                text_parts.append(t)
    return "\n\n".join(text_parts).strip()


def build_chunk_analysis(full_text: str) -> str:
    chunks = chunk_text(full_text, chunk_size=6000, max_chunks=10)
    partial = []

    for idx, chunk in enumerate(chunks):
        prompt = f"""
You are analyzing chunk {idx+1} of a research paper.

Return concise bullet notes under these headings ONLY:
- Main points
- Claims
- Evidence/Experiments
- Assumptions
- Limitations
- Any equations / math mentioned (if any)

Text:
{chunk}
""".strip()

        notes = generate_text(prompt)
        partial.append(f"--- Chunk {idx+1} ---\n{notes}")

    return "\n\n".join(partial)


def overall_prompt(combined_analysis: str) -> str:
    return f"""
You are an expert research-paper evaluator.

You MUST return VALID MARKDOWN.

Use EXACTLY these headers (spelled exactly):

## Problem
## Approach
## Key Claims
## Evidence Quality
## Assumptions
## Red Flags

CRITICAL RULES:
- Every section MUST contain real content (no empty sections)
- Do NOT say "Not addressed explicitly."
- If the paper doesn't state something directly, infer a reasonable, practical answer and label it as **Inference**
- Be concrete and specific
- Prefer bullet points

Chunk notes:
{combined_analysis}
""".strip()


# ------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze-pdf", response_model=AnalyzePDFResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()

    paper_text = extract_pdf_text_bytes(pdf_bytes)
    if not paper_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF (maybe scanned).")

    # Prevent huge inputs from blowing quota/time
    paper_text = paper_text[:60000]

    combined_analysis = build_chunk_analysis(paper_text)

    md = generate_text(overall_prompt(combined_analysis))

    # Hard block bad filler text (demo-safe)
    md = md.replace("Not addressed explicitly.", "Inference: Not clearly specified in the excerpt; best-effort summary based on available text.")
    md = md.replace("Not addressed explicitly", "Inference: Not clearly specified in the excerpt; best-effort summary based on available text.")

    md = format_output(md)

    return AnalyzePDFResponse(
        model="models/gemini-2.0-flash",
        overall_markdown=md
    )
