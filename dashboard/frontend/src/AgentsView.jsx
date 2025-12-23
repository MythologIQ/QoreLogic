import { useState, useEffect } from 'react';
import { HostAPI, ContainerAPI } from './api';

/**
 * Agent Configuration Panel
 * 
 * Allows configuration of:
 * - LLM Backend (Ollama, OpenAI, Anthropic)
 * - Per-agent model assignment (Sentinel, Judge, Overseer, Scrivener)
 * - System prompts for each agent
 * - Formal Verification Protocol (PyVeritas)
 * 
 * Configuration is persisted to host filesystem via Launcher API (5500)
 */
export default function AgentsView() {
  // Global Ollama endpoint for local discovery
  const [ollamaEndpoint, setOllamaEndpoint] = useState('http://localhost:11434');
  
  // Default prompts for each agent role
  const defaultPrompts = {
    sentinel: `You are SENTINEL, the Security Analysis Engine for QoreLogic.

ROLE: Perform static security analysis on code artifacts. You are the first line of defense.

RESPONSIBILITIES:
- Detect hardcoded secrets, API keys, and credentials
- Identify unsafe function calls (eval, exec, os.system, etc.)
- Flag SQL injection, XSS, and command injection vulnerabilities
- Calculate cyclomatic complexity and flag high-risk functions
- Identify PII exposure risks

OUTPUT FORMAT:
- Return a JSON object with: { "verdict": "PASS|FAIL|WARN", "findings": [...], "risk_grade": "L1|L2|L3" }
- Be concise and actionable. No false positives.

CONSTRAINTS:
- Fast-fail on critical issues (secrets, injection)
- Escalate uncertainty to higher risk grades
- Never approve without evidence`,

    judge: `You are JUDGE, the Compliance Arbiter for QoreLogic.

ROLE: Make final verdicts on code submissions. You review SENTINEL's findings and apply governance policies.

RESPONSIBILITIES:
- Validate SENTINEL's security findings
- Apply the Lewicki-Bunker trust model (CBT → KBT → IBT)
- Enforce citation depth rules (max 2 degrees of separation)
- Verify quote context (±2 sentences or 200 chars)
- Calculate trust score impacts

OUTPUT FORMAT:
- Return: { "verdict": "APPROVED|REJECTED|ESCALATE", "rationale": "...", "trust_delta": ±N }
- Provide clear, auditable reasoning

CONSTRAINTS:
- L3 artifacts ALWAYS require human oversight
- Trust is earned incrementally, lost immediately
- Apply the principle of minimal authority`,

    overseer: `You are OVERSEER, the Strategic Coordinator for QoreLogic.

ROLE: Manage multi-agent workflows and maintain system coherence. You see the big picture.

RESPONSIBILITIES:
- Coordinate task delegation between agents
- Monitor agent trust scores and flag anomalies
- Enforce operational modes (LEAN/SURGE/SAFE)
- Maintain context windows and prevent bloat
- Trigger human escalation when uncertainty is high

OUTPUT FORMAT:
- Return: { "action": "DELEGATE|ESCALATE|COMPLETE", "target": "agent_name", "context": {...} }
- Include confidence scores for all decisions

CONSTRAINTS:
- Never bypass SENTINEL or JUDGE
- Preserve audit trail integrity
- Prioritize human alignment over efficiency`,

    scrivener: `You are SCRIVENER, the Documentation Engine for QoreLogic.

ROLE: Generate, validate, and maintain technical documentation with precision.

RESPONSIBILITIES:
- Write clear, accurate code documentation
- Generate API references and usage examples
- Maintain changelog and migration guides
- Cross-reference citations and validate sources
- Detect echo/paraphrase content (>60% similarity)

OUTPUT FORMAT:
- Return well-structured Markdown
- Include code examples with proper syntax highlighting
- Add metadata: { "sources": [...], "confidence": 0.0-1.0 }

CONSTRAINTS:
- Never fabricate citations or sources
- Flag low-confidence content explicitly
- Maintain consistent terminology`
  };
  
  // Per-agent configuration
  // mode: 'local' (Ollama) or 'api' (external API like xAI GLM)
  const [agentConfigs, setAgentConfigs] = useState({
    sentinel: { mode: 'local', model: 'default', apiEndpoint: '', apiModel: '', prompt: defaultPrompts.sentinel },
    judge: { mode: 'local', model: 'default', apiEndpoint: '', apiModel: '', prompt: defaultPrompts.judge },
    overseer: { mode: 'local', model: 'default', apiEndpoint: '', apiModel: '', prompt: defaultPrompts.overseer },
    scrivener: { mode: 'local', model: 'default', apiEndpoint: '', apiModel: '', prompt: defaultPrompts.scrivener }
  });
  
  // Discovery state
  const [availableModels, setAvailableModels] = useState([]);
  const [modelsDiscovered, setModelsDiscovered] = useState(false);
  const [discoveryStatus, setDiscoveryStatus] = useState(''); // '', 'scanning', 'success', 'failed'
  
  const [saving, setSaving] = useState(false);
  const [hostConnected, setHostConnected] = useState(false);
  
  // Phase 9: Verification Config
  const [verificationMode, setVerificationMode] = useState('lite');

  // Check host connectivity and auto-discover models on mount
  useEffect(() => {
    HostAPI.health().then(res => {
      setHostConnected(res.success && !res.offline);
    });
    
    // Load Verification Config
    HostAPI.verificationConfig().then(res => {
        if (res && res.success && res.config) {
            setVerificationMode(res.config.mode);
        }
    });
    
    // Auto-discover local models on mount
    discoverLocalModels();
  }, []);

  // Discover local Ollama models
  const discoverLocalModels = async () => {
    setDiscoveryStatus('scanning');
    try {
      const res = await fetch(`${ollamaEndpoint}/api/tags`);
      if (!res.ok) throw new Error('Connection failed');
      
      const data = await res.json();
      const modelList = data.models?.map(m => m.name) || [];
      setAvailableModels(modelList);
      setModelsDiscovered(true);
      setDiscoveryStatus('success');
    } catch (e) {
      setDiscoveryStatus('failed');
      setModelsDiscovered(false);
      setAvailableModels([]);
    }
  };

  // Helper to update a single agent's config
  const updateAgentConfig = (agentKey, field, value) => {
    setAgentConfigs(prev => ({
      ...prev,
      [agentKey]: { ...prev[agentKey], [field]: value }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    
    // Build per-agent config with resolved endpoint/model
    const agents = {};
    Object.entries(agentConfigs).forEach(([agentKey, cfg]) => {
      if (cfg.mode === 'local') {
        agents[agentKey] = {
          provider: 'ollama',
          endpoint: ollamaEndpoint,
          model: cfg.model,
          prompt: cfg.prompt
        };
      } else {
        agents[agentKey] = {
          provider: 'api',
          endpoint: cfg.apiEndpoint,
          model: cfg.apiModel,
          prompt: cfg.prompt
        };
      }
    });
    
    const config = {
      ollamaEndpoint,
      verificationMode,
      agentConfigs,
      // Resolved config for backend consumption
      agents
    };
    
    // Always save to localStorage (works offline)
    localStorage.setItem('qorelogic_agent_config', JSON.stringify(config));
    
    // Save to Container API (persists to ~/.qorelogic/config/agents.json)
    const containerResult = await ContainerAPI.saveAgentConfig(config);
    
    // Also sync to HostAPI if available (for backward compat)
    if (hostConnected) {
      await HostAPI.saveAgentConfig(config);
      await HostAPI.verificationConfig({ mode: verificationMode });
    }
    
    if (containerResult.success) {
      alert('✅ Agent configuration saved!');
    } else {
      alert('Configuration saved locally (container sync failed).');
    }
    setSaving(false);
  };

  // Load config: try ContainerAPI first, then localStorage
  useEffect(() => {
    const loadConfig = async () => {
      const applyConfig = (config) => {
        if (config.ollamaEndpoint) setOllamaEndpoint(config.ollamaEndpoint);
        if (config.verificationMode) setVerificationMode(config.verificationMode);
        if (config.agentConfigs) setAgentConfigs(config.agentConfigs);
      };
      
      // Try to load from Container API first (persistent storage)
      const result = await ContainerAPI.getAgentConfig();
      if (result.success && result.data?.config) {
        applyConfig(result.data.config);
        return;
      }
      
      // Fallback to localStorage
      const savedConfig = localStorage.getItem('qorelogic_agent_config');
      if (savedConfig) {
        try {
          applyConfig(JSON.parse(savedConfig));
        } catch (e) {
          console.warn('Failed to load agent config from localStorage');
        }
      }
    };
    loadConfig();
  }, []);

  const agents = [
    { key: 'sentinel', name: 'Sentinel', icon: '🛡️', role: 'Security Auditor' },
    { key: 'judge', name: 'Judge', icon: '⚖️', role: 'Compliance Verifier' },
    { key: 'overseer', name: 'Overseer', icon: '👁️', role: 'Context Manager' },
    { key: 'scrivener', name: 'Scrivener', icon: '📝', role: 'Documentation Engine' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '900px' }}>
      
      {/* Formal Verification Settings (New Phase 9) */}
      <div className="glass-panel" style={{ padding: '24px', borderLeft: '3px solid var(--accent-primary)' }}>
        <h3 style={{ marginBottom: '8px', color: 'var(--text-primary)' }}>Formal Verification Protocol</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
            Configure PyVeritas verification intensity. 
            Full mode requires GPU resources for LLM transpilation.
        </p>
        
        <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.2)', padding: '4px', borderRadius: '8px', width: 'fit-content' }}>
            {['disabled', 'lite', 'full'].map(mode => (
                <button
                    key={mode}
                    onClick={() => setVerificationMode(mode)}
                    style={{
                        padding: '8px 24px',
                        borderRadius: '6px',
                        border: 'none',
                        background: verificationMode === mode ? 'var(--accent-primary)' : 'transparent',
                        color: verificationMode === mode ? 'var(--bg-primary)' : 'var(--text-secondary)',
                        fontWeight: verificationMode === mode ? 600 : 400,
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                        transition: 'all 0.2s'
                    }}
                >
                    {mode}
                </button>
            ))}
        </div>
        
        <div style={{ marginTop: '16px', fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
            {verificationMode === 'disabled' && "Verification disabled. Not recommended for production."}
            {verificationMode === 'lite' && "Pattern-based heuristic scanning (CPU-friendly). Catches 60-70% of issues."}
            {verificationMode === 'full' && "LLM Transpilation + CBMC Bounded Model Checking. High accuracy, higher latency."}
        </div>
      </div>

      {/* Local Model Discovery */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ marginBottom: '8px', color: 'var(--text-primary)' }}>Local Model Discovery</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Connect to your local Ollama instance to discover available models.
        </p>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input 
            type="text"
            value={ollamaEndpoint}
            onChange={e => setOllamaEndpoint(e.target.value)}
            className="input-field"
            style={{ flex: 1, fontFamily: 'var(--font-mono)' }}
            placeholder="http://localhost:11434"
          />
          <button 
            onClick={discoverLocalModels}
            disabled={discoveryStatus === 'scanning'}
            style={{
              ...secondaryButtonStyle,
              minWidth: '140px'
            }}
          >
            {discoveryStatus === 'scanning' ? '⏳ Scanning...' : '🔍 Discover Models'}
          </button>
        </div>
        
        {/* Discovery Status Indicator */}
        <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          {discoveryStatus === 'success' && (
            <>
              <span style={{ color: 'var(--success)', fontSize: '14px' }}>✅</span>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Found {availableModels.length} models: {availableModels.slice(0, 3).join(', ')}{availableModels.length > 3 ? '...' : ''}
              </span>
            </>
          )}
          {discoveryStatus === 'failed' && (
            <>
              <span style={{ color: 'var(--error)', fontSize: '14px' }}>❌</span>
              <span style={{ fontSize: '12px', color: 'var(--error)' }}>
                Connection failed. Is Ollama running at {ollamaEndpoint}?
              </span>
            </>
          )}
          {discoveryStatus === '' && (
            <>
              <span style={{ color: 'var(--warning)', fontSize: '14px' }}>⚠️</span>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Models not discovered. Click "Discover Models" to scan.
              </span>
            </>
          )}
        </div>
      </div>

      {/* Agent Configurations */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ marginBottom: '8px', color: 'var(--text-primary)' }}>Agent Assignment & Directives</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
          Configure each agent with Local (Ollama) or API (external) backend. Toggle to switch modes.
        </p>

        {agents.map((agent, index) => {
          const config = agentConfigs[agent.key];
          const isApi = config.mode === 'api';
          
          return (
            <div 
              key={agent.key}
              style={{ 
                borderBottom: index < agents.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                paddingBottom: index < agents.length - 1 ? '20px' : 0,
                marginBottom: index < agents.length - 1 ? '20px' : 0
              }}
            >
              {/* Header Row: Name + Toggle */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <label style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
                  {agent.icon} {agent.name} <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>({agent.role})</span>
                </label>
                
                {/* Local/API Toggle Switch */}
                <div style={{ 
                  display: 'flex', 
                  background: 'rgba(0,0,0,0.3)', 
                  borderRadius: '6px', 
                  padding: '2px',
                  gap: '2px'
                }}>
                  <button
                    onClick={() => updateAgentConfig(agent.key, 'mode', 'local')}
                    style={{
                      padding: '6px 16px',
                      border: 'none',
                      borderRadius: '4px',
                      background: !isApi ? 'var(--accent-primary)' : 'transparent',
                      color: !isApi ? 'var(--bg-primary)' : 'var(--text-secondary)',
                      fontWeight: !isApi ? 600 : 400,
                      cursor: 'pointer',
                      fontSize: '12px',
                      transition: 'all 0.2s'
                    }}
                  >
                    🏠 Local
                  </button>
                  <button
                    onClick={() => updateAgentConfig(agent.key, 'mode', 'api')}
                    style={{
                      padding: '6px 16px',
                      border: 'none',
                      borderRadius: '4px',
                      background: isApi ? 'var(--accent-primary)' : 'transparent',
                      color: isApi ? 'var(--bg-primary)' : 'var(--text-secondary)',
                      fontWeight: isApi ? 600 : 400,
                      cursor: 'pointer',
                      fontSize: '12px',
                      transition: 'all 0.2s'
                    }}
                  >
                    🌐 API
                  </button>
                </div>
              </div>
              
              {/* Model Selection Row */}
              <div style={{ marginBottom: '8px' }}>
                {isApi ? (
                  /* API Mode: Endpoint + Model text inputs */
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      placeholder="API Endpoint (e.g., https://api.x.ai/v1)"
                      value={config.apiEndpoint}
                      onChange={e => updateAgentConfig(agent.key, 'apiEndpoint', e.target.value)}
                      className="input-field"
                      style={{ flex: 1, fontFamily: 'var(--font-mono)', fontSize: '12px' }}
                    />
                    <input
                      type="text"
                      placeholder="Model (e.g., glm-4.6)"
                      value={config.apiModel}
                      onChange={e => updateAgentConfig(agent.key, 'apiModel', e.target.value)}
                      className="input-field"
                      style={{ width: '150px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
                    />
                  </div>
                ) : (
                  /* Local Mode: Model dropdown */
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <select 
                      value={config.model}
                      onChange={e => updateAgentConfig(agent.key, 'model', e.target.value)}
                      className="input-field"
                      style={{ width: '250px' }}
                      disabled={!modelsDiscovered}
                    >
                      <option value="default">Default (System)</option>
                      {availableModels.map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                    {!modelsDiscovered && (
                      <span style={{ fontSize: '12px', color: 'var(--warning)' }}>
                        ⚠️ Discover models above
                      </span>
                    )}
                  </div>
                )}
              </div>
              
              {/* Prompt Textarea */}
              <textarea
                value={config.prompt}
                onChange={e => updateAgentConfig(agent.key, 'prompt', e.target.value)}
                rows={2}
                style={textareaStyle}
                placeholder={`System prompt for ${agent.name}...`}
              />
            </div>
          );
        })}

        <button 
          onClick={handleSave}
          disabled={saving}
          className="btn-primary"
          style={{ marginTop: '24px', width: '100%' }}
        >
          {saving ? 'Saving...' : 'Save Agent Configuration'}
        </button>
      </div>
    </div>
  );
}

// Styles
const labelStyle = {
  display: 'block',
  marginBottom: '8px',
  color: 'var(--text-secondary)',
  fontSize: '14px'
};

const secondaryButtonStyle = {
  padding: '8px 16px',
  fontSize: '12px',
  background: 'rgba(255,255,255,0.05)',
  border: '1px solid var(--border-subtle)',
  borderRadius: '6px',
  color: 'var(--text-primary)',
  cursor: 'pointer'
};

const textareaStyle = {
  width: '100%',
  marginTop: '8px',
  background: 'rgba(0,0,0,0.3)',
  color: 'var(--text-secondary)',
  border: '1px solid var(--border-subtle)',
  padding: '12px',
  borderRadius: '6px',
  fontFamily: 'var(--font-mono)',
  fontSize: '12px',
  resize: 'vertical'
};
