 HOOK — The Problem (20 seconds)

  "Be honest — your best ideas are scattered across a dozen apps right now. Meeting notes here, tasks in your email, that late night idea, living in some random app. We're great at
  collecting information. But Connecting and acting on it? That's the hard part."

  [SCREEN: Quick montage — Obsidian vault, sticky notes, email, Slack. Fast cuts, 2-3 seconds each]

  ---
  MEET ATHENA (30 seconds)

  "What you need isn't another note-taking app. It's a central intelligence that can understand, connect, and act on your knowledge. Meet Athena — a conversational AI agent that
  bridges your personal knowledge vault with your productivity system. Its mission: turn scattered knowledge into focused action, all through natural conversation."

  [SCREEN: Athena logo + mission statement text on screen]

  "It can search your notes semantically, write new ones, extract tasks, plan your day, remember past conversations, and even nudge you proactively. Let me show you."

  [SCREEN: Quick feature grid/icons — 6 capabilities as bullet points or cards]

  ---
  LIVE DEMO (90-100 seconds)

  This is where you win or lose. Show, don't tell.

  Demo Beat 1 — Semantic Search (~20s)

  "I've got an Obsidian vault with project notes, meeting notes, ideas and daily journals. Let me ask Athena something vague..."

  [SCREEN SHARE: Artemis dashboard with Athena chat sidebar open]
  [TYPE: "What were my ideas about improving the user onboarding experience?"]

  "Notice I didn't search for exact keywords. ELSER semantic search understands the meaning — it pulls up notes about progressive disclosure, onboarding flows, even related meeting
  notes I had forgotten about."

  [SCREEN SHARE: Athena's response with vault path citations]

  Demo Beat 2 — Bidirectional Vault Access (~25s)

  "Now here's what makes Athena different from every other AI notes tool — it's not read-only. Watch this."

  [TYPE: "Create a new note in Ideas called 'Gamified Onboarding Flow' with the key points from that research"]

  "It drafts the note, shows me what it'll create, and waits for my go-ahead. Human-in-the-loop — it never writes without permission."

  [SCREEN SHARE: Athena proposing the note → user confirms → note created]
  [SCREEN SHARE: Quick flip to Obsidian showing the new file actually exists]

  Demo Beat 3 — Task Extraction + Daily Planning (~30s)

  "But Athena doesn't just manage notes — it turns knowledge into action. Let me ask it to look at my meeting notes from last week."

  [TYPE: "Extract action items from my Sprint Review meeting notes"]

  "It finds the tasks, classifies each one using the Eisenhower Matrix — urgent and important, or something that can wait — and presents them for approval. Once I confirm, they land
  in Artemis as real tasks."

  [SCREEN SHARE: Athena showing classified tasks → user confirms → tasks appear in Artemis quadrant grid]

  "And now — 'Plan my day.'"

  [TYPE: "Plan my day"]

  "It uses the 1-3-5 rule: one big focus task, three medium, five small. A structured, achievable plan built from my actual commitments."

  [SCREEN SHARE: Daily plan proposal in chat → Artemis daily plan view populated]

  Demo Beat 4 — Voice (Optional, 15s)

  "And because sometimes you just want to talk to your second brain..."

  [SCREEN SHARE: Toggle to voice mode, ask a question by speaking, hear Athena respond via TTS]

  ---
  UNDER THE HOOD (45 seconds)

  "So how does this work? Athena is eight interconnected services, orchestrated by Docker Compose."

  [SCREEN: Architecture diagram — the dual-path one from your docs]

  "The brain is Elastic Agent Builder, sitting in the center. It has two paths to your knowledge. Path one: Elasticsearch with ELSER embeddings for deep semantic search and analytics. 

Path two: a direct filesystem connection to your vault for real-time reads and writes. This dual-path design is what gives Athena both search intelligence and hands-on file access."

  [SCREEN: Highlight each path on the diagram as you mention it]

  "The tools are exposed via the MCP protocol — 14 MCP tools plus 6 ES|QL tools, all available to the agent through natural conversation. The frontend is React, the backend is FastAPI with Supabase, and everything ships as a single docker compose up."

  [SCREEN: Tech stack table — brief flash, 3-4 seconds]

  ---
  WHAT'S NEXT (20 seconds)

  "Athena is actively evolving. On the roadmap: streaming responses for real-time conversation feel, multi-vault support, and my personal favorite — a community skill marketplace
  where you can share reusable workflows like weekly reviews or project planning templates."

  [SCREEN: Roadmap bullets on screen]

  ---
  CLOSE (15 seconds)

Athena proves that your second brain can do more than store — it can think, act, and work alongside you. 

Thank you to Elastic and the DevPost team for putting this hackathon     together. 

This has been an incredible build, and honestly, the best part is what comes next." 

 [SCREEN: Athena logo + GitHub link + "Built with Elastic Agent Builder"]