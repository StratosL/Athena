/**
 * WebSocket connection hook for real-time timer updates.
 */

import { useEffect, useRef, useCallback, useState } from "react"
import { useTimerStore } from "@/stores/timerStore"
import type { TimerState } from "@/lib/api"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

// Convert http/https to ws/wss
const WS_URL = API_URL.replace(/^http/, "ws")

interface WSMessage {
  type: string
  remaining_seconds?: number
  state?: TimerState
  session_id?: string
  completed?: boolean
  message?: string
}

interface UsePomodoroWebSocketReturn {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  connect: (sessionId: string) => void
  disconnect: () => void
  sendMessage: (message: object) => void
}

// Exponential backoff delays in ms
const BACKOFF_DELAYS = [3000, 6000, 12000, 24000, 48000]

export function usePomodoroWebSocket(): UsePomodoroWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const retryCountRef = useRef(0)
  const sessionIdRef = useRef<string | null>(null)
  const intentionalDisconnectRef = useRef(false)

  const {
    setState,
    setRemainingSeconds,
    incrementPomodoro,
    setConnected,
    reset,
  } = useTimerStore()

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data: WSMessage = JSON.parse(event.data)

        switch (data.type) {
          case "TICK":
            if (data.remaining_seconds !== undefined) {
              setRemainingSeconds(data.remaining_seconds)
            }
            if (data.state) {
              setState(data.state)
            }
            break

          case "STATE_CHANGE":
            if (data.state) {
              setState(data.state)
            }
            if (data.remaining_seconds !== undefined) {
              setRemainingSeconds(data.remaining_seconds)
            }
            break

          case "SESSION_COMPLETE":
            if (data.completed) {
              incrementPomodoro()
            }
            reset()
            break

          case "SESSION_STOPPED":
            reset()
            break

          case "PONG":
            // Keepalive response, nothing to do
            break

          case "ERROR":
            setError(data.message || "Unknown error")
            break

          default:
            console.warn("Unknown WebSocket message type:", data.type)
        }
      } catch {
        console.error("Failed to parse WebSocket message")
      }
    },
    [setState, setRemainingSeconds, incrementPomodoro, reset]
  )

  const connect = useCallback(
    (sessionId: string) => {
      // Cleanup existing connection
      if (wsRef.current) {
        wsRef.current.close()
      }

      // Reset intentional disconnect flag when starting a new connection
      intentionalDisconnectRef.current = false
      sessionIdRef.current = sessionId
      setIsConnecting(true)
      setError(null)

      const ws = new WebSocket(`${WS_URL}/pomodoro/ws/${sessionId}`)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setIsConnecting(false)
        setConnected(true)
        retryCountRef.current = 0
        setError(null)
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsConnecting(false)
        setConnected(false)

        // Only auto-reconnect if this wasn't an intentional disconnect
        if (sessionIdRef.current && !intentionalDisconnectRef.current) {
          const delay =
            BACKOFF_DELAYS[
              Math.min(retryCountRef.current, BACKOFF_DELAYS.length - 1)
            ]
          retryCountRef.current++

          setTimeout(() => {
            // Double-check before reconnecting
            if (sessionIdRef.current && !intentionalDisconnectRef.current) {
              connect(sessionIdRef.current)
            }
          }, delay)
        }
      }

      ws.onerror = () => {
        setError("WebSocket connection failed")
        setIsConnecting(false)
      }

      ws.onmessage = handleMessage
    },
    [handleMessage, setConnected]
  )

  const disconnect = useCallback(() => {
    // Set flag to prevent auto-reconnect
    intentionalDisconnectRef.current = true
    sessionIdRef.current = null
    retryCountRef.current = 0

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
    setIsConnecting(false)
    setConnected(false)
    reset()
  }, [setConnected, reset])

  const sendMessage = useCallback((message: object) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return {
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    sendMessage,
  }
}
