---
title: "Meeting Debrief"
tags: [skill, meetings, tasks]
created: 2026-02-16
trigger_phrases:
  - "meeting debrief"
  - "process meeting notes"
  - "extract tasks from meeting"
---

# Meeting Debrief

Process a meeting note: extract action items, classify them by priority, create tasks in Artemis, and append a summary to the note.

## Steps

1. **Identify the meeting note**
   - Ask the user which meeting note to process, or use the most recent one
   - Tool: `vault_read` with operation=read_note

2. **Extract action items**
   - Scan the note content for action items, decisions, and follow-ups
   - Look for patterns: "TODO", "action:", names + verbs, deadlines mentioned

3. **Classify tasks**
   - Assign each action item an Eisenhower quadrant with reasoning
   - Present the numbered list to the user for review

4. **Create approved tasks**
   - After user confirms (may adjust quadrants or remove items)
   - Tool: `artemis_create_task` for each approved task

5. **Append debrief summary to note**
   - Tool: `vault_manage` with operation=append_note
   - Add a "## Debrief" section with: tasks created (with IDs), key decisions, follow-up dates

## Expected Output

- Numbered list of extracted tasks with quadrant classification
- After approval: confirmation of created tasks with Artemis IDs
- Updated meeting note with debrief section appended
