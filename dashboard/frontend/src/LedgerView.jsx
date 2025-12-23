import { useState, useEffect } from 'react';
import { ContainerAPI } from './api';

export default function LedgerView({ workspaceId }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const fetchLedger = async () => {
    setLoading(true);
    // Use ContainerAPI to get workspace-scoped history
    const res = await ContainerAPI.ledger(100, workspaceId);
    if (res.success && Array.isArray(res.data)) {
      setEvents(res.data);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchLedger();
  }, [workspaceId]);

  const filteredEvents = events.filter(e => 
    e.event_type?.toLowerCase().includes(filter.toLowerCase()) ||
    e.agent_did?.toLowerCase().includes(filter.toLowerCase()) ||
    e.payload?.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <input 
          type="text" 
          placeholder="Filter ledger events..." 
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="input-field"
          style={{ width: '300px' }}
        />
        <button className="btn-secondary" onClick={fetchLedger}>
          Refresh Ledger
        </button>
      </div>

      {/* Table Container */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead style={{ position: 'sticky', top: 0, background: 'var(--bg-secondary)', zIndex: 10 }}>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-subtle)' }}>
              <th style={thStyle}>Event</th>
              <th style={thStyle}>Agent</th>
              <th style={thStyle}>Risk</th>
              <th style={thStyle}>Workspace</th>
              <th style={thStyle}>Time</th>
              <th style={thStyle}>Hash</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" style={{ padding: '40px', textAlign: 'center' }}>Loading Ledger...</td></tr>
            ) : (
                filteredEvents.map(entry => {
                // Certainty Logic (Progressive Formalization)
                // Mapping old "Risk" fields to certainties if needed, or using direct certainty if available
                let certainty = 'L0';
                if (entry.risk_grade === 'L1') certainty = 'L1'; 
                if (entry.risk_grade === 'L2') certainty = 'L2';
                if (entry.risk_grade === 'L3') certainty = 'L3';
                
                // Visuals for Certainty Levels
                const levelRaw = parseInt(certainty.replace('L', '')) || 0;
                let certColor = '#9ca3af'; // L0 Gray
                if (levelRaw >= 1) certColor = '#3b82f6'; // L1 Blue
                if (levelRaw >= 2) certColor = '#f59e0b'; // L2 Amber
                if (levelRaw >= 3) certColor = '#10b981'; // L3 Green
                if (levelRaw >= 4) certColor = '#8b5cf6'; // L4 Purple
                if (levelRaw >= 5) certColor = '#ec4899'; // L5 Pink

                // Event Type Logic
                const isFail = entry.event_type?.includes('FAIL');
                const isPass = entry.event_type?.includes('PASS');
                const isL3 = entry.event_type?.includes('L3');
                
                let icon = '•';
                if (isPass) icon = '✓';
                if (isFail) icon = '✕';
                if (isL3) icon = '⚖️';

                // Parse Payload for Summary
                let summary = "";
                try {
                  const pl = JSON.parse(entry.payload);
                  if (pl.verdict) summary += `Verdict: ${pl.verdict} `;
                  if (pl.failure_modes?.length) summary += `| FM: ${pl.failure_modes.join(', ')} `;
                  if (pl.reason) summary += `| ${pl.reason} `;
                } catch (e) {}

                return (
                  <tr key={entry.entry_hash} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px 16px', color: 'var(--text-primary)' }}>
                      <span style={{ 
                        marginRight: '8px', 
                        color: isFail ? '#ef4444' : isPass ? '#10b981' : 'var(--text-secondary)',
                        fontWeight: 'bold'
                      }}>
                        {icon}
                      </span>
                      {entry.event_type}
                    </td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>
                      {entry.agent_did?.split(':')[2] || 'System'}
                      <div style={{ fontSize: '10px', opacity: 0.6 }}>{entry.agent_did}</div>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                       <span style={{ 
                          padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold',
                          background: `${certColor}20`, color: certColor, border: `1px solid ${certColor}40`
                       }}>
                         LEVEL {levelRaw}
                       </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>
                      {entry.workspace_id || 'default'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ color: 'var(--text-secondary)' }}>{new Date(entry.timestamp * 1000).toLocaleString()}</div>
                      {summary && (
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', opacity: 0.8, maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {summary}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {entry.entry_hash?.substring(0, 8)}...
                    </td>
                  </tr>
                );
            })
          )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle = {
  padding: '12px 16px',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  fontSize: '12px',
  textTransform: 'uppercase'
};
