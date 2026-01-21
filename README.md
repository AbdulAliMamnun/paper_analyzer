# 📄 Paper Analyzer – AI-Assisted Research Paper Review

A full-stack web application that analyzes academic research papers (PDFs) and produces a structured, high-signal summary using large language models.  
Built with **FastAPI**, **Google Gemini**, and a lightweight **HTML / CSS / JavaScript frontend**.

---

## 🚀 Overview

This project allows a user to upload a **PDF research paper** and receive a **structured analysis** that extracts reasoning, claims, assumptions, and limitations in a format suitable for technical and product decision-making.

Rather than paraphrasing the paper, the system performs **multi-stage reasoning**:
- Chunk-level analysis
- Global synthesis
- Structured Markdown output

---

## 🧠 Key Features

- 📄 PDF text extraction using `pdfplumber`
- ✂️ Safe chunking to respect LLM context limits
- 🧩 Multi-pass reasoning with LLMs
- 🧱 Deterministic Markdown structure for rendering
- 🌐 Browser-based UI
- 📋 Copy and download analysis as Markdown

---

## 🏗️ System Architecture

```
User (Browser)
   |
   |  Upload PDF
   v
Frontend (HTML / CSS / JS)
   |
   |  POST /api/analyze-pdf
   v
FastAPI Backend
   |
   |-- PDF Extraction (pdfplumber)
   |-- Text Chunking
   |-- Chunk-level LLM calls (Gemini)
   |-- Global synthesis prompt
   |-- Markdown formatting
   v
Structured Markdown Response
   |
   v
Rendered in Browser
```

---

## 📁 Project Structure

```
paper_analyzer/
│
├── backend/
│   ├── main.py                  # FastAPI application
│   └── services/
│       ├── gemini_client.py     # Gemini API wrapper
│       └── format_output.py     # Markdown normalization
│
├── frontend/
│   ├── index.html               # UI layout
│   ├── app.js                   # Client-side logic
│   └── styles.css               # Styling
│
├── .env                         # API keys (not committed)
├── .gitignore
└── README.md


Open in browser:
```
http://127.0.0.1:8000
```

---

## 🧪 How the Analysis Pipeline Works

1. User uploads a PDF
2. Backend extracts text from the document
3. Text is chunked to avoid context overflow
4. Each chunk is analyzed individually by the LLM
5. Chunk analyses are combined
6. A final synthesis prompt produces structured Markdown
7. Output is formatted and rendered in the UI

---

## 🎯 Design Decisions

- **Chunk-first processing** prevents hallucinations from long-context overload
- **Strict Markdown headers** ensure deterministic rendering
- **Inference allowed but labeled** when papers are underspecified
- **Minimal frontend** to maximize demo reliability

---

## 📌 Example Use Cases

- Rapid literature review
- Engineering feasibility assessment
- Research comparison
- Interview or academic demonstrations
- Internal research summaries

---

## ⚠️ Known Limitations

- Performance depends on PDF text quality
- Scanned PDFs without text will fail extraction
- Mathematical derivations are summarized, not re-derived
- Output quality depends on prompt and paper clarity

---

## 🤖 AI Assistance Disclosure

This project was developed with assistance from **ChatGPT** for:
- Writing and refining FastAPI backend functions
- Designing and iterating on LLM prompt structures
- Debugging integration issues
- Drafting this README
- Generating frontend logic and layout ideas

All architectural decisions, prompt intent, and final implementation choices were reviewed and integrated manually.

---

## 👤 Author

**Abdul Ali Mamnun**  
GitHub: https://github.com/AbdulAliMamnun
