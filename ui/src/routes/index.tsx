import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { ArrowUp, ExternalLink,Info, Layers, MessageSquarePlus,  } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { DEFAULT_ENDPOINT, askBackend, getEndpoint, setEndpoint } from "@/lib/chat-api";
import ReactMarkdown from "react-markdown";


export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Finance AI Assistant — Ask your finance questions" },
      {
        name: "description",
        content:
          "A calm, terminal-inspired chat interface for the Finance AI Assistant. Ask portfolio, market and risk questions and get answers instantly.",
      },
      { property: "og:title", content: "Finance AI Assistant" },
      {
        property: "og:description",
        content:
          "A calm, terminal-inspired chat interface for the Finance AI Assistant, built by Sri Sakticharan.",
      },
    ],
  }),
  component: Index,
});

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  error?: boolean;
};

const SUGGESTIONS = [
  "What does Nvidia disclose about employee-related risks?",
  "What is Apple's current stock price?",
  "How does Microsoft describe AI competition in its 10-K?",
];

function Index() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"chat" | "about">("chat");
  const [endpoint, setEndpointState] = useState(DEFAULT_ENDPOINT);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setEndpointState(getEndpoint());
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;
    setView("chat");
    setInput("");
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
    ]);
    setLoading(true);
    try {
      const answer = await askBackend(trimmed);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Couldn't reach the backend at ${getEndpoint()} — ${
            err instanceof Error ? err.message : "unknown error"
          }`,
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen w-full bg-background font-sans text-foreground">
      {/* Sidebar */}
      <aside className="hidden w-72 flex-col border-r border-hairline bg-sidebar md:flex">
        <div className="flex h-full flex-col p-6">
          <button
            onClick={() => {
              setMessages([]);
              setView("chat");
            }}
            className="flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground ring-1 ring-primary transition-colors hover:opacity-90"
          >
            <MessageSquarePlus className="size-4 shrink-0" />
            New Conversation
          </button>
          <p className="mt-3 px-2 text-[11px] leading-relaxed text-muted-foreground">
            Covers Apple, Microsoft, and Nvidia — SEC filings, stock prices, and news.
          </p>
          <nav className="mt-8 flex flex-col gap-1">
            <span className="px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Suggested Inquiries
            </span>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="group flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground"
              >
                <span className="size-1.5 shrink-0 rounded-full bg-muted-foreground/40 group-hover:bg-foreground" />
                {s}
              </button>
            ))}
          </nav>

                    <div className="mt-8">
            <span className="px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              My Other Projects
            </span>

            <a
              href="https://phishguard-ai-tau-one.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 flex items-start gap-2 rounded-md px-2 py-2 text-left transition-colors hover:bg-accent/60"
            >
              <ExternalLink className="mt-0.5 size-3.5 shrink-0 text-muted-foreground" />
              <span className="flex flex-col gap-0.5">
                <span className="text-sm text-foreground">Phishing Detection</span>
                <span className="text-[11px] text-muted-foreground">
                  Multimodal — text, URL &amp; image classifiers
                </span>
              </span>
            </a>

            <a
              href="https://bmw-price-predictor-rhbypw6b6qntxdt9cszde8.streamlit.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 flex items-start gap-2 rounded-md px-2 py-2 text-left transition-colors hover:bg-accent/60"
            >
              <ExternalLink className="mt-0.5 size-3.5 shrink-0 text-muted-foreground" />
              <span className="flex flex-col gap-0.5">
                <span className="text-sm text-foreground">Used Car Price Predictor</span>
                <span className="text-[11px] text-muted-foreground">
                  BMW valuation — XGBoost, deployed on AWS
                </span>
              </span>
            </a>
          </div>




                  <div className="mt-auto border-t border-hairline pt-6">
          <Link
            to="/stack"
            className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground"
          >
            <Layers className="size-4 shrink-0" />
            Tech Stack
          </Link>
          <button
            onClick={() => setView(view === "about" ? "chat" : "about")}
            className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground"
          >
            <Info className="size-4 shrink-0" />
            About
          </button>
        </div>
             
        </div>
      </aside>

      {/* Main */}
      <main className="relative flex flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-hairline bg-background/80 px-8 backdrop-blur-sm">
          <h1 className="text-sm font-medium tracking-tight text-foreground">
            Finance AI Assistant
          </h1>
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-positive" />
            <span className="text-[11px] font-medium uppercase tracking-tight text-muted-foreground">
              Market Live
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-[64ch] space-y-12 px-6 py-12">
            {messages.length === 0 && !loading && (
              <div className="space-y-3 pt-16 text-center">
                <p className="text-sm text-muted-foreground">
                  Ask a finance question to begin.
                </p>
                <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground/60">
                  Session ready
                </p>
              </div>
            )}

            {messages.map((m) =>
              m.role === "user" ? (
                <div key={m.id} className="flex animate-fade-up justify-end">
                  <div className="max-w-[48ch] whitespace-pre-wrap rounded-xl bg-primary px-4 py-3 text-sm leading-relaxed text-primary-foreground ring-1 ring-primary">
                    {m.content}
                  </div>
                </div>
              ) : (
                <div key={m.id} className="flex animate-fade-up flex-col gap-4">
                  <div className="flex items-center gap-2">
                    <div className="flex size-5 shrink-0 items-center justify-center rounded bg-primary">
                      <div className="size-2 rounded-full bg-primary-foreground" />
                    </div>
                    <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                      Assistant
                    </span>
                  </div>
                  <div
                  className={`max-w-[56ch] text-sm leading-relaxed ${
                    m.error ? "text-destructive" : "text-foreground/80"
                  }`}
                >
                  <ReactMarkdown
                    components={{
                      strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
                    }}
                  >
                    {m.content}
                  </ReactMarkdown>
                </div>
                </div>
              ),
            )}

            {loading && (
              <div className="flex flex-col gap-4 opacity-60">
                <div className="flex items-center gap-2">
                  <div className="flex size-5 shrink-0 items-center justify-center rounded bg-surface">
                    <div className="size-1.5 animate-pulse rounded-full bg-muted-foreground" />
                  </div>
                  <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                    Analyzing Market Data
                  </span>
                </div>
                <div className="shimmer h-4 w-48 rounded bg-surface" />
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* Composer */}
        <div className="border-t border-hairline bg-background p-6">
          <div className="mx-auto max-w-[64ch]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="relative flex items-center"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Inquire about your holdings..."
                className="w-full rounded-lg bg-surface py-3 pl-4 pr-12 text-sm text-foreground outline-none ring-1 ring-hairline placeholder:text-muted-foreground/70 focus:ring-ring"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                aria-label="Send question"
                className="absolute right-2 rounded-md bg-primary p-1.5 text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-30"
              >
                <ArrowUp className="size-4" />
              </button>
            </form>
            <p className="mt-3 text-center text-[10px] text-muted-foreground">
              Financial insights are for informational purposes only. Crafted by Sri
              Sakticharan.
            </p>
          </div>
        </div>

        {/* About view */}
        {view === "about" && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-background/95 p-8">
            <div className="w-full max-w-md rounded-2xl bg-surface p-8 ring-1 ring-hairline">
              <h2 className="mb-4 text-xl font-medium tracking-tight">About Project</h2>
              <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
                Finance AI Assistant is a focused interface for asking financial
                questions and reading back clear, considered answers from the
                assistant's backend.
              </p>
              <div className="flex flex-col gap-3">
                <div className="flex justify-between border-b border-hairline py-2 text-xs">
                  <span className="font-medium uppercase text-muted-foreground">
                    Built by
                  </span>
                  <span className="text-foreground">Sri Sakticharan</span>
                </div>
                <div className="flex justify-between border-b border-hairline py-2 text-xs">
                  <span className="font-medium uppercase text-muted-foreground">
                    Interface
                  </span>
                  <span className="text-foreground">Single-page chat console</span>
                </div>
                <div className="flex justify-between border-b border-hairline py-2 text-xs">
                  <span className="font-medium uppercase text-muted-foreground">
                    Backend
                  </span>
                  <span className="max-w-[60%] truncate font-mono text-foreground">
                    {endpoint}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setView("chat")}
                className="mt-8 w-full rounded-md bg-primary py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
              >
                Return to Console
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
