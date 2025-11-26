import { useEffect, useState, useRef } from "react";
import GeminiAIController from "./GeminiAIController";

// ===============================
// API URL
// ===============================
const API_BASE = "http://192.168.137.1:5000/api";
const SENSOR_DATA_URL = `${API_BASE}/data/latest`;
const ACTUATOR_STATUS_URL = `${API_BASE}/actuator/status`;
const PUMP_CONTROL_URL = `${API_BASE}/pump/control`;
const AI_STATUS_URL = `${API_BASE}/ai/status`;

// ===============================
// GEMINI API KEY
// ===============================
const GEMINI_API_KEY = "AIzaSyAeefoAQX3A6RdjHfj9rYTwvCWdB5UryPA"; // ← ISI DENGAN API KEY GEMINI ANDA

function App() {
  const [sensor, setSensor] = useState(null);
  const [pumpStatus, setPumpStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Voice Assistant
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);

  // AI Controller
  const [aiControllerRunning, setAiControllerRunning] = useState(false);
  const [aiStats, setAiStats] = useState(null);
  const aiControllerRef = useRef(null);
  const recognitionRef = useRef(null);

  // ===============================
  // FETCH SENSOR DATA
  // ===============================
  const fetchSensorData = async () => {
    try {
      const res = await fetch(SENSOR_DATA_URL);
      const data = await res.json();
      setSensor(data);
    } catch (err) {
      console.error("[SENSOR-DATA] Error:", err);
    }
  };

  // ===============================
  // FETCH ACTUATOR STATUS
  // ===============================
  const fetchActuatorStatus = async () => {
    try {
      const res = await fetch(ACTUATOR_STATUS_URL);
      const data = await res.json();
      setPumpStatus(data.pump || "OFF");
    } catch (err) {
      console.error("[ACTUATOR-STATUS] Error:", err);
    }
  };

  // ===============================
  // AI CONTROLLER FUNCTIONS
  // ===============================
  const initializeAIController = () => {
    try {
      if (!aiControllerRef.current) {
        aiControllerRef.current = new GeminiAIController(GEMINI_API_KEY, API_BASE);
        console.log("[UI] AI Controller initialized");
      }
      return aiControllerRef.current;
    } catch (error) {
      console.error("[UI] Failed to init AI:", error);
      alert("❌ Gagal inisialisasi AI: " + error.message);
      return null;
    }
  };

  const startAIAutomation = async () => {
    try {
      const controller = initializeAIController();
      if (!controller) return;

      setAiControllerRunning(true);
      console.log("[UI] Starting AI Automation...");

      // Run in background
      controller.start().catch((error) => {
        console.error("[UI] AI error:", error);
        setAiControllerRunning(false);
      });
    } catch (error) {
      console.error("[UI] Start failed:", error);
      setAiControllerRunning(false);
    }
  };

  const stopAIAutomation = () => {
    if (aiControllerRef.current) {
      aiControllerRef.current.stop();
      setAiControllerRunning(false);
      console.log("[UI] AI Automation stopped");
    }
  };

  const refreshAIStats = () => {
    if (aiControllerRef.current) {
      const stats = aiControllerRef.current.getStatus();
      setAiStats(stats);
      console.log("[UI] AI Stats:", stats);
    }
  };

  const changeAIPollInterval = (ms) => {
    if (aiControllerRef.current) {
      aiControllerRef.current.setPollInterval(ms);
      console.log(`[UI] Poll interval changed to ${ms}ms`);
    }
  };

  // ===============================
  // CONTROL PUMP
  // ===============================
  const controlPump = async (state) => {
    try {
      const res = await fetch(PUMP_CONTROL_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pump: state }),
      });

      const data = await res.json();
      console.log("[PUMP-CONTROL]", data);
      setPumpStatus(state);
      return true;

    } catch (err) {
      console.error("[PUMP-CONTROL] Error:", err);
      return false;
    }
  };

  // ===============================
  // GEMINI AI PROCESSING
  // ===============================
  const processWithGemini = async (userText) => {
    try {
      setAiResponse("🤔 Memproses...");

      if (!GEMINI_API_KEY) {
        setAiResponse("❌ API Key Gemini belum diisi!");
        speak("API Key Gemini belum diisi");
        return;
      }

      const prompt = `
Kamu adalah AI assistant untuk sistem greenhouse.

Data sensor:
- Temperature: ${sensor?.temperature_c ?? "?"} °C
- Humidity: ${sensor?.humidity_pct ?? "?"} %
- Soil Moisture: ${sensor?.soil_moisture ?? "?"} %
- Light: ${sensor?.light_lux ?? "?"}
- pH: ${sensor?.ph ?? "?"}
- Pump: ${pumpStatus}

User berkata: "${userText}"

Berikan jawaban dalam format JSON:
{
  "action": "pump_on" | "pump_off" | "get_info" | "none",
  "response": "jawaban singkat bahasa Indonesia"
}
`;

      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
          }),
        }
      );

      const data = await response.json();
      console.log("[GEMINI] Raw Response:", data);

      // =========================================
      // CEK RESPONSE VALID
      // =========================================
      const aiText =
        data?.candidates?.[0]?.content?.parts?.[0]?.text || "";

      if (!aiText) {
        setAiResponse("❌ Tidak ada respons dari AI");
        speak("Maaf, AI tidak merespon");
        return;
      }

      // Ambil JSON dari teks
      const match = aiText.match(/\{[\s\S]*\}/);
      if (!match) {
        setAiResponse("❌ Format AI tidak valid");
        speak("Format AI tidak valid");
        return;
      }

      let parsed;
      try {
        parsed = JSON.parse(match[0]);
      } catch (e) {
        setAiResponse("❌ JSON tidak bisa diparse");
        speak("Tidak bisa memproses JSON AI");
        return;
      }

      // =========================================
      // ACTION EXECUTION
      // =========================================
      if (parsed.action === "pump_on") {
        await controlPump("ON");
      }
      if (parsed.action === "pump_off") {
        await controlPump("OFF");
      }

      setAiResponse(parsed.response);
      speak(parsed.response);

    } catch (err) {
      console.error("[GEMINI ERROR]:", err);
      setAiResponse("❌ Terjadi error pada AI");
      speak("Maaf, terjadi kesalahan pada sistem AI");
    }
  };

  // ===============================
  // SPEECH SYNTHESIS
  // ===============================
  const speak = (text) => {
    if (!window.speechSynthesis) return;
    setIsSpeaking(true);

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "id-ID";
    utter.rate = 1;
    utter.onend = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utter);
  };

  // ===============================
  // SPEECH RECOGNITION
  // ===============================
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Browser tidak mendukung Speech Recognition");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "id-ID";
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript("🎤 Mendengarkan...");
      setAiResponse("");
    };

    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      setTranscript(text);
      processWithGemini(text);
    };

    recognition.onerror = (err) => {
      console.error("Speech Error:", err);
      setTranscript("❌ Error: " + err.error);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  // ===============================
  // AUTO REFRESH 3 DETIK
  // ===============================
  useEffect(() => {
    const load = async () => {
      await fetchSensorData();
      await fetchActuatorStatus();
      setLoading(false);
    };

    load();
    const interval = setInterval(load, 3000);
    
    return () => {
      clearInterval(interval);
      // Cleanup AI controller
      if (aiControllerRef.current) {
        aiControllerRef.current.stop();
      }
    };
  }, []);

  // ===============================
  // UI LOADING
  // ===============================
  if (loading) {
    return (
      <div className="p-10 text-center text-xl">Loading dashboard...</div>
    );
  }

  // ===============================
  // UI
  // ===============================
  return (
    <div className="min-h-screen p-6 bg-green-100">
      <h1 className="text-4xl mb-4 font-bold text-center">
        🏡 Smart Greenhouse
      </h1>

      {/* VOICE */}
      <div className="bg-white p-6 rounded-xl shadow-md mb-6 text-center">
        <h2 className="text-2xl font-bold mb-4">🎙️ Voice Assistant</h2>

        <button
          onClick={isListening ? stopListening : startListening}
          disabled={isSpeaking}
          className="px-6 py-4 rounded-full bg-green-500 text-white text-3xl shadow-lg"
        >
          {isListening ? "🔴" : "🎤"}
        </button>

        <p className="mt-4">{transcript}</p>
        <p className="mt-2 font-semibold">{aiResponse}</p>
      </div>

      {/* AI AUTOMATION */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-xl shadow-md mb-6 text-white">
        <h2 className="text-2xl font-bold mb-4">🤖 AI Automation Control</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Status */}
          <div className="bg-white bg-opacity-20 p-4 rounded-lg">
            <p className="text-lg font-semibold">Status:</p>
            <p className={`text-2xl font-bold ${aiControllerRunning ? 'text-green-300' : 'text-red-300'}`}>
              {aiControllerRunning ? '🟢 RUNNING' : '🔴 STOPPED'}
            </p>
            <p className="text-sm mt-2">
              Poll Interval: {aiControllerRef.current?.getPollInterval() || 'N/A'}ms
            </p>
          </div>

          {/* Controls */}
          <div className="flex flex-col gap-2">
            <button
              onClick={startAIAutomation}
              disabled={aiControllerRunning}
              className="px-4 py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-500 text-white rounded-lg font-bold transition"
            >
              ▶️ Start AI
            </button>
            <button
              onClick={stopAIAutomation}
              disabled={!aiControllerRunning}
              className="px-4 py-3 bg-red-500 hover:bg-red-600 disabled:bg-gray-500 text-white rounded-lg font-bold transition"
            >
              ⏹️ Stop AI
            </button>
            <button
              onClick={refreshAIStats}
              className="px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-bold transition"
            >
              📊 Refresh Stats
            </button>
          </div>
        </div>

        {/* Poll Interval Controls */}
        <div className="mt-4 bg-white bg-opacity-20 p-4 rounded-lg">
          <p className="text-lg font-semibold mb-2">Poll Interval (ms):</p>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => changeAIPollInterval(5000)}
              className="px-3 py-2 bg-white bg-opacity-30 hover:bg-opacity-50 rounded text-sm"
            >
              5s
            </button>
            <button
              onClick={() => changeAIPollInterval(10000)}
              className="px-3 py-2 bg-white bg-opacity-30 hover:bg-opacity-50 rounded text-sm"
            >
              10s (default)
            </button>
            <button
              onClick={() => changeAIPollInterval(15000)}
              className="px-3 py-2 bg-white bg-opacity-30 hover:bg-opacity-50 rounded text-sm"
            >
              15s
            </button>
            <button
              onClick={() => changeAIPollInterval(30000)}
              className="px-3 py-2 bg-white bg-opacity-30 hover:bg-opacity-50 rounded text-sm"
            >
              30s
            </button>
          </div>
        </div>

        {/* Statistics */}
        {aiStats && (
          <div className="mt-4 bg-white bg-opacity-20 p-4 rounded-lg">
            <p className="text-lg font-semibold mb-2">📈 Statistics:</p>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <p>Total Decisions: <b>{aiStats.stats.total_decisions}</b></p>
              <p>Success Rate: <b>{aiStats.stats.success_rate}</b></p>
              <p>Pump Actions: <b>{aiStats.stats.pump_actions}</b></p>
              <p>Servo Actions: <b>{aiStats.stats.servo_actions}</b></p>
            </div>
            {aiStats.stats.last_decision && (
              <div className="mt-2 text-xs bg-black bg-opacity-30 p-2 rounded max-h-24 overflow-y-auto">
                <p className="font-mono">Last Decision:</p>
                <p className="font-mono">{aiStats.stats.last_decision.decision.reason}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* SENSOR DATA */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 bg-white rounded-lg shadow">
          🌡️ Temperature: <b>{sensor.temperature_c}°C</b>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          💧 Humidity: <b>{sensor.humidity_pct}%</b>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          🌱 Soil: <b>{sensor.soil_moisture}%</b>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          ☀️ Light: <b>{sensor.light_lux}</b>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          ⚗️ pH: <b>{sensor.ph}</b>
        </div>
      </div>

      {/* MANUAL CONTROL */}
      <div className="bg-white p-6 mt-6 rounded-xl shadow-md">
        <h2 className="text-xl font-bold mb-4">Manual Pump Control</h2>

        <p>Status: {pumpStatus}</p>

        <button
          onClick={() => controlPump(pumpStatus === "ON" ? "OFF" : "ON")}
          className="mt-3 px-6 py-3 bg-blue-600 text-white rounded-lg"
        >
          {pumpStatus === "ON" ? "Turn OFF" : "Turn ON"}
        </button>
      </div>
    </div>
  );
}

export default App;
