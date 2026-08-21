/**
 * Talks to YOUR backend.
 *
 * Set the endpoint once here (or at runtime from the sidebar "Backend" field,
 * which stores it in localStorage under `finance-ai-endpoint`).
 *
 * Expected contract (adjust `body`/`readAnswer` below if yours differs):
 *   POST <endpoint>   { "question": "..." }  ->  { "answer": "..." }
 */
export const DEFAULT_ENDPOINT = import.meta.env.VITE_API_URL || "http://localhost:8000/ask";


const STORAGE_KEY = "finance-ai-endpoint";

export function getEndpoint(): string {
  if (typeof window === "undefined") return DEFAULT_ENDPOINT;
  return window.localStorage.getItem(STORAGE_KEY) || DEFAULT_ENDPOINT;
}

export function setEndpoint(url: string) {
  if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, url);
}

function readAnswer(data: unknown): string {
  if (typeof data === "string") return data;
  if (data && typeof data === "object") {
    const d = data as Record<string, unknown>;
    for (const key of ["answer", "response", "message", "output", "text", "result"]) {
      const v = d[key];
      if (typeof v === "string") return v;
    }
  }
  return JSON.stringify(data, null, 2);
}

export async function askBackend(question: string, signal?: AbortSignal): Promise<string> {
  const res = await fetch(getEndpoint(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal: signal ?? null,
  });

  if (!res.ok) {
    throw new Error(`Backend responded with ${res.status} ${res.statusText}`);
  }

  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return readAnswer(await res.json());
  }
  return await res.text();
}
