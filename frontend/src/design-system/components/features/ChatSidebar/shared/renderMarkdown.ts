import { marked } from "marked"
import DOMPurify from "dompurify"

marked.setOptions({ breaks: true })

export function renderMarkdown(text: string): string {
  if (typeof text !== "string") return String(text ?? "")
  const raw = marked.parse(text)
  if (typeof raw !== "string") return text
  return DOMPurify.sanitize(raw)
}
