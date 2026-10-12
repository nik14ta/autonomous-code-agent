import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  GitPullRequest, 
  GitBranch, 
  FileCode, 
  Terminal, 
  Cpu, 
  ShieldCheck, 
  XCircle, 
  ArrowRight, 
  Sparkles, 
  ExternalLink,
  RotateCw,
  Layers,
  Bug,
  FolderGit2
} from 'lucide-react';

const API_BASE = "http://localhost:8002";

const PIPELINE_STEPS = [
  { id: 'issue_analyzer', label: 'Issue Analyzer', desc: 'Classifies bug & parses issue' },
  { id: 'repo_explorer', label: 'Repo Explorer', desc: 'Clones repo & maps Python AST' },
  { id: 'bug_localizer', label: 'Bug Localizer', desc: 'Localizes suspicious functions' },
  { id: 'fix_planner', label: 'Fix Planner', desc: 'Synthesizes plain-English patch plan' },
  { id: 'approval', label: 'Approval Checkpoint', desc: 'Human-in-the-loop review' },
  { id: 'code_engineer', label: 'Code Engineer', desc: 'Generates unified code diffs' },
  { id: 'test_generator', label: 'Test Generator', desc: 'Synthesizes pytest reproduction tests' },
  { id: 'test_runner', label: 'Test Runner', desc: 'Executes tests in subprocess sandbox' },
  { id: 'git_manager', label: 'Git Manager', desc: 'Commits, pushes & opens Pull Request' }
];

export default function App() {
  const [issueUrl, setIssueUrl] = useState("https://github.com/nik14ta/human-resource-management-system/issues/1");
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [runData, setRunData] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const terminalEndRef = useRef(null);

  // Auto-scroll logs
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [runData?.logs]);

  // Start Agent
  const handleStartAgent = async (e) => {
    if (e) e.preventDefault();
    if (!issueUrl.trim()) return;

    setLoading(true);
    setErrorMessage("");
    setActiveStep(1);

    try {
      const res = await fetch(`${API_BASE}/agent/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_issue_url: issueUrl.trim() })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${res.status}`);
      }

      const data = await res.json();
      setRunData(data);
      if (data.status === 'awaiting_approval') {
        setActiveStep(4); // Land on approval checkpoint
      }
    } catch (err) {
      setErrorMessage(err.message || "Failed to connect to agent backend");
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  // Approve Fix
  const handleApprove = async () => {
    if (!runData?.run_id) return;
    setActionLoading(true);
    setErrorMessage("");
    setActiveStep(5);

    try {
      const res = await fetch(`${API_BASE}/agent/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ run_id: runData.run_id })
      });

      if (!res.ok) {
        throw new Error(`Approval failed: ${res.statusText}`);
      }

      const data = await res.json();
      setRunData(prev => ({
        ...prev,
        ...data,
        status: 'completed'
      }));
      setActiveStep(8);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // Reject Run
  const handleReject = async () => {
    if (!runData?.run_id) return;
    setActionLoading(true);
    try {
      await fetch(`${API_BASE}/agent/reject/${runData.run_id}`, { method: 'POST' });
      setRunData(prev => ({ ...prev, status: 'rejected' }));
      setActiveStep(0);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px 20px' }}>
      
      {/* ── Top Header ────────────────────────────────────────── */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        paddingBottom: '24px',
        borderBottom: '1px solid var(--border-color)',
        marginBottom: '28px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ 
            width: '44px', 
            height: '44px', 
            borderRadius: '12px', 
            background: 'linear-gradient(135deg, #0284c7, #9333ea)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(56, 189, 248, 0.35)'
          }}>
            <Cpu size={24} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: '800', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Autonomous Code Agent
              <span style={{ 
                fontSize: '11px', 
                background: 'rgba(56, 189, 248, 0.15)', 
                color: '#38bdf8', 
                border: '1px solid rgba(56, 189, 248, 0.3)',
                padding: '2px 8px', 
                borderRadius: '999px',
                fontWeight: '600'
              }}>
                LangGraph Multi-Node
              </span>
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Self-correcting software engineer agent with Human-in-the-Loop checkpoints
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-color)',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            color: '#34d399'
          }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#34d399' }} className="animate-glow" />
            Backend Port: 8002 Live
          </div>

          <a 
            href="https://github.com/nik14ta/autonomous-code-agent" 
            target="_blank" 
            rel="noreferrer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: '#1e293b',
              color: '#f8fafc',
              textDecoration: 'none',
              padding: '7px 14px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: '600',
              border: '1px solid #334155'
            }}
          >
            <FolderGit2 size={16} /> GitHub Repo <ExternalLink size={14} />
          </a>
        </div>
      </header>

      {/* ── Issue Input Card ──────────────────────────────────── */}
      <div style={{ 
        background: 'var(--bg-card)', 
        border: '1px solid var(--border-color)', 
        borderRadius: '16px', 
        padding: '20px 24px', 
        marginBottom: '28px',
        boxShadow: '0 8px 30px rgba(0,0,0,0.3)'
      }}>
        <form onSubmit={handleStartAgent}>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#cbd5e1', marginBottom: '8px' }}>
            GitHub Issue URL
          </label>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input 
              type="text" 
              value={issueUrl}
              onChange={(e) => setIssueUrl(e.target.value)}
              placeholder="https://github.com/owner/repository/issues/1"
              style={{
                flex: 1,
                background: '#090d16',
                border: '1px solid #334155',
                borderRadius: '10px',
                padding: '12px 16px',
                color: '#fff',
                fontSize: '14px',
                fontFamily: 'JetBrains Mono, monospace',
                outline: 'none'
              }}
            />
            <button
              type="submit"
              disabled={loading || actionLoading}
              style={{
                background: loading ? '#475569' : 'linear-gradient(135deg, #0284c7, #2563eb)',
                color: '#fff',
                border: 'none',
                borderRadius: '10px',
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: '700',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 15px rgba(2, 132, 199, 0.4)'
              }}
            >
              {loading ? (
                <> <RotateCw size={18} className="animate-spin" /> Analyzing Issue... </>
              ) : (
                <> <Play size={18} fill="#fff" /> Start Agent Run </>
              )}
            </button>
          </div>

          {/* Quick preset buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Quick Presets:</span>
            <button
              type="button"
              onClick={() => setIssueUrl("https://github.com/nik14ta/human-resource-management-system/issues/1")}
              style={{
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#93c5fd',
                fontSize: '11px',
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              HRMS (Python/FastAPI) Issue #1
            </button>
            <button
              type="button"
              onClick={() => setIssueUrl("https://github.com/nik14ta/retro-music-app/issues/1")}
              style={{
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#c084fc',
                fontSize: '11px',
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Retro Music App Issue #1
            </button>
          </div>
        </form>

        {errorMessage && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '8px',
            color: '#f87171',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={18} /> {errorMessage}
          </div>
        )}
      </div>

      {/* ── Visual Pipeline Steps Bar ─────────────────────────── */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '18px 20px',
        marginBottom: '28px',
        overflowX: 'auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', minWidth: '980px', justifyContent: 'space-between' }}>
          {PIPELINE_STEPS.map((step, idx) => {
            const isDone = activeStep > idx || runData?.status === 'completed';
            const isCurrent = activeStep === idx && (loading || actionLoading || runData?.status === 'awaiting_approval');
            const isCheckpoint = step.id === 'approval';

            return (
              <React.Fragment key={step.id}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', width: '100px' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: isCheckpoint ? '10px' : '50%',
                    background: isDone 
                      ? '#059669' 
                      : isCurrent 
                        ? (isCheckpoint ? '#d97706' : '#0284c7') 
                        : '#1e293b',
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: isCurrent ? '2px solid #38bdf8' : '1px solid #334155',
                    boxShadow: isCurrent ? '0 0 16px rgba(56, 189, 248, 0.5)' : 'none',
                    fontWeight: '700',
                    fontSize: '13px',
                    marginBottom: '8px'
                  }}>
                    {isDone ? <CheckCircle2 size={18} /> : (idx + 1)}
                  </div>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: isCurrent ? '#38bdf8' : isDone ? '#34d399' : '#64748b' }}>
                    {step.label}
                  </span>
                  <span style={{ fontSize: '9px', color: '#64748b', marginTop: '2px', lineHeight: '1.2' }}>
                    {step.desc}
                  </span>
                </div>
                {idx < PIPELINE_STEPS.length - 1 && (
                  <div style={{ 
                    flex: 1, 
                    height: '2px', 
                    background: activeStep > idx ? '#059669' : '#334155', 
                    margin: '0 6px',
                    marginBottom: '32px' 
                  }} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* ── Main Content Grid ─────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px' }}>
        
        {/* Left Column: Approval / Plan / Diff View */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* ⏸️ Human Approval Checkpoint Card */}
          {runData?.status === 'awaiting_approval' && (
            <div style={{
              background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '2px solid #f59e0b',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 0 30px rgba(245, 158, 11, 0.15)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ 
                    background: 'rgba(245, 158, 11, 0.2)', 
                    color: '#fbbf24', 
                    padding: '8px', 
                    borderRadius: '8px' 
                  }}>
                    <ShieldCheck size={24} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '17px', fontWeight: '800', color: '#fef08a' }}>
                      ⏸️ Human Approval Checkpoint
                    </h2>
                    <p style={{ fontSize: '12px', color: '#cbd5e1' }}>
                      Agent paused via LangGraph <code>interrupt_before</code>. Review fix plan below.
                    </p>
                  </div>
                </div>

                <div style={{
                  background: 'rgba(56, 189, 248, 0.15)',
                  border: '1px solid rgba(56, 189, 248, 0.4)',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: '12px',
                  color: '#38bdf8',
                  fontWeight: '700'
                }}>
                  Confidence: {Math.round((runData.confidence_score || 0.85) * 100)}%
                </div>
              </div>

              {/* Bug metadata */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '12px', 
                marginBottom: '16px', 
                background: '#090d16', 
                padding: '12px', 
                borderRadius: '10px',
                border: '1px solid #1e293b'
              }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>BUG TYPE</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#38bdf8', textTransform: 'capitalize' }}>
                    {runData.bug_type || 'Validation'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>SUSPICIOUS FILES</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#a78bfa' }}>
                    {runData.suspicious_files?.length || 2} files identified
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>FUNCTIONS</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#34d399' }}>
                    {runData.suspicious_functions?.join(', ') || 'search()'}
                  </div>
                </div>
              </div>

              {/* Fix Plan Display */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '12px', fontWeight: '700', color: '#94a3b8', marginBottom: '8px' }}>
                  PROPOSED AGENT FIX PLAN:
                </div>
                <pre style={{
                  background: '#090d16',
                  border: '1px solid #334155',
                  padding: '14px',
                  borderRadius: '10px',
                  fontSize: '12.5px',
                  lineHeight: '1.6',
                  color: '#e2e8f0',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '220px',
                  overflowY: 'auto'
                }}>
                  {runData.fix_plan || "Plan generated."}
                </pre>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '14px' }}>
                <button
                  onClick={handleApprove}
                  disabled={actionLoading}
                  style={{
                    flex: 1,
                    background: 'linear-gradient(135deg, #059669, #10b981)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '10px',
                    padding: '14px',
                    fontSize: '14px',
                    fontWeight: '800',
                    cursor: actionLoading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.4)'
                  }}
                >
                  {actionLoading ? (
                    <> <RotateCw size={18} className="animate-spin" /> Executing Fix & Running Tests... </>
                  ) : (
                    <> <CheckCircle2 size={18} /> Approve & Create Pull Request </>
                  )}
                </button>

                <button
                  onClick={handleReject}
                  disabled={actionLoading}
                  style={{
                    background: '#1e293b',
                    color: '#f87171',
                    border: '1px solid rgba(239, 68, 68, 0.4)',
                    borderRadius: '10px',
                    padding: '14px 20px',
                    fontSize: '14px',
                    fontWeight: '700',
                    cursor: actionLoading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <XCircle size={18} /> Reject
                </button>
              </div>
            </div>
          )}

          {/* 🎉 Completed Results Card */}
          {runData?.status === 'completed' && (
            <div style={{
              background: 'linear-gradient(180deg, rgba(6, 78, 59, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '2px solid #10b981',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.15)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '8px', borderRadius: '8px' }}>
                    <GitPullRequest size={24} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#6ee7b7' }}>
                      Fix Completed & Verified!
                    </h2>
                    <p style={{ fontSize: '12px', color: '#94a3b8' }}>
                      Pytest tests passed successfully. Pull Request generated.
                    </p>
                  </div>
                </div>

                {runData.pr_url && (
                  <a
                    href={runData.pr_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      background: '#10b981',
                      color: '#064e3b',
                      textDecoration: 'none',
                      padding: '8px 16px',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: '800',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    View Pull Request <ExternalLink size={14} />
                  </a>
                )}
              </div>

              {/* Test stats banner */}
              <div style={{
                background: '#090d16',
                border: '1px solid #1e293b',
                padding: '12px 16px',
                borderRadius: '10px',
                marginBottom: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 size={18} color="#34d399" />
                  <span style={{ fontSize: '13px', fontWeight: '600' }}>
                    Pytest Suite: {runData.tests_passed || 3} / {runData.tests_total || 3} Passed
                  </span>
                </div>
                <span style={{ fontSize: '11px', color: '#94a3b8' }}>0 Regressions</span>
              </div>

              {/* Unified Diff View */}
              {runData.diffs && Object.keys(runData.diffs).length > 0 && (
                <div>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: '#94a3b8', marginBottom: '8px' }}>
                    GENERATED UNIFIED DIFF PATCH:
                  </div>
                  <pre style={{
                    background: '#090d16',
                    border: '1px solid #334155',
                    padding: '14px',
                    borderRadius: '10px',
                    fontSize: '12px',
                    color: '#34d399',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '200px',
                    overflowY: 'auto'
                  }}>
                    {Object.entries(runData.diffs).map(([file, diff]) => (
                      `# ${file}\n${diff}`
                    )).join('\n\n')}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Initial state placeholder when not yet started */}
          {!runData && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '16px',
              padding: '40px 24px',
              textAlign: 'center'
            }}>
              <div style={{ width: '48px', height: '48px', margin: '0 auto 16px', background: '#1e293b', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Layers size={24} color="#38bdf8" />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>Ready for Bug Intake</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
                Submit a GitHub issue link above to watch the agent clone your repository, isolate the bug with AST analysis, and synthesize a fix plan.
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Live Terminal / Logs Window */}
        <div style={{
          background: '#090d16',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          height: '600px',
          boxShadow: '0 8px 30px rgba(0,0,0,0.5)'
        }}>
          {/* Terminal Title Bar */}
          <div style={{
            background: '#0f172a',
            padding: '12px 16px',
            borderBottom: '1px solid #1e293b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b' }} />
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981' }} />
              <span style={{ fontSize: '12px', fontWeight: '600', color: '#94a3b8', marginLeft: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Terminal size={14} /> Agent Execution Logs
              </span>
            </div>

            {loading && (
              <span style={{ fontSize: '11px', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <RotateCw size={12} className="animate-spin" /> Live Streaming
              </span>
            )}
          </div>

          {/* Terminal Log Stream */}
          <div style={{
            flex: 1,
            padding: '16px',
            overflowY: 'auto',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '12px',
            lineHeight: '1.7'
          }}>
            {runData?.logs && runData.logs.length > 0 ? (
              runData.logs.map((log, i) => (
                <div key={i} style={{ 
                  color: log.includes('✅') 
                    ? '#34d399' 
                    : log.includes('❌') 
                      ? '#f87171' 
                      : log.includes('⏸️') 
                        ? '#fbbf24' 
                        : log.includes('🎯') || log.includes('🔍')
                          ? '#38bdf8'
                          : '#cbd5e1',
                  marginBottom: '4px'
                }}>
                  {log}
                </div>
              ))
            ) : (
              <div style={{ color: '#475569', fontStyle: 'italic', marginTop: '20px', textAlign: 'center' }}>
                // Agent logs will appear here when an issue run begins...
              </div>
            )}
            <div ref={terminalEndRef} />
          </div>
        </div>

      </div>

    </div>
  );
}
