import { useState, useEffect } from 'react';
import { HostAPI } from './api';

export default function IdentityView() {
  const [identities, setIdentities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rotating, setRotating] = useState(null);

  const fetchIdentities = async () => {
    try {
      const res = await HostAPI.listIdentities();
      if (res.success && res.identities) {
        setIdentities(res.identities);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchIdentities();
  }, []);

  const handleRotate = async (did) => {
    if (!confirm("Are you sure you want to rotate this key? The old key will be archived.")) return;
    
    setRotating(did);
    const res = await HostAPI.rotateKey(did);
    if (res.success) {
      alert("Key rotated successfully!");
      fetchIdentities();
    } else {
      alert(`Rotation failed: ${res.error}`);
    }
    setRotating(null);
  };

  if (loading) return <div>Loading Identities...</div>;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ marginBottom: '24px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Identity Fortress</h3>
      
      <p style={{ marginBottom: '24px', color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '800px' }}>
        Manage sovereign identities and cryptographic keys. 
        Keys are derived using Argon2id (GPU-resistant) and stored locally.
      </p>

      <div style={{ display: 'grid', gap: '16px' }}>
        {identities.map((id) => {
          // Trust Color Logic
          const score = id.trust_score || 0;
          let trustColor = '#ef4444'; // Red
          if (score >= 0.8) trustColor = '#10b981'; // Green
          else if (score >= 0.5) trustColor = '#f59e0b'; // Yellow

          return (
            <div key={id.did} style={{ 
              padding: '20px', 
              background: 'rgba(0,0,0,0.2)', 
              border: `1px solid ${id.status === 'QUARANTINED' ? '#ef4444' : 'var(--border-subtle)'}`, 
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Quarantine Overlay */}
              {id.status === 'QUARANTINED' && (
                <div style={{
                  position: 'absolute', top: 0, right: 0, 
                  background: '#ef4444', color: 'white', 
                  fontSize: '10px', padding: '2px 8px', fontWeight: 'bold'
                }}>
                  QUARANTINED
                </div>
              )}

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 600, color: 'var(--accent-primary)' }}>
                    {id.role || 'Unknown Agent'}
                  </span>
                  
                  {/* Trust Stage Badge */}
                  {id.trust_stage && (
                    <span style={{ 
                      fontSize: '10px', padding: '2px 6px', borderRadius: '4px', 
                      background: 'rgba(255,255,255,0.1)', color: 'var(--text-secondary)',
                      border: '1px solid rgba(255,255,255,0.2)'
                    }}>
                      {id.trust_stage}
                    </span>
                  )}

                  {/* Algo Badge */}
                  <span style={{ 
                    fontSize: '10px', padding: '2px 6px', borderRadius: '4px', 
                    background: id.algorithm === 'argon2id' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: id.algorithm === 'argon2id' ? '#10b981' : '#ef4444'
                  }}>
                    {id.algorithm?.toUpperCase()}
                  </span>
                </div>
                
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', opacity: 0.7 }}>
                  {id.did}
                </div>

                {/* Trust Metrics Grid */}
                <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
                  
                  {/* Trust Score Gauge */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Trust Score</div>
                    <div style={{ width: '100px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                      <div style={{ 
                        width: `${score * 100}%`, height: '100%', 
                        background: trustColor, borderRadius: '3px',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                    <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: trustColor }}>
                      {score.toFixed(3)}
                    </div>
                  </div>

                  {/* Influence Weight */}
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    Influence: <span style={{ color: 'var(--text-primary)' }}>{((id.influence_weight || 0) * 100).toFixed(1)}%</span>
                  </div>

                  {/* Experience */}
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    Verifications: <span style={{ color: 'var(--text-primary)' }}>{id.verification_count || 0}</span>
                  </div>

                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                <button 
                  onClick={() => handleRotate(id.did)}
                  disabled={rotating === id.did}
                  className="btn-secondary"
                  style={{ fontSize: '12px', padding: '6px 12px' }}
                >
                  {rotating === id.did ? 'Rotating...' : 'Rotate Key'}
                </button>
                {id.is_local && (
                   <span style={{ fontSize: '10px', color: 'var(--text-secondary)', opacity: 0.5 }}>Local Key</span>
                )}
              </div>
            </div>
          );
        })}
        
        {identities.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            No identities found in keystore.
          </div>
        )}
      </div>
    </div>
  );
}
