import { useState, useEffect } from 'react';
import './index.css';
import AgentsView from './AgentsView';
import SystemControls from './SystemControls';
import { ContainerAPI, HostAPI } from './api';

const API_BASE = "http://localhost:8000/api";

import TrustMonitor from './TrustMonitor';
import IdentityView from './IdentityView';
import LedgerView from './LedgerView';

const Icons = {
  Dashboard: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  List: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>,
  Folder: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  Plus: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  Brain: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.54"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.54"/></svg>,
  Shield: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Activity: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
};

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [status, setStatus] = useState(null);
  const [ledger, setLedger] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState({ host: false, container: false });
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [workspaces, setWorkspaces] = useState({});

  const fetchData = async () => {
    try {
      const [statusRes, ledgerRes, wsRes] = await Promise.all([
        fetch(`${API_BASE}/status${activeWorkspace ? `?ws_id=${activeWorkspace.id}` : ''}`).catch(() => null),
        fetch(`${API_BASE}/ledger?limit=20${activeWorkspace ? `&ws_id=${activeWorkspace.id}` : ''}`).catch(() => null),
        fetch(`${API_BASE}/workspaces`).catch(() => null)
      ]);
      
      if (statusRes && statusRes.ok) setStatus(await statusRes.json());
      if (ledgerRes && ledgerRes.ok) setLedger(await ledgerRes.json());
      
      if (wsRes && wsRes.ok) {
        const wsData = await wsRes.json();
        setWorkspaces(wsData.workspaces || {});
        
        // If we have an active workspace in state, ensure it matches backend, 
        // BUT if backend has 'active' set and we don't, trust backend (initial load)
        // If user explicitly "exits" workspace, we might need to handle that.
        // For now, let's trust the backend's "Active" unless we explicitly unset it.
        if (!activeWorkspace && wsData.active && wsData.workspaces[wsData.active]) {
           setActiveWorkspace(wsData.workspaces[wsData.active]);
        }
      }
    } catch (e) {
      console.error("Fetch error", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [activeWorkspace?.id]);

  const handleSwitchWorkspace = async (id) => {
    const ws = workspaces[id];
    if (!ws) return;
    
    // Show loading state
    setActiveWorkspace({ ...ws, loading: true });
    setActiveTab('overview');
    
    // 1. First activate in the container's registry
    const activateRes = await ContainerAPI.activateWorkspace(id);
    if (!activateRes.success) {
      alert('Failed to activate workspace: ' + activateRes.error);
      setActiveWorkspace(null);
      return;
    }
    
    // 2. Restart Docker with the workspace's path as /src
    // This requires the HostAPI (Control Plane) to be running
    const launchRes = await HostAPI.launch({ path: ws.path, workspace: id });
    if (launchRes.success) {
      // Wait a moment for container to restart, then reload
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    } else {
      // HostAPI isn't available - workspace is activated but mount won't change
      console.warn('HostAPI not available - container not restarted');
      setActiveWorkspace(ws);
    }
  };

  const handleExitWorkspace = async () => {
    await ContainerAPI.deactivateWorkspace();
    setActiveWorkspace(null); // Return to selector
  };

  // --------------------------------------------------------------------------
  // RENDER: WORKSPACE SELECTOR (Global Scope)
  // --------------------------------------------------------------------------
  if (!activeWorkspace) {
    return (
      <div style={{ height: '100vh', width: '100vw', background: 'var(--bg-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
        <div style={{ maxWidth: '900px', width: '100%', padding: '40px' }}>
             
             <div style={{ textAlign: 'center', marginBottom: '60px' }}>
                <h1 style={{ fontSize: '48px', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', color: 'var(--text-primary)' }}>
                  <span style={{ color: 'var(--accent-primary)' }}>⬢</span> QoreLogic
                </h1>
                <p style={{ fontSize: '18px', color: 'var(--text-secondary)' }}>Sovereign Governance Gatekeeper</p>
             </div>

             <h2 style={{ fontSize: '20px', marginBottom: '24px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
               Select Active Workspace
             </h2>

             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '24px' }}>
                
                {/* Existing Workspaces */}
                {Object.values(workspaces).map(ws => (
                  <div 
                    key={ws.id}
                    onClick={() => handleSwitchWorkspace(ws.id)}
                    className="glass-panel"
                    style={{ 
                      padding: '24px', 
                      cursor: 'pointer', 
                      border: '1px solid var(--border-subtle)',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.transform = 'none'; }}
                  >
                     <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <div style={{ fontSize: '32px' }}>📂</div>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                          <div style={{ fontSize: '11px', padding: '4px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', height: 'fit-content' }}>
                            {ws.env_type?.toUpperCase()}
                          </div>
                          <button
                            onClick={async (e) => {
                              e.stopPropagation();
                              if (confirm(`Delete workspace "${ws.name}"? This removes it from the list but does not delete files.`)) {
                                const res = await ContainerAPI.deleteWorkspace(ws.id);
                                if (res.success) {
                                  setWorkspaces(prev => {
                                    const updated = { ...prev };
                                    delete updated[ws.id];
                                    return updated;
                                  });
                                } else {
                                  alert('Failed to delete: ' + res.error);
                                }
                              }
                            }}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '14px',
                              padding: '4px',
                              opacity: 0.5,
                              transition: 'opacity 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.opacity = '1'}
                            onMouseLeave={e => e.currentTarget.style.opacity = '0.5'}
                            title="Remove workspace"
                          >
                            🗑️
                          </button>
                        </div>
                     </div>
                     <h3 style={{ fontSize: '18px', marginBottom: '8px', color: 'var(--text-primary)' }}>{ws.name}</h3>
                     <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{ws.path}</div>
                     <div style={{ marginTop: '24px', fontSize: '12px', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        Open Workspace &rarr;
                     </div>
                  </div>
                ))}

                {/* Create New Card */}
                <div 
                    onClick={() => setActiveTab('new-workspace')} // This is hacky, we need a "mode" state. Let's just create a quick local toggle or render the View if specific key.
                    className="glass-panel"
                    style={{ 
                      padding: '24px', 
                      cursor: 'pointer', 
                      border: '1px dashed var(--text-secondary)',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: '200px',
                      opacity: 0.7,
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.opacity = '1'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--text-secondary)'; e.currentTarget.style.opacity = '0.7'; }}
                  >
                     {activeTab === 'new-workspace' ? (
                        <NewWorkspaceView /> /* In-place rendering logic needs cleaner separation, but for now... */
                     ) : (
                        <>
                           <div style={{ fontSize: '32px', marginBottom: '16px', color: 'var(--accent-primary)' }}>+</div>
                           <div style={{ fontSize: '16px', fontWeight: 600 }}>Create New Workspace</div>
                        </>
                     )}
                  </div>
             </div>
             
             {/* If we clicked create new, we need to show that view. 
                 Actually, simpler: Let's make "NewWorkspaceView" a modal or a separate screen state.
                 For speed: I will just render NewWorkspaceView if activeTab is 'new-workspace' and overlay it.
             */}
             {activeTab === 'new-workspace' && (
               <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
                  <div style={{ position: 'relative' }}>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setActiveTab('overview'); }}
                      style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '24px', cursor: 'pointer', zIndex: 101 }}
                    >
                      &times;
                    </button>
                    <NewWorkspaceView />
                  </div>
               </div>
             )}

        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // RENDER: DASHBOARD (Workspace Scope)
  // --------------------------------------------------------------------------
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <nav style={{ 
        width: '260px', 
        borderRight: '1px solid var(--border-subtle)', 
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 16px'
      }}>
        <div style={{ marginBottom: '32px', paddingLeft: '12px' }}>
          <h2 style={{ fontSize: '20px', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--accent-primary)' }}>
            <span style={{ fontSize: '24px' }}>⬢</span>
            QoreLogic
          </h2>
          <div style={{ 
               marginTop: '12px', 
               padding: '8px 12px', 
               background: 'rgba(255, 215, 0, 0.1)', 
               borderRadius: '6px', 
               border: '1px solid rgba(255, 215, 0, 0.2)'
             }}>
               <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>WORKSPACE</div>
               <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{activeWorkspace.name}</div>
             </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <NavItem icon={<Icons.Dashboard/>} label="Overview" active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} />
          <NavItem icon={<Icons.List/>} label="Ledger Explorer" active={activeTab === 'ledger'} onClick={() => setActiveTab('ledger')} />
          <NavItem icon={<Icons.Activity/>} label="Deep Trust Analysis" active={activeTab === 'trust'} onClick={() => setActiveTab('trust')} />
          <NavItem icon={<Icons.Shield/>} label="Identity Fortress" active={activeTab === 'identity'} onClick={() => setActiveTab('identity')} />
          <NavItem icon={<Icons.Folder/>} label="File Browser" active={activeTab === 'workspace'} onClick={() => setActiveTab('workspace')} />
          <NavItem icon={<Icons.Brain/>} label="Agent Intelligence" active={activeTab === 'agents'} onClick={() => setActiveTab('agents')} />
          <NavItem icon={<Icons.Settings/>} label="Environment" active={activeTab === 'environment'} onClick={() => setActiveTab('environment')} />
        </div>

        <div style={{ marginTop: 'auto' }}>
           <button 
             onClick={handleExitWorkspace}
             style={{
               width: '100%',
               padding: '12px',
               marginBottom: '16px',
               background: 'rgba(255,255,255,0.05)',
               border: '1px solid var(--border-subtle)',
               borderRadius: '6px',
               color: 'var(--text-secondary)',
               cursor: 'pointer',
               display: 'flex',
               alignItems: 'center',
               justifyContent: 'center',
               gap: '8px',
               fontSize: '13px'
             }}
           >
             &larr; Switch Workspace
           </button>

          <div className="glass-panel" style={{ padding: '16px', fontSize: '12px', background: 'rgba(255, 215, 0, 0.03)', borderColor: 'rgba(255, 215, 0, 0.1)' }}>
            <div style={{ color: 'var(--accent-primary)', marginBottom: '8px', fontWeight: 600 }}>SYSTEM STATUS</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: status?.current_mode === 'NORMAL' ? 'var(--success)' : 'var(--warning)', boxShadow: `0 0 10px ${status?.current_mode === 'NORMAL' ? 'var(--success)' : 'var(--warning)'}` }}></div>
              <span style={{ fontWeight: 500 }}>{status?.current_mode || 'OFFLINE'}</span>
            </div>
            <div style={{ color: 'var(--text-secondary)' }}>v2.2.0-beta</div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
        <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '28px', color: 'var(--text-primary)', marginBottom: '8px' }}>
              {activeTab === 'new-workspace' ? 'Initialize Workspace' : 
               activeTab === 'environment' ? 'System Environment' :
               activeTab === 'trust' ? 'Trust Dynamics Engine' :
               activeTab === 'identity' ? 'Identity Fortress' :
               activeTab === 'ledger' ? 'Ledger Explorer' :
               activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
            </h1>
            <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              {activeTab === 'overview' && 'Real-time telemetry and system health.'}
              {activeTab === 'trust' && 'Behavioral economics and reputation metrics.'}
              {activeTab === 'identity' && 'Cryptographic key management (Argon2id).'}
              {activeTab === 'ledger' && 'Immutable audit trail of all agent interactions.'}
              {activeTab === 'workspace' && 'Manage files and security context.'}
              {activeTab === 'agents' && 'Configure LLM backends and agent personas.'}
              {activeTab === 'environment' && 'Configure global QoreLogic variables.'}
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
             <button className="glass-panel" style={{ padding: '8px 16px', color: 'var(--text-secondary)', cursor: 'pointer', transition: 'all 0.2s' }} onClick={fetchData}>
               Refresh
             </button>
          </div>
        </header>

        <SystemControls onStatusChange={setConnectionStatus} />

        {activeTab === 'overview' && <Overview status={status} ledger={ledger} />}
        {activeTab === 'trust' && <TrustMonitor />}
        {activeTab === 'identity' && <IdentityView />}
        {activeTab === 'ledger' && <LedgerView workspaceId={activeWorkspace?.id} />}
        {activeTab === 'workspace' && <WorkspaceView workspaceId={activeWorkspace?.id} workspacePath={activeWorkspace?.path} />}
        {activeTab === 'agents' && <AgentsView />}
        {activeTab === 'environment' && <EnvironmentView />}
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        width: '100%',
        padding: '12px 16px',
        background: active ? 'rgba(255, 215, 0, 0.1)' : 'transparent',
        border: 'none',
        borderRadius: '8px',
        color: active ? 'var(--accent-primary)' : 'var(--text-secondary)',
        cursor: 'pointer',
        textAlign: 'left',
        transition: 'all 0.2s',
        borderLeft: active ? '3px solid var(--accent-primary)' : '3px solid transparent'
      }}
    >
      <div style={{ color: active ? 'var(--accent-primary)' : 'inherit' }}>{icon}</div>
      <span style={{ fontWeight: active ? 600 : 400 }}>{label}</span>
    </button>
  )
}

function Overview({ status, ledger }) {
  if (!status) return <div>Connecting to Telemetry...</div>;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
      <MetricCard 
        label="Total Ledger Entries" 
        value={status.total_ledger_entries?.toLocaleString()} 
        trend="+12 this hour"
        color="var(--accent-primary)"
      />
      <MetricCard 
        label="Pending Approvals" 
        value={status.pending_approvals} 
        trend="Requires Attention"
        color={status.pending_approvals > 0 ? "var(--warning)" : "var(--success)"}
      />
       <MetricCard 
        label="Active Agents" 
        value="4" 
        trend="Judge, Sentinel, Scrivener, Overseer"
        color="var(--text-primary)"
      />
      
      <div className="glass-panel" style={{ gridColumn: '1 / -1', padding: '24px' }}>
        <h3 style={{ marginBottom: '20px', fontSize: '16px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Recent Ledger Activity</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0px' }}>
          {ledger.slice(0, 5).map(entry => (
            <div key={entry.entry_id} style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              padding: '16px 0',
              borderBottom: '1px solid var(--border-subtle)'
            }}>
              <div>
                <div style={{ fontWeight: 500, marginBottom: '6px', color: 'var(--text-primary)' }}>{entry.event_type}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{entry.agent_did}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '12px', padding: '4px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', display: 'inline-block', border: '1px solid var(--border-subtle)' }}>
                  {entry.risk_grade}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  {new Date(entry.timestamp * 1000).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MetricCard({ label, value, trend, color }) {
  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ color: 'var(--text-secondary)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>{label}</div>
      <div style={{ fontSize: '36px', fontWeight: 600, marginBottom: '8px', color: color || 'var(--text-primary)', textShadow: `0 0 20px ${color}40` }}>{value}</div>
      <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{trend}</div>
    </div>
  )
}



function WorkspaceView({ workspaceId, workspacePath }) {
  const [path, setPath] = useState('');
  const [files, setFiles] = useState([]);
  const [wsRoot, setWsRoot] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError('');
    
    let url = `${API_BASE}/files?path=${encodeURIComponent(path)}`;
    if (workspaceId) url += `&ws_id=${workspaceId}`;
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setError(data.error);
          setFiles([]);
        } else {
          setFiles(data.items || []);
          setError('');
        }
        if (data.workspace_root) setWsRoot(data.workspace_root);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch files');
        setLoading(false);
      });
  }, [path, workspaceId]);

  const handleNavigate = (itemName, isDir) => {
    if (isDir) {
      setPath(prev => prev ? `${prev}/${itemName}` : itemName);
    }
  };

  const handleUp = () => {
    if (!path) return;
    const parts = path.split('/');
    parts.pop();
    setPath(parts.join('/'));
  };

  // Display the actual workspace path, not the Docker mount point
  const displayPath = workspacePath || wsRoot || '/src';

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <button onClick={handleUp} disabled={!path} style={{ background: 'none', border: 'none', color: 'var(--text-primary)', cursor: 'pointer', fontSize: '18px' }}>&uarr;</button>
        <div style={{ fontFamily: 'monospace', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.3)', padding: '4px 8px', borderRadius: '4px', overflow: 'hidden', textOverflow: 'ellipsis', flex: 1 }}>{displayPath}{path ? '/' + path : ''}</div>
      </div>
      
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>Loading...</div>
      )}
      
      {error && !loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📁</div>
          <div style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>
            {error === 'Path not found' ? 
              "This workspace's directory is not accessible from the container." :
              error
            }
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
            The workspace may be located outside the mounted Docker volume. 
            Files can only be browsed when the workspace path is inside the Q-DNA project directory.
          </div>
        </div>
      )}
      
      {!loading && !error && files.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📂</div>
          <div>This directory is empty</div>
        </div>
      )}
      
      {!loading && !error && files.length > 0 && (
        <div style={{ display: 'grid', gap: '4px' }}>
        {files.map((item, i) => (
          <div key={i} 
            onClick={() => handleNavigate(item.name, item.is_dir)}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '12px 16px', 
              background: 'rgba(255,255,255,0.02)', 
              borderRadius: '6px',
              cursor: item.is_dir ? 'pointer' : 'default',
              transition: 'background 0.2s',
              border: '1px solid transparent'
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
          >
            <div style={{ color: item.is_dir ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
              {item.is_dir ? <Icons.Folder /> : <Icons.List />}
            </div>
            <span style={{ color: 'var(--text-primary)' }}>{item.name}</span>
            <div style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-secondary)' }}>
               {item.is_dir ? 'DIR' : `${(item.size / 1024).toFixed(1)} KB`}
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  )
}

function EnvironmentView() {
  const [vars, setVars] = useState({
    "QORELOGIC_ENV": "production",
    "QORELOGIC_DB_PATH": "/app/ledger/qorelogic_soa_ledger.db",
    "QORELOGIC_IDENTITY_PASSPHRASE": "********",
    "QORELOGIC_LOG_LEVEL": "INFO",
    "DOCKER_CONTAINER_ID": "a1b2c3d4e5f6"
  });

  return (
    <div className="glass-panel" style={{ padding: '32px', maxWidth: '800px' }}>
      <div style={{ marginBottom: '24px', color: 'var(--text-secondary)' }}>
        These variables define the runtime behavior of the QoreLogic instance. 
        <br/>Warning: Changing these requires a container restart.
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {Object.entries(vars).map(([key, value]) => (
          <div key={key}>
            <label style={{ display: 'block', color: 'var(--accent-primary)', fontSize: '12px', fontWeight: 600, marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>{key}</label>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input 
                type="text" 
                value={value} 
                readOnly
                className="input-field"
                style={{ fontFamily: 'var(--font-mono)' }}
              />
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <button style={{ background: 'transparent', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', padding: '8px 16px', borderRadius: '6px' }}>Discard Changes</button>
        <button className="btn-primary">Save Configuration</button>
      </div>
    </div>
  )
}

function NewWorkspaceView() {
  const [name, setName] = useState('');
  const [path, setPath] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name || !path) return alert("Name and Path are required");
    
    setLoading(true);
    // Register the workspace
    const createRes = await ContainerAPI.createWorkspace({ name, path });
    if (createRes.success) {
      // Activate it
      const activateRes = await ContainerAPI.activateWorkspace(createRes.data.id);
      if (activateRes.success) {
        alert(`Workspace '${name}' initialized and activated!`);
        window.location.reload(); 
      } else {
        alert("Created but failed to activate: " + activateRes.error);
      }
    } else {
      alert("Failed to create workspace: " + createRes.error);
    }
    setLoading(false);
  };

  return (
    <div className="glass-panel" style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{ width: '48px', height: '48px', background: 'var(--accent-primary)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--bg-primary)' }}>
          <Icons.Plus />
        </div>
        <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>Create New Workspace</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Initialize a sterile QoreLogic environment for a new project.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div>
          <label style={{ display: 'block', color: 'var(--text-primary)', fontSize: '14px', fontWeight: 500, marginBottom: '8px' }}>Project Name</label>
          <input 
            type="text" 
            placeholder="e.g., Project Alpha" 
            className="input-field"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>

        <div>
          <label style={{ display: 'block', color: 'var(--text-primary)', fontSize: '14px', fontWeight: 500, marginBottom: '8px' }}>Workspace Root</label>
          <input 
            type="text" 
            placeholder="e.g., G:\Projects\MyApp or /home/user/projects/myapp" 
            className="input-field" 
            value={path}
            onChange={e => setPath(e.target.value)}
          />
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Enter the absolute path to your project directory.
          </div>
        </div>

        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)', cursor: 'pointer' }}>
            <input type="checkbox" style={{ width: '16px', height: '16px' }} defaultChecked />
            <span>Initialize Git Repository</span>
          </label>
        </div>

        <button 
          className="btn-primary" 
          style={{ marginTop: '16px', padding: '12px', opacity: loading ? 0.7 : 1 }}
          onClick={handleCreate}
          disabled={loading}
        >
          {loading ? 'Initializing...' : 'Initialize Workspace'}
        </button>
      </div>
    </div>
  )
}

export default App;
