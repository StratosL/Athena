// Athena Voice Client
// State machine, text chat, voice recording, Whisper STT, OpenAI TTS
(function () {
  "use strict";

  // --- State Machine ---
  const STATES = { IDLE: "IDLE", RECORDING: "RECORDING", TRANSCRIBING: "TRANSCRIBING", THINKING: "THINKING", SPEAKING: "SPEAKING" };
  let state = STATES.IDLE;
  let isVoiceMode = false;
  let conversationId = null;
  let mediaRecorder = null;
  let audioChunks = [];
  let currentAudio = null;

  // --- Settings ---
  let selectedVoice = localStorage.getItem("athena-voice") || "nova";
  let autoSpeak = localStorage.getItem("athena-auto-speak") !== "false";

  // --- DOM References ---
  let $messages, $textInput, $sendBtn, $micBtn, $voiceStatus;
  let $textContainer, $voiceContainer, $modeToggle, $modeIconMic, $modeIconText;
  let $settingsToggle, $settingsPanel, $voiceSelect, $autoSpeak;

  // --- Initialization ---

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    $messages = document.getElementById("messages");
    $textInput = document.getElementById("text-input");
    $sendBtn = document.getElementById("send-btn");
    $micBtn = document.getElementById("mic-btn");
    $voiceStatus = document.getElementById("voice-status");
    $textContainer = document.getElementById("text-input-container");
    $voiceContainer = document.getElementById("voice-input-container");
    $modeToggle = document.getElementById("mode-toggle");
    $modeIconMic = document.getElementById("mode-icon-mic");
    $modeIconText = document.getElementById("mode-icon-text");
    $settingsToggle = document.getElementById("settings-toggle");
    $settingsPanel = document.getElementById("settings-panel");
    $voiceSelect = document.getElementById("voice-select");
    $autoSpeak = document.getElementById("auto-speak");

    // Load settings
    $voiceSelect.value = selectedVoice;
    $autoSpeak.checked = autoSpeak;

    // Event listeners
    $textInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        onSend();
      }
    });
    $sendBtn.addEventListener("click", onSend);
    $micBtn.addEventListener("click", onMicClick);
    $modeToggle.addEventListener("click", toggleMode);
    $settingsToggle.addEventListener("click", toggleSettings);
    $voiceSelect.addEventListener("change", function () {
      selectedVoice = $voiceSelect.value;
      localStorage.setItem("athena-voice", selectedVoice);
    });
    $autoSpeak.addEventListener("change", function () {
      autoSpeak = $autoSpeak.checked;
      localStorage.setItem("athena-auto-speak", autoSpeak);
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        if (state === STATES.RECORDING) {
          cancelRecording();
        } else if (state === STATES.SPEAKING) {
          stopSpeaking();
        }
      }
      if (e.key === " " && isVoiceMode && document.activeElement !== $textInput) {
        e.preventDefault();
        onMicClick();
      }
    });

    // Welcome message
    addWelcome();
    updateUI();
  }

  // --- UI Updates ---

  function setState(newState) {
    state = newState;
    updateUI();
  }

  function updateUI() {
    // Mic button state
    $micBtn.classList.toggle("recording", state === STATES.RECORDING);
    $micBtn.disabled = state === STATES.TRANSCRIBING || state === STATES.THINKING;

    // Send button
    $sendBtn.disabled = state !== STATES.IDLE;

    // Text input
    $textInput.disabled = state !== STATES.IDLE;

    // Voice status text
    var statusText = {
      IDLE: "Click to speak",
      RECORDING: "Recording... click to stop",
      TRANSCRIBING: "Transcribing...",
      THINKING: "Athena is thinking...",
      SPEAKING: "Speaking... click to stop",
    };
    $voiceStatus.textContent = statusText[state] || "";

    // Mode toggle icon
    $modeIconMic.classList.toggle("hidden", isVoiceMode);
    $modeIconText.classList.toggle("hidden", !isVoiceMode);
    $modeToggle.classList.toggle("active", isVoiceMode);

    // Show/hide input containers
    $textContainer.classList.toggle("hidden", isVoiceMode);
    $voiceContainer.classList.toggle("hidden", !isVoiceMode);
  }

  function removeStatusIndicator() {
    var indicator = $messages.querySelector(".status-indicator");
    if (indicator) indicator.remove();
  }

  function showStatusIndicator(type, text) {
    removeStatusIndicator();
    var el = document.createElement("div");
    el.className = "status-indicator";

    if (type === "recording") {
      el.innerHTML = '<div class="dot recording"></div>' + text;
    } else if (type === "speaking") {
      el.innerHTML =
        '<div class="bars"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>' +
        text;
    } else {
      el.innerHTML = '<div class="dot"></div>' + text;
    }

    $messages.appendChild(el);
    scrollToBottom();
  }

  // --- Messages ---

  function addMessage(role, text) {
    removeStatusIndicator();
    var el = document.createElement("div");
    el.className = "message " + role;
    el.textContent = text;
    $messages.appendChild(el);
    scrollToBottom();
  }

  function addWelcome() {
    var el = document.createElement("div");
    el.className = "welcome";
    el.innerHTML =
      "<h2>Welcome to Athena</h2>" +
      "<p>Ask about your notes, manage tasks, or explore your second brain.<br>" +
      'Type below or click the mic icon to switch to voice mode.</p>';
    $messages.appendChild(el);
  }

  function scrollToBottom() {
    $messages.scrollTop = $messages.scrollHeight;
  }

  // --- Mode Toggle ---

  function toggleMode() {
    if (state !== STATES.IDLE) return;
    isVoiceMode = !isVoiceMode;
    updateUI();
    if (!isVoiceMode) {
      $textInput.focus();
    }
  }

  function toggleSettings() {
    $settingsPanel.classList.toggle("hidden");
    $settingsToggle.classList.toggle("active");
  }

  // --- Text Chat ---

  function onSend() {
    var text = $textInput.value.trim();
    if (!text || state !== STATES.IDLE) return;
    $textInput.value = "";
    handleTextInput(text);
  }

  async function handleTextInput(text) {
    addMessage("user", text);
    showStatusIndicator("thinking", "Athena is thinking...");
    setState(STATES.THINKING);

    try {
      var response = await chat(text);
      removeStatusIndicator();
      addMessage("agent", response);

      if (autoSpeak && isVoiceMode) {
        showStatusIndicator("speaking", "Speaking...");
        setState(STATES.SPEAKING);
        await speak(response);
        removeStatusIndicator();
      }
    } catch (err) {
      removeStatusIndicator();
      addMessage("system", "Error: " + err.message);
    }

    setState(STATES.IDLE);
    if (!isVoiceMode) {
      $textInput.focus();
    }
  }

  async function chat(text) {
    var body = { input: text };
    if (conversationId) body.conversation_id = conversationId;

    var resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    var data = await resp.json();
    if (data.error) throw new Error(data.error);

    if (data.conversation_id) conversationId = data.conversation_id;
    return data.response && data.response.message
      ? data.response.message
      : JSON.stringify(data);
  }

  // --- Voice Recording ---

  function onMicClick() {
    if (state === STATES.IDLE) {
      startRecording();
    } else if (state === STATES.RECORDING) {
      handleVoiceInput();
    } else if (state === STATES.SPEAKING) {
      stopSpeaking();
    }
  }

  async function startRecording() {
    try {
      var stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];

      var mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
      mediaRecorder.addEventListener("dataavailable", function (e) {
        if (e.data.size > 0) audioChunks.push(e.data);
      });

      mediaRecorder.start();
      showStatusIndicator("recording", "Recording...");
      setState(STATES.RECORDING);
    } catch (err) {
      addMessage("system", "Microphone access denied: " + err.message);
    }
  }

  function stopRecording() {
    return new Promise(function (resolve) {
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        resolve(null);
        return;
      }

      mediaRecorder.addEventListener("stop", function () {
        var blob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
        // Release mic
        mediaRecorder.stream.getTracks().forEach(function (t) { t.stop(); });
        mediaRecorder = null;
        audioChunks = [];
        resolve(blob);
      });

      mediaRecorder.stop();
    });
  }

  function cancelRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stream.getTracks().forEach(function (t) { t.stop(); });
      mediaRecorder.stop();
    }
    mediaRecorder = null;
    audioChunks = [];
    removeStatusIndicator();
    setState(STATES.IDLE);
  }

  // --- Voice Pipeline ---

  async function handleVoiceInput() {
    try {
      var audioBlob = await stopRecording();
      if (!audioBlob) {
        setState(STATES.IDLE);
        return;
      }

      showStatusIndicator("thinking", "Transcribing...");
      setState(STATES.TRANSCRIBING);
      var text = await transcribe(audioBlob);

      addMessage("user", text);
      showStatusIndicator("thinking", "Athena is thinking...");
      setState(STATES.THINKING);
      var response = await chat(text);

      removeStatusIndicator();
      addMessage("agent", response);

      if (autoSpeak) {
        showStatusIndicator("speaking", "Speaking...");
        setState(STATES.SPEAKING);
        await speak(response);
        removeStatusIndicator();
      }

      setState(STATES.IDLE);
    } catch (err) {
      removeStatusIndicator();
      addMessage("system", "Error: " + err.message);
      setState(STATES.IDLE);
    }
  }

  async function transcribe(audioBlob) {
    var formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    formData.append("model", "whisper-1");

    var resp = await fetch("/api/transcribe", {
      method: "POST",
      body: formData,
    });

    var data = await resp.json();
    if (data.error) throw new Error(data.error);
    return data.text;
  }

  async function speak(text) {
    var resp = await fetch("/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, voice: selectedVoice }),
    });

    if (!resp.ok) {
      var err = await resp.json().catch(function () { return { error: "TTS failed" }; });
      throw new Error(err.error || "TTS failed");
    }

    var blob = await resp.blob();
    var url = URL.createObjectURL(blob);

    return new Promise(function (resolve, reject) {
      currentAudio = new Audio(url);
      currentAudio.addEventListener("ended", function () {
        URL.revokeObjectURL(url);
        currentAudio = null;
        resolve();
      });
      currentAudio.addEventListener("error", function () {
        URL.revokeObjectURL(url);
        currentAudio = null;
        reject(new Error("Audio playback failed"));
      });
      currentAudio.play();
    });
  }

  function stopSpeaking() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    removeStatusIndicator();
    setState(STATES.IDLE);
  }
})();
