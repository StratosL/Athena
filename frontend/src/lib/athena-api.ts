/**
 * Athena chat API client.
 * Proxied via Vite dev server: /athena/* → localhost:3001/api/*
 */

const BASE_URL = "/athena-api"

export interface ChatRequest {
  input: string
  conversation_id?: string
}

export interface ChatResponse {
  response: string
  conversation_id: string
}

export async function athenaChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => null)
    const msg = err?.error || err?.message || err?.detail || `Something went wrong (HTTP ${res.status})`
    throw new Error(msg)
  }
  const data = await res.json()
  // Kibana Agent Builder returns { response: { message: "..." }, conversation_id }
  const message =
    data.response && data.response.message
      ? data.response.message
      : typeof data.response === "string"
        ? data.response
        : JSON.stringify(data)
  return { response: message, conversation_id: data.conversation_id }
}

export async function athenaTranscribe(blob: Blob): Promise<string> {
  const form = new FormData()
  form.append("file", blob, "audio.webm")
  const res = await fetch(`${BASE_URL}/transcribe`, {
    method: "POST",
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => null)
    const msg = err?.error || err?.message || err?.detail || `Something went wrong (HTTP ${res.status})`
    throw new Error(msg)
  }
  const data = await res.json()
  return data.text
}

export async function athenaSpeak(
  text: string,
  voice: string = "nova"
): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voice }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => null)
    const msg = err?.error || err?.message || err?.detail || `Something went wrong (HTTP ${res.status})`
    throw new Error(msg)
  }
  return res.blob()
}
