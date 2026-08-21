import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/stack")({
  head: () => ({
    meta: [
      { title: "Finance AI Assistant — Tech Stack" },
      { name: "description", content: "The technologies powering the Finance AI Assistant." },
    ],
  }),
  component: StackPage,
});

const STACK = [
  { category: "LLM", items: ["Google Gemini (gemini-3.1-flash-lite)"] },
  { category: "Embeddings & Reranking", items: ["Voyage AI (voyage-4 embeddings, rerank-2.5)"] },
  { category: "Vector Database", items: ["Qdrant Cloud"] },
  { category: "Agent Orchestration", items: ["Custom tool-calling loop (Gemini function calling)"] },
  { category: "Backend API", items: ["FastAPI (Python)"] },
  { category: "Data Sources", items: ["SEC EDGAR (10-K filings)", "yfinance (live market data)", "Tavily (news search)"] },
  { category: "Containerization", items: ["Docker"] },
  { category: "CI/CD", items: ["GitHub Actions — test, build, and deploy automatically on every push"] },
  { category: "Deployment", items: ["Render (backend API)", "Qdrant Cloud (vector database)"] },
  { category: "Frontend", items: ["React, TanStack Start, Tailwind CSS"] },
  { category: "Testing", items: ["pytest"] },
];

function StackPage() {
  return (
    <div className="min-h-screen bg-background px-6 py-12 text-foreground">
      <div className="mx-auto max-w-[64ch]">
        <Link
          to="/"
          className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground"
        >
          ← Back to console
        </Link>
        <h1 className="mt-6 text-2xl font-medium tracking-tight">Tech Stack</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          What's actually running under the hood of this project.
        </p>
        <div className="mt-8 flex flex-col gap-6">
          {STACK.map((group) => (
            <div key={group.category} className="border-b border-hairline pb-6">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {group.category}
              </h2>
              <ul className="mt-2 flex flex-col gap-1">
                {group.items.map((item) => (
                  <li key={item} className="text-sm text-foreground/80">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}