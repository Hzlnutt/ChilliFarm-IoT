/**
 * AI Controller untuk IoT Chili Garden
 * Menggunakan Gemini API untuk membuat keputusan automasi
 * 
 * Integration: Frontend React App
 * Usage: Import dan gunakan GeminiAIController class
 */

class GeminiAIController {
  constructor(apiKey, backendUrl = 'http://192.168.137.1:5000/api') {
    this.apiKey = apiKey;
    this.backendUrl = backendUrl;
    this.isRunning = false;
    this.pollInterval = 10000; // 10 detik
    this.lastStatus = null;
    this.decisionLog = [];
    this.maxLogSize = 100;
    
    // Validation
    if (!apiKey) {
      throw new Error('[GEMINI-AI] API Key tidak ditemukan');
    }
    
    console.log('[GEMINI-AI] Controller initialized');
  }

  /**
   * Mulai monitoring dan automasi
   */
  async start() {
    if (this.isRunning) {
      console.warn('[GEMINI-AI] Already running');
      return;
    }
    
    this.isRunning = true;
    console.log('[GEMINI-AI] Starting...');
    
    // Polling loop
    while (this.isRunning) {
      try {
        // 1. Fetch current status
        const status = await this.getSystemStatus();
        this.lastStatus = status;
        
        // 2. Make AI decision
        const decision = await this.makeDecision(status);
        
        // 3. Execute command
        if (decision) {
          const result = await this.executeCommand(decision);
          this.addLog(decision, result);
        }
        
        // Wait before next poll
        await this.sleep(this.pollInterval);
      } catch (error) {
        console.error('[GEMINI-AI] Error in polling loop:', error);
        await this.sleep(this.pollInterval);
      }
    }
  }

  /**
   * Stop monitoring
   */
  stop() {
    this.isRunning = false;
    console.log('[GEMINI-AI] Stopped');
  }

  /**
   * Fetch status dari backend
   */
  async getSystemStatus() {
    try {
      const response = await fetch(`${this.backendUrl}/ai/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log('[STATUS] Retrieved:', data);
      return data;
    } catch (error) {
      console.error('[STATUS] Fetch failed:', error);
      throw error;
    }
  }

  /**
   * Buat keputusan menggunakan Gemini API
   */
  async makeDecision(status) {
    try {
      // Build context untuk Gemini
      const context = this.buildContext(status);
      
      // Call Gemini API
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: context
              }]
            }],
            generationConfig: {
              temperature: 0.5,
              topK: 40,
              topP: 0.95,
              maxOutputTokens: 1024,
            }
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Gemini API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Parse response
      if (!data.candidates || !data.candidates[0]) {
        console.warn('[GEMINI] No candidates in response');
        return null;
      }

      const textContent = data.candidates[0].content.parts[0].text;
      console.log('[GEMINI] Raw response:', textContent);
      
      // Extract JSON dari response
      const jsonMatch = textContent.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        console.warn('[GEMINI] No JSON found in response');
        return null;
      }

      const decision = JSON.parse(jsonMatch[0]);
      console.log('[DECISION] AI Decision:', decision);
      
      return this.validateDecision(decision);
    } catch (error) {
      console.error('[GEMINI] API call failed:', error);
      throw error;
    }
  }

  /**
   * Validasi keputusan sebelum eksekusi
   */
  validateDecision(decision) {
    const required = ['action', 'command'];
    const missing = required.filter(field => !decision[field]);
    
    if (missing.length > 0) {
      console.error('[VALIDATE] Missing fields:', missing);
      return null;
    }
    
    // Validate action
    if (!['pump', 'servo'].includes(decision.action)) {
      console.error('[VALIDATE] Invalid action:', decision.action);
      return null;
    }
    
    // Validate command based on action
    if (decision.action === 'pump') {
      if (!['on', 'off'].includes(decision.command)) {
        console.error('[VALIDATE] Invalid pump command:', decision.command);
        return null;
      }
    } else if (decision.action === 'servo') {
      if (!['open', 'close', 'angle'].includes(decision.command)) {
        console.error('[VALIDATE] Invalid servo command:', decision.command);
        return null;
      }
      
      if (decision.command === 'angle') {
        if (!decision.value || decision.value < 0 || decision.value > 180) {
          console.error('[VALIDATE] Invalid servo angle:', decision.value);
          return null;
        }
      }
    }
    
    return decision;
  }

  /**
   * Execute command via backend API
   */
  async executeCommand(decision) {
    try {
      const payload = {
        action: decision.action,
        command: decision.command,
        reason: decision.reason || 'AI-generated decision',
        auto_triggered: true
      };

      // Add value untuk servo angle
      if (decision.value !== undefined) {
        payload.value = decision.value;
      }

      const response = await fetch(`${this.backendUrl}/ai/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('[EXECUTE] Result:', result);
      
      return result;
    } catch (error) {
      console.error('[EXECUTE] Command execution failed:', error);
      throw error;
    }
  }

  /**
   * Build context untuk Gemini AI
   */
  buildContext(status) {
    const sensors = status.sensors;
    const actuators = status.actuators;
    
    return `You are an AI assistant controlling an automated Chili Garden greenhouse system.

CURRENT SYSTEM STATUS:
${JSON.stringify({
  temperature: `${sensors.temperature.value}°C (${sensors.temperature.status})`,
  humidity: `${sensors.humidity.value}% (${sensors.humidity.status})`,
  soil_moisture: `${sensors.soil_moisture.value}% (${sensors.soil_moisture.status})`,
  light: `${sensors.light.value} lux (${sensors.light.status})`,
  ph: `${sensors.ph.value} (${sensors.ph.status})`,
  pump_state: actuators.pump.state,
  servo_angle: actuators.servo.angle
}, null, 2)}

SYSTEM RECOMMENDATIONS:
${status.recommendations.map(r => `- ${r}`).join('\n')}

CONTROL RULES:
1. Pump Control:
   - Turn ON when soil_moisture < 40% AND pump is OFF
   - Turn OFF when soil_moisture > 70% OR pump runtime > 60s
   - Never turn ON if it's already ON (avoid spam)

2. Servo Control (Lid):
   - Open (90°) when temperature > 30°C for cooling
   - Close (0°) when temperature < 20°C to retain heat
   - Use partial angle (30-60°) for ventilation without extreme changes
   - Keep current state if conditions are optimal

3. Safety Rules:
   - Make ONE decision per cycle
   - Only change state if necessary
   - Avoid rapid toggling of same device

DECISION FORMAT:
Respond with ONLY a JSON object (no explanation):
{
  "action": "pump|servo",
  "command": "on|off|open|close|angle",
  "value": optional_number_for_angle,
  "reason": "short explanation why this decision was made"
}

If no action is needed, respond with:
{
  "action": "none",
  "reason": "all conditions optimal"
}

Make the decision now based on current system status.`;
  }

  /**
   * Log keputusan untuk audit
   */
  addLog(decision, result) {
    const entry = {
      timestamp: new Date().toISOString(),
      decision,
      result,
      status: result.status
    };
    
    this.decisionLog.push(entry);
    
    // Keep only last N entries
    if (this.decisionLog.length > this.maxLogSize) {
      this.decisionLog.shift();
    }
    
    console.log(`[LOG] Decision #${this.decisionLog.length}:`, entry);
  }

  /**
   * Get decision log
   */
  getLog() {
    return this.decisionLog;
  }

  /**
   * Get summary statistics
   */
  getStats() {
    const total = this.decisionLog.length;
    const successful = this.decisionLog.filter(e => e.status === 'success').length;
    const failed = this.decisionLog.filter(e => e.status === 'failed').length;
    
    const pumpActions = this.decisionLog.filter(e => e.decision.action === 'pump');
    const servoActions = this.decisionLog.filter(e => e.decision.action === 'servo');
    
    return {
      total_decisions: total,
      successful: successful,
      failed: failed,
      success_rate: total > 0 ? ((successful / total) * 100).toFixed(2) + '%' : 'N/A',
      pump_actions: pumpActions.length,
      servo_actions: servoActions.length,
      last_decision: this.decisionLog[this.decisionLog.length - 1],
      last_status: this.lastStatus
    };
  }

  /**
   * Helper: Sleep
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Set poll interval (milliseconds)
   */
  setPollInterval(ms) {
    this.pollInterval = ms;
    console.log(`[GEMINI-AI] Poll interval set to ${ms}ms`);
  }

  /**
   * Get current poll interval
   */
  getPollInterval() {
    return this.pollInterval;
  }

  /**
   * Get running status
   */
  getStatus() {
    return {
      running: this.isRunning,
      pollInterval: this.pollInterval,
      lastStatus: this.lastStatus,
      stats: this.getStats()
    };
  }
}

// ============================================================================
// USAGE EXAMPLE (untuk React Frontend)
// ============================================================================

/**
 * Contoh implementasi di React App:
 * 
 * import GeminiAIController from './GeminiAIController';
 * 
 * function App() {
 *   const [aiStatus, setAiStatus] = useState(null);
 *   const aiControllerRef = useRef(null);
 * 
 *   useEffect(() => {
 *     // Initialize AI Controller
 *     const controller = new GeminiAIController(GEMINI_API_KEY);
 *     aiControllerRef.current = controller;
 * 
 *     return () => {
 *       if (aiControllerRef.current) {
 *         aiControllerRef.current.stop();
 *       }
 *     };
 *   }, []);
 * 
 *   const startAI = async () => {
 *     try {
 *       await aiControllerRef.current.start();
 *     } catch (error) {
 *       console.error('Failed to start AI:', error);
 *     }
 *   };
 * 
 *   const stopAI = () => {
 *     aiControllerRef.current.stop();
 *   };
 * 
 *   const getAIStatus = () => {
 *     setAiStatus(aiControllerRef.current.getStatus());
 *   };
 * 
 *   return (
 *     <div>
 *       <button onClick={startAI}>Start AI</button>
 *       <button onClick={stopAI}>Stop AI</button>
 *       <button onClick={getAIStatus}>Refresh Status</button>
 *       {aiStatus && <pre>{JSON.stringify(aiStatus, null, 2)}</pre>}
 *     </div>
 *   );
 * }
 */

export default GeminiAIController;
