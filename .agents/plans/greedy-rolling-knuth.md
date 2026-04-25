# Plan: Scaffold Remotion Demo Video Project

## Context

The Athena hackathon deadline is Feb 27. The demo video (3 min, 30% of score) is the highest-priority remaining deliverable. We're scaffolding a Remotion project to produce the full demo video — polished intro/outro, title cards, transitions, with raw screen recordings embedded as `<Video>` assets.

## Approach

Scaffold a new `demo-video/` directory at the project root using `npx create-video@latest`, then customize it with compositions matching the demo flow from PRD section 11.

## Project Location

```
Athena/demo-video/
```

## Scaffold Steps

1. **Run `npx create-video@latest`** in the project root, targeting `demo-video/` directory (Hello World template)
2. **Install additional packages:**
   - `@remotion/transitions` — scene transitions (fade, slide, wipe)
   - `@remotion/google-fonts` — clean typography (Inter or similar)
3. **Copy assets** into `demo-video/public/`:
   - `Athena-logo.jpg` from `assets/`
4. **Replace scaffolded code** with our composition structure

## Composition Structure

One main composition (`DemoVideo`) that sequences all scenes via `<TransitionSeries>`. Individual scenes as separate components:

```
demo-video/src/
├── Root.tsx                    ← Register DemoVideo composition
├── DemoVideo.tsx               ← Main composition (sequences all scenes)
├── scenes/
│   ├── Intro.tsx               ← Logo reveal + title + tagline
│   ├── ProblemStatement.tsx    ← "Your notes, tasks, and knowledge are scattered"
│   ├── ArchitectureOverview.tsx← Tech stack visual (Elastic, MCP, Obsidian, Artemis)
│   ├── DemoSection.tsx         ← Reusable wrapper for screen recording clips
│   ├── VoiceDemo.tsx           ← Voice interaction highlight
│   └── Outro.tsx               ← Built with, GitHub link, CTA
├── components/
│   ├── TitleCard.tsx           ← Reusable title card between sections
│   ├── AnimatedText.tsx        ← Typewriter / fade-in text
│   └── FeatureCallout.tsx      ← Animated feature bullet points
└── lib/
    ├── colors.ts               ← Brand color palette
    ├── fonts.ts                ← Font loading (Inter / JetBrains Mono)
    └── transitions.ts          ← Shared transition configs
```

## Video Specs

| Setting | Value |
|---------|-------|
| Resolution | 1920×1080 |
| FPS | 30 |
| Duration | ~3 min (5400 frames) |
| Codec | H.264 (MP4) |

## Scene Breakdown (approximate timing)

| Scene | Duration | Frames |
|-------|----------|--------|
| Intro (logo + title) | 5s | 150 |
| Problem statement | 5s | 150 |
| Architecture overview | 8s | 240 |
| Demo: Semantic search | 30s | 900 |
| Demo: Note reading + task extraction | 30s | 900 |
| Demo: Artemis integration | 30s | 900 |
| Demo: Voice interaction | 20s | 600 |
| Demo: Skills/automation | 20s | 600 |
| Outro | 7s | 210 |
| **Buffer/transitions** | ~25s | ~750 |
| **Total** | ~180s | ~5400 |

Demo sections will use `<Video>` to embed raw screen recordings (recorded separately with OBS). The Remotion project wraps them with title cards, transitions, and callout overlays.

## Brand/Style

- Dark theme (matches Athena frontend's glassmorphism aesthetic)
- Primary color from the existing frontend palette
- Font: Inter (body) + JetBrains Mono (code/tech labels)
- Smooth spring-based transitions between scenes

## Verification

1. `cd demo-video && npm install` succeeds
2. `npm run dev` launches Remotion Studio in browser
3. All scenes render in the preview timeline
4. `npx remotion render src/index.ts DemoVideo out/demo.mp4` produces output

## Files Modified

- **New directory:** `demo-video/` (scaffolded by create-video, then customized)
- **No existing files modified**
