/**
 * Hook orchestrating voice: record → transcribe → chat → speak.
 */

import { useRef, useCallback } from "react"
import { useChatStore } from "@/stores/chatStore"
import { useVoiceRecorder } from "./useVoiceRecorder"
import { useAthenaChat } from "./useAthenaChat"
import { athenaTranscribe, athenaSpeak } from "@/lib/athena-api"

function getVoiceSetting(): string {
  try {
    return localStorage.getItem("athena-voice") || "nova"
  } catch {
    return "nova"
  }
}

function getAutoSpeak(): boolean {
  try {
    const val = localStorage.getItem("athena-auto-speak")
    return val === null ? true : val === "true"
  } catch {
    return true
  }
}

export function useAthenaVoice() {
  const status = useChatStore((s) => s.status)
  const setStatus = useChatStore((s) => s.setStatus)
  const { isRecording, startRecording, stopRecording, cancelRecording } =
    useVoiceRecorder()
  const { sendMessage } = useAthenaChat()
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const blobUrlRef = useRef<string | null>(null)

  const cleanupAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current)
      blobUrlRef.current = null
    }
  }, [])

  const speakText = useCallback(
    async (text: string) => {
      if (!getAutoSpeak()) return
      try {
        setStatus("speaking")
        const blob = await athenaSpeak(text, getVoiceSetting())
        cleanupAudio()
        const url = URL.createObjectURL(blob)
        blobUrlRef.current = url
        const audio = new Audio(url)
        audioRef.current = audio
        audio.onended = () => {
          cleanupAudio()
          setStatus("idle")
        }
        audio.play()
      } catch {
        setStatus("idle")
      }
    },
    [setStatus, cleanupAudio]
  )

  const stopSpeaking = useCallback(() => {
    cleanupAudio()
    setStatus("idle")
  }, [cleanupAudio, setStatus])

  const handleMicClick = useCallback(async () => {
    if (status === "speaking") {
      stopSpeaking()
      return
    }

    if (isRecording) {
      // Stop recording → transcribe → chat → speak
      const blob = await stopRecording()
      if (blob.size === 0) return

      try {
        setStatus("transcribing")
        const transcript = await athenaTranscribe(blob)
        if (!transcript.trim()) {
          setStatus("idle")
          return
        }
        // sendMessage adds the user message and sets status to thinking
        const response = await sendMessage(transcript)
        if (response && getAutoSpeak()) {
          await speakText(response)
        }
      } catch {
        setStatus("idle")
      }
    } else {
      // Start recording
      try {
        await startRecording()
        setStatus("recording")
      } catch {
        setStatus("idle")
      }
    }
  }, [
    status,
    isRecording,
    stopRecording,
    startRecording,
    sendMessage,
    speakText,
    stopSpeaking,
    setStatus,
  ])

  const handleCancel = useCallback(() => {
    if (isRecording) {
      cancelRecording()
      setStatus("idle")
    } else if (status === "speaking") {
      stopSpeaking()
    }
  }, [isRecording, status, cancelRecording, stopSpeaking, setStatus])

  return {
    isRecording,
    handleMicClick,
    handleCancel,
    stopSpeaking,
    speakText,
  }
}
