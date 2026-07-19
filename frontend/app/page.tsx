"use client";

import { useState } from "react";
import { research, type ResearchResponse } from "@/lib/api";

function isArxivUrl(url: string): boolean {
  return url.includes("arxiv.org");
}

function RetryBadge({ count }: { count: number }) {
  const color =
    count === 0
      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
      : "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300";

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${color}`}>
      {count === 0 ? "No retries" : `${count} retr${count === 1 ? "y" : "ies"}`}
    </span>
  );
}

function ConfidenceBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 70
      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
      : pct >= 40
        ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
        : "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300";

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${color}`}>
      Confidence: {pct}%
    </span>
  );
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || status === "loading") return;

    setStatus("loading");
    setErrorMessage(null);

    try {
      const response = await research(question.trim());
      setResult(response);
      setStatus("success");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  const arxivSources = result?.sources.filter(isArxivUrl) ?? [];
  const webSources = result?.sources.filter((s) => !isArxivUrl(s)) ?? [];

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <a
          href="/sanctuary.html"
          className="w-fit text-xs font-medium text-neutral-500 underline-offset-2 hover:underline dark:text-neutral-400"
        >
          ← Visit the Writer&apos;s Sanctuary
        </a>
        <h1 className="text-2xl font-semibold tracking-tight">MultiAgent ResearchBot</h1>
        <p className="text-sm text-neutral-500 dark:text-neutral-400">
          Ask a research question. A planner, two researchers, a critic, and a writer agent
          will work through it together.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What are the latest advances in retrieval augmented generation?"
          disabled={status === "loading"}
          className="flex-1 rounded-lg border border-neutral-300 bg-white px-4 py-2.5 text-sm outline-none transition focus:border-neutral-500 disabled:opacity-60 dark:border-neutral-700 dark:bg-neutral-900 dark:focus:border-neutral-500"
        />
        <button
          type="submit"
          disabled={status === "loading" || !question.trim()}
          className="rounded-lg bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-200"
        >
          Research
        </button>
      </form>

      {status === "loading" && (
        <div className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-600 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
          <span className="flex gap-1">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400 [animation-delay:-0.3s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400 [animation-delay:-0.15s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400" />
          </span>
          Agent thinking…
        </div>
      )}

      {status === "error" && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-400">
          {errorMessage}
        </div>
      )}

      {status === "success" && result && (
        <div className="flex flex-col gap-6">
          <div className="flex flex-wrap items-center gap-2">
            <RetryBadge count={result.retry_count} />
            {typeof result.report.confidence_score === "number" && (
              <ConfidenceBadge score={result.report.confidence_score} />
            )}
            <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
              Status: {result.status}
            </span>
          </div>

          <section className="flex flex-col gap-3 rounded-xl border border-neutral-200 p-5 dark:border-neutral-800">
            <h2 className="text-lg font-semibold">Report</h2>
            {result.report.summary && (
              <p className="text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
                {result.report.summary}
              </p>
            )}
            {result.report.key_findings && result.report.key_findings.length > 0 && (
              <ul className="flex flex-col gap-1.5 text-sm text-neutral-700 dark:text-neutral-300">
                {result.report.key_findings.map((finding, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-neutral-400">•</span>
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {(arxivSources.length > 0 || webSources.length > 0) && (
            <section className="flex flex-col gap-4 rounded-xl border border-neutral-200 p-5 dark:border-neutral-800">
              <h2 className="text-lg font-semibold">Sources</h2>

              {arxivSources.length > 0 && (
                <div className="flex flex-col gap-1.5">
                  <h3 className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                    arXiv
                  </h3>
                  <ul className="flex flex-col gap-1 text-sm">
                    {arxivSources.map((url, i) => (
                      <li key={i}>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 underline-offset-2 hover:underline dark:text-blue-400"
                        >
                          {url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {webSources.length > 0 && (
                <div className="flex flex-col gap-1.5">
                  <h3 className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                    Web
                  </h3>
                  <ul className="flex flex-col gap-1 text-sm">
                    {webSources.map((url, i) => (
                      <li key={i}>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 underline-offset-2 hover:underline dark:text-blue-400"
                        >
                          {url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          <details className="group rounded-xl border border-neutral-200 p-5 dark:border-neutral-800">
            <summary className="cursor-pointer list-none text-lg font-semibold marker:content-none">
              <span className="inline-flex items-center gap-2">
                Critique
                {result.critique.verdict && (
                  <span className="text-xs font-normal text-neutral-400">
                    ({result.critique.verdict})
                  </span>
                )}
                <span className="ml-auto text-neutral-400 transition group-open:rotate-180">
                  ▾
                </span>
              </span>
            </summary>
            <div className="mt-3 flex flex-col gap-2 text-sm text-neutral-700 dark:text-neutral-300">
              <p>{result.critique.critique || "No critique text returned."}</p>
              {result.critique.follow_up_queries && result.critique.follow_up_queries.length > 0 && (
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                    Follow-up queries
                  </span>
                  <ul className="flex flex-col gap-1">
                    {result.critique.follow_up_queries.map((q, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-neutral-400">•</span>
                        <span>{q}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </details>
        </div>
      )}
    </main>
  );
}
