# Voice Client UI Redesign — Glassmorphism Dark

## Context

The voice client at `localhost:3001` works functionally but looks basic — flat dark theme, plain text messages, no markdown rendering, no branding. For the hackathon demo video (deadline Feb 27), the UI needs to be visually impressive. The user requested a **full redesign** with **glassmorphism dark** aesthetic.

## Files to Modify

| File | Change |
|------|--------|
| `voice-client/style.css` | Full rewrite — glassmorphism variables, frosted glass surfaces, markdown content styles, mic ring animation, responsive |
| `voice-client/index.html` | CDN imports (marked.js, DOMPurify, Inter font), logo in header, settings as overlay modal, mic ring elements |
| `voice-client/voice.js` | Markdown rendering in `addMessage()`, agent avatar + timestamps, new welcome screen with clickable hints, settings overlay toggle |
| `voice-client/athena-logo.svg` | **New** — minimalist owl SVG for header, welcome screen, and agent avatar |

`serve.py` is **not modified** — it already serves any static file from the directory.

## CDN Libraries (no build step)

- **marked.js** v15 (~40KB gz) — markdown-to-HTML for agent responses
- **DOMPurify** v3 (~15KB gz) — sanitize rendered HTML
- **Google Fonts: Inter** — modern UI font (weights 400/500/600/700)

## Key Changes

### 1. Visual Foundation (CSS)
- Background: gradient from `#0a0c1a` to `#141233` with radial accent glows
- All surfaces (header, input, settings, bubbles) use `backdrop-filter: blur(20px)` + translucent backgrounds + subtle borders
- Accent shifted from `#7c4dff` to richer indigo `#6c5ce7` with `#a29bfe` light variant
- "Athena" title in gradient text (`background-clip: text`)
- Inter font family

### 2. Markdown Rendering (JS)
- `addMessage("agent", text)` changes from `el.textContent = text` to `DOMPurify.sanitize(marked.parse(text))` via `innerHTML`
- Full markdown content styles inside `.message.agent`: headers, code blocks (with `pre` background), lists, tables, links, blockquotes
- User messages remain `textContent` (plain text)
- `white-space: normal` on agent bubbles (markdown handles its own spacing), `pre-wrap` kept for user bubbles

### 3. Agent Avatar + Timestamps
- Agent messages wrapped in `.message-row` flex container with 28px owl avatar to the left
- Subtle timestamps on all messages (`toLocaleTimeString` HH:MM)

### 4. Welcome Screen
- Floating owl logo (64px) with glow + `@keyframes float`
- Gradient title text
- **3 clickable hint chips** ("What did I write about last week?", etc.) — clicking sends the prompt. Great for demo video.

### 5. Settings Panel → Overlay Modal
- Settings become a centered glassmorphism modal over a dimmed backdrop
- Click backdrop or close button to dismiss
- Custom toggle switch for auto-speak checkbox

### 6. Mic Recording Animation
- 3 concentric `.mic-ring` divs behind the mic button
- On recording: rings pulse outward in staggered sequence (`animation-delay: 0s, 0.4s, 0.8s`)
- Mic button goes red with gradient + glow shadow

### 7. Responsive
- 400px–1200px breakpoints
- Subtitle hidden on mobile, padding/font adjustments

## DOM ID Compatibility

All existing IDs preserved: `messages`, `text-input`, `send-btn`, `mic-btn`, `voice-status`, `text-input-container`, `voice-input-container`, `mode-toggle`, `mode-icon-mic`, `mode-icon-text`, `settings-toggle`, `settings-panel`, `voice-select`, `auto-speak`. The JS `getElementById` calls in `init()` continue to work unchanged.

## Implementation Order

1. Create `athena-logo.svg`
2. Rewrite `style.css` (complete)
3. Update `index.html` (CDN links, header logo, settings overlay, mic rings)
4. Update `voice.js` (marked config, `addMessage`, `addWelcome`, `toggleSettings`)

## Verification

1. Start voice server: `cd voice-client && uv run python serve.py`
2. Open `http://localhost:3001` — verify glassmorphism background, header with logo, welcome screen with floating owl and clickable hints
3. Type a message — verify user bubble (right-aligned, plain text, timestamp)
4. Verify agent response renders as markdown (bold, lists, headers, code blocks if present) with avatar
5. Toggle to voice mode — verify mic button gradient, click to record, confirm concentric ring animation
6. Open settings — verify modal overlay with backdrop blur
7. Resize browser to ~400px — verify responsive layout
