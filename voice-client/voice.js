// Athena Voice Client
// State machine, text chat, voice recording, Whisper STT, OpenAI TTS
(function () {
  "use strict";

  // --- Markdown config ---
  if (typeof marked !== "undefined") {
    marked.setOptions({ breaks: true, gfm: true });
  }

  function renderMarkdown(text) {
    if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
      return DOMPurify.sanitize(marked.parse(text));
    }
    // Fallback: escape HTML and preserve newlines
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, "<br>");
  }

  function timeStamp() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  // --- State Machine ---
  var STATES = { IDLE: "IDLE", RECORDING: "RECORDING", TRANSCRIBING: "TRANSCRIBING", THINKING: "THINKING", SPEAKING: "SPEAKING" };
  var state = STATES.IDLE;
  var isVoiceMode = false;
  var conversationId = null;
  var mediaRecorder = null;
  var audioChunks = [];
  var currentAudio = null;

  // --- Settings ---
  var selectedVoice = localStorage.getItem("athena-voice") || "nova";
  var autoSpeak = localStorage.getItem("athena-auto-speak") !== "false";

  // --- DOM References ---
  var $messages, $textInput, $sendBtn, $micBtn, $voiceStatus;
  var $textContainer, $voiceContainer, $modeToggle, $modeIconMic, $modeIconText;
  var $settingsToggle, $settingsPanel, $voiceSelect, $autoSpeak;
  var $settingsBackdrop, $settingsClose, $micBtnWrapper;

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
    $settingsBackdrop = document.getElementById("settings-backdrop");
    $settingsClose = document.getElementById("settings-close");
    $micBtnWrapper = document.getElementById("mic-btn-wrapper");

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
    $settingsClose.addEventListener("click", toggleSettings);
    $settingsBackdrop.addEventListener("click", toggleSettings);
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
        // Close settings if open
        if (!$settingsPanel.classList.contains("hidden")) {
          toggleSettings();
          return;
        }
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
    $micBtnWrapper.classList.toggle("recording", state === STATES.RECORDING);
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
    // Remove welcome screen on first message
    var welcome = $messages.querySelector(".welcome");
    if (welcome) welcome.remove();

    if (role === "agent") {
      // Wrap in message-row with avatar
      var row = document.createElement("div");
      row.className = "message-row";

      var avatar = document.createElement("img");
      avatar.src = "athena-logo.jpg";
      avatar.alt = "Athena";
      avatar.className = "agent-avatar";
      row.appendChild(avatar);

      var bubble = document.createElement("div");
      bubble.className = "message agent";
      bubble.innerHTML = renderMarkdown(text);

      var time = document.createElement("div");
      time.className = "msg-time";
      time.textContent = timeStamp();
      bubble.appendChild(time);

      row.appendChild(bubble);
      $messages.appendChild(row);
    } else {
      var el = document.createElement("div");
      el.className = "message " + role;
      if (role === "user") {
        // Plain text for user messages
        var span = document.createElement("span");
        span.textContent = text;
        el.appendChild(span);
        var time2 = document.createElement("div");
        time2.className = "msg-time";
        time2.textContent = timeStamp();
        el.appendChild(time2);
      } else {
        el.textContent = text;
      }
      $messages.appendChild(el);
    }

    scrollToBottom();
  }

  function addWelcome() {
    var el = document.createElement("div");
    el.className = "welcome";

    var hints = [
      "What did I write about last week?",
      "Summarize my project notes",
      "What tasks are due today?",
    ];

    var hintsHTML = '<div class="welcome-hints">';
    for (var i = 0; i < hints.length; i++) {
      hintsHTML += '<button class="hint-chip" data-hint="' + hints[i] + '">' + hints[i] + '</button>';
    }
    hintsHTML += '</div>';

    el.innerHTML =
      '<img src="athena-logo.jpg" alt="Athena" class="welcome-logo">' +
      '<h2>Welcome to Athena</h2>' +
      '<p>Ask about your notes, manage tasks, or explore your second brain.</p>' +
      hintsHTML;

    $messages.appendChild(el);

    // Bind hint chip clicks
    var chips = el.querySelectorAll(".hint-chip");
    for (var j = 0; j < chips.length; j++) {
      chips[j].addEventListener("click", function () {
        var text = this.getAttribute("data-hint");
        $textInput.value = text;
        onSend();
      });
    }
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
    var isOpen = !$settingsPanel.classList.contains("hidden");
    if (isOpen) {
      $settingsPanel.classList.add("hidden");
      $settingsBackdrop.classList.add("hidden");
      $settingsToggle.classList.remove("active");
    } else {
      $settingsPanel.classList.remove("hidden");
      $settingsBackdrop.classList.remove("hidden");
      $settingsToggle.classList.add("active");
    }
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
