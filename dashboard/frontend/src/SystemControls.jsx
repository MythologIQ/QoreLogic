import { useState, useEffect } from 'react';
import { HostAPI, ContainerAPI, ConnectionState } from './api';

/**
 * System Control Panel
 * 
 * Provides lifecycle controls for the QoreLogic system:
 * - Start/Stop container
 * - Connection status indicators
 */
export default function SystemControls({ onStatusChange }) {
  const [hostConnected, setHostConnected] = useState(false);
  const [containerConnected, setContainerConnected] = useState(false);
  const [launching, setLaunching] = useState(false);
  const [stopping, setStopping] = useState(false);

  // Poll connection status
  useEffect(() => {
    const checkStatus = async () => {
      const status = await ConnectionState.checkAll();
      setHostConnected(status.host);
      setContainerConnected(status.container);
      onStatusChange?.(status);
    };

    checkStatus();
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [onStatusChange]);

  const handleStop = async () => {
    if (!confirm('Stop the QoreLogic system?')) return;
    
    setStopping(true);
    const result = await HostAPI.stop();
    
    if (result.success) {
      setContainerConnected(false);
    } else {
      alert(`Error stopping: ${result.error}`);
    }
    setStopping(false);
  };

  const handleStart = async () => {
    setLaunching(true);
    const result = await HostAPI.launch();
    
    if (result.success) {
      // Wait a moment for container to come up
      setTimeout(async () => {
        const status = await ConnectionState.checkAll();
        setContainerConnected(status.container);
        setLaunching(false);
      }, 3000);
    } else {
      alert(`Error starting: ${result.error || 'Control plane may be offline'}`);
      setLaunching(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '16px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          {/* Container Status - Primary Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: containerConnected ? 'var(--success)' : 'var(--warning)',
              boxShadow: `0 0 8px ${containerConnected ? 'var(--success)' : 'var(--warning)'}`
            }} />
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              System {containerConnected ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          {containerConnected ? (
            <button
              onClick={handleStop}
              disabled={stopping || !hostConnected}
              style={{
                padding: '8px 16px',
                background: 'var(--error)',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: stopping ? 'not-allowed' : 'pointer',
                opacity: stopping ? 0.6 : 1,
                fontWeight: 600,
                fontSize: '13px'
              }}
            >
              {stopping ? 'Stopping...' : '⏹ Stop System'}
            </button>
          ) : (
            <button
              onClick={handleStart}
              disabled={launching || !hostConnected}
              style={{
                padding: '8px 16px',
                background: hostConnected ? 'var(--accent-primary)' : 'var(--text-secondary)',
                color: '#000',
                border: 'none',
                borderRadius: '6px',
                cursor: launching || !hostConnected ? 'not-allowed' : 'pointer',
                opacity: launching ? 0.6 : 1,
                fontWeight: 600,
                fontSize: '13px'
              }}
            >
              {launching ? 'Starting...' : '🚀 Start System'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
