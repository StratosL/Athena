/**
 * Hook that wires chatStore + athena-api for text chat.
 * Invalidates TanStack Query caches after agent responses so that
 * actions performed via Athena (create task, start pomodoro, etc.)
 * are reflected in the dashboard without manual refresh.
 */

import { useCallback } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useChatStore } from "@/stores/chatStore"
import { athenaChat } from "@/lib/athena-api"
import { pomodoroKeys } from "./usePomodoro"
import { taskKeys } from "./useTasks"
import { dailyPlanKeys } from "./useDailyPlan"
import { analyticsKeys } from "./useAnalytics"

export function useAthenaChat() {
  const queryClient = useQueryClient()
  const addMessage = useChatStore((s) => s.addMessage)
  const setStatus = useChatStore((s) => s.setStatus)
  const conversationId = useChatStore((s) => s.conversationId)
  const setConversationId = useChatStore((s) => s.setConversationId)

  const sendMessage = useCallback(
    async (text: string): Promise<string | null> => {
      addMessage("user", text)
      setStatus("thinking")

      try {
        const resp = await athenaChat({
          input: text,
          conversation_id: conversationId ?? undefined,
        })

        if (resp.conversation_id) {
          setConversationId(resp.conversation_id)
        }

        addMessage("agent", resp.response)
        setStatus("idle")

        // Invalidate dashboard caches so agent-triggered changes
        // (tasks, pomodoro, daily plan) appear immediately in the UI
        queryClient.invalidateQueries({ queryKey: pomodoroKeys.all })
        queryClient.invalidateQueries({ queryKey: taskKeys.all })
        queryClient.invalidateQueries({ queryKey: dailyPlanKeys.all })
        queryClient.invalidateQueries({ queryKey: analyticsKeys.all })

        return resp.response
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : "Failed to reach Athena"
        addMessage("agent", `Sorry, I couldn't process that. ${msg}`)
        setStatus("idle")
        return null
      }
    },
    [addMessage, setStatus, conversationId, setConversationId, queryClient]
  )

  return { sendMessage }
}
