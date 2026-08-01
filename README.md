<p align="center">
  <h1 align="center">📜 The Writer's Sanctuary</h1>
  <p align="center">
    <b>A Multi-Agent AI Research System for Deep Literature Analysis</b>
  </p>

  <p align="center">
    CrewAI • LangGraph • FastAPI • Next.js • Groq • Gemini Flash • arXiv • Multi-Agent Systems
  </p>
</p>

---

## Overview

The Writer's Sanctuary is a production-ready multi-agent AI research assistant designed to emulate the workflow of a team of academic researchers.

Instead of retrieving documents once and generating a response, the system coordinates multiple specialized AI agents that plan, search, critique, retry, and synthesize research before producing a final report.

Unlike conventional Retrieval-Augmented Generation (RAG) systems, the architecture incorporates an iterative **Critic → Retry** mechanism that continuously evaluates evidence quality and forces additional retrieval when supporting evidence is insufficient.

The result is a structured research report containing:

- Research Question
- Abstract
- Key Findings
- Evidence-backed Conclusions
- Confidence Score
- Evidence Table
- Research References

---

# Live Demo

**Website**

https://multiagent-researchbot.vercel.app/sanctuary.html

**Source Code**

https://github.com/Neel-K26/multiagent-researchbot

---

# Demo

(Add GIF here)

---

# Motivation

Most AI research assistants follow a simple pipeline:

```
User
 ↓
Retriever
 ↓
LLM
 ↓
Answer
```

This approach often suffers from

- shallow retrieval
- hallucinations
- weak citations
- no quality control
- single-pass reasoning

The Writer's Sanctuary approaches research differently.

Every answer is reviewed by another AI before being accepted.

---

# System Architecture

```
                 User Query
                      │
                      ▼
            Planner Agent (Groq)
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
Researcher A                   Researcher B
(arXiv Search)                 (Web Search)
      │                               │
      └───────────────┬───────────────┘
                      ▼
             Critic Agent (Gemini)
                      │
          Weak Evidence?
             │          │
            Yes        No
             │          │
             ▼          ▼
      Retry Research    Writer Agent
                           │
                           ▼
                   Final Research Report
```

---

# Multi-Agent Workflow

## Planner

The planner decomposes the user's question into targeted retrieval strategies.

Responsibilities

- query decomposition
- planning
- search strategy generation
- task routing

---

## Researcher A

Specialized academic researcher.

Sources

- arXiv API

Responsibilities

- literature search
- academic paper retrieval
- paper filtering

---

## Researcher B

Specialized web researcher.

Sources

- Web Search

Responsibilities

- latest developments
- industrial reports
- documentation
- news

---

## Critic

The most important agent.

Rather than accepting the first answer, the critic evaluates

- evidence quality
- citation relevance
- completeness
- hallucination risk
- unsupported claims

If quality is below threshold

↓

the system automatically launches another research iteration.

---

## Writer

Produces the final report.

Output includes

- Abstract
- Findings
- References
- Confidence Score
- Evidence Table

---

# Features

✔ Multi-Agent Architecture

✔ Parallel Research

✔ Academic + Web Retrieval

✔ Evidence Critique

✔ Retry Loop

✔ Confidence Scoring

✔ Citation Generation

✔ Structured Research Reports

✔ Dark Academia Interface

✔ Responsive UI

---

# Tech Stack

## Backend

- FastAPI
- CrewAI
- LangGraph
- Python
- Groq API
- Gemini Flash
- arXiv API

---

## Frontend

- Next.js
- React
- TailwindCSS

---

## Infrastructure

- Vercel
- Async API Calls
- REST APIs

---

# Sample Output

The generated report contains

- Research Question
- Abstract
- Key Findings
- References
- Confidence Score
- Evidence Table

Example

```
Research Question

What are the latest advances in supervised machine learning?

↓

Planner generates search strategy

↓

Parallel literature retrieval

↓

Critic validates evidence

↓

Writer synthesizes report

↓

21 references

↓

Confidence Score 80%
```

---

# Design Philosophy

The project follows one principle:

> Retrieval alone is not research.

Research requires

- planning
- evidence gathering
- verification
- critique
- synthesis

The Writer's Sanctuary models this workflow using specialized AI agents rather than relying on a single LLM response.

---

# Repository Structure

```
app/
backend/
frontend/
agents/
api/
components/
prompts/
utils/
```

---

# Future Improvements

- CrossRef Integration
- PubMed Support
- Semantic Scholar Retrieval
- Citation Graph Search
- PDF Upload
- Knowledge Graph Generation
- Multi-hop Verification
- Human Feedback Loop
- Report Export (PDF / DOCX)
- Local LLM Support
- Research Memory

---

# Why This Project?

Most public CrewAI demonstrations focus on simple automation tasks.

This project explores a different problem:

> Can multiple AI agents collaboratively perform research while critiquing each other's work before producing an answer?

The resulting architecture combines planning, parallel retrieval, iterative verification, and synthesis into a unified research workflow.

---

# Author

Neel Khairnar

AI Engineer • Machine Learning • LLMs • Agentic AI • Retrieval Systems

GitHub

https://github.com/Neel-K26

LinkedIn

(https://www.linkedin.com/in/neel-k-43b797217/)

Portfolio

(https://neelkhairnar-portfolio.vercel.app/)

