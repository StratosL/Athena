/**
 * Hook encapsulating MediaRecorder for voice capture.
 */

import { useRef, useCallback, useState } from "react"

export function useVoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "audio/webm"

    const recorder = new MediaRecorder(stream, { mimeType })
    chunksRef.current = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }

    recorder.start()
    recorderRef.current = recorder
    setIsRecording(true)
  }, [])

  const stopRecording = useCallback((): Promise<Blob> => {
    return new Promise((resolve) => {
      const recorder = recorderRef.current
      if (!recorder || recorder.state === "inactive") {
        resolve(new Blob())
        return
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType })
        // Release mic tracks
        recorder.stream.getTracks().forEach((t) => t.stop())
        recorderRef.current = null
        setIsRecording(false)
        resolve(blob)
      }
      recorder.stop()
    })
  }, [])

  const cancelRecording = useCallback(() => {
    const recorder = recorderRef.current
    if (!recorder) return
    recorder.onstop = null
    if (recorder.state !== "inactive") recorder.stop()
    recorder.stream.getTracks().forEach((t) => t.stop())
    recorderRef.current = null
    chunksRef.current = []
    setIsRecording(false)
  }, [])

  return { isRecording, startRecording, stopRecording, cancelRecording }
}
