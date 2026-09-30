/**
 * Talks to YOUR backend.
 *
 * Set the endpoint once here (or at runtime from the sidebar "Backend" field,
 * which stores it in localStorage under `finance-ai-endpoint`).
 *
 * Expected contract (adjust `body`/`parseAskResponse` below if yours differs):
 *   POST <endpoint>   { "question": "...", "previous_interaction_id": "..." | null }
 *     -> { "answer": "...", "interaction_id": "..." }
 *   POST <endpoint minus "/ask" plus "/summarize">   { "text": "..." }  ->  { "summary": "..." }
 */
export const DEFAULT_ENDPOINT =
  import.meta.env.VITE_API_URL || "http://localhost:8000/ask";

const STORAGE_KEY = "finance-ai-endpoint";

export function getEndpoint(): string {
  if (typeof window === "undefined") return DEFAULT_ENDPOINT;
  return window.localStorage.getItem(STORAGE_KEY) || DEFAULT_ENDPOINT;
}

export function setEndpoint(url: string) {
  if (typeof window !== "undefined")
    window.localStorage.setItem(STORAGE_KEY, url);
}

function summarizeEndpointFrom(askEndpoint: string): string {
  return askEndpoint.replace(/\/ask\/?$/, "/summarize");
}

export type AskResult = {
  answer: string;
  interactionId?: string;
};

function parseAskResponse(data: unknown): AskResult {
  if (typeof data === "string") return { answer: data };
  if (data && typeof data === "object") {
    const d = data as Record<string, unknown>;
    let answer = "";
    for (const key of [
      "answer",
      "response",
      "message",
      "output",
      "text",
      "result",
    ]) {
      const v = d[key];
      if (typeof v === "string") {
        answer = v;
        break;
      }
    }
    const interactionId =
      typeof d["interaction_id"] === "string"
        ? (d["interaction_id"] as string)
        : undefined;
    if (answer) return { answer, interactionId };
  }
  return { answer: JSON.stringify(data, null, 2) };
}

export async function askBackend(
  question: string,
  previousInteractionId?: string,
  signal?: AbortSignal,
): Promise<AskResult> {
  const res = await fetch(getEndpoint(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      previous_interaction_id: previousInteractionId ?? null,
    }),
    signal: signal ?? null,
  });

  if (!res.ok) {
    throw new Error(`Backend responded with ${res.status} ${res.statusText}`);
  }

  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return parseAskResponse(await res.json());
  }
  return { answer: await res.text() };
}

export async function summarizeBackend(text: string): Promise<string> {
  const res = await fetch(summarizeEndpointFrom(getEndpoint()), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    throw new Error(`Backend responded with ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  if (data && typeof data === "object" && typeof (data as any).summary === "string") {
    return (data as any).summary;
  }
  return typeof data === "string" ? data : JSON.stringify(data);
}
