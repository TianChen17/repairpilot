import {
  Activity,
  ArrowRight,
  Check,
  CircleStop,
  Database,
  ExternalLink,
  FileCode2,
  GitPullRequest,
  Network,
  Play,
  RefreshCcw,
  ShieldAlert,
  Sparkles,
  UserCheck,
} from 'lucide-react';
import {useCallback, useEffect, useMemo, useState} from 'react';

type Event = {sequence: number; state: string; message: string; timestamp: string};
type Evidence = {source: string; tool: string; summary: string};
type Incident = {
  run_id: string;
  mode: 'live' | 'replay';
  state: string;
  context?: {
    owners: string[];
    tags: string[];
    domain?: string;
    downstream_assets: string[];
    downstream_dashboards: string[];
    queries: string[];
    assertions: string[];
    evidence: Evidence[];
  };
  risk?: {
    score: number;
    level: string;
    action: string;
    matched_rules: string[];
    rationale: string;
  };
  repair?: {
    root_cause: string;
    summary: string;
    operations: {operation: string; target: string; rationale: string}[];
    migration_note: string;
    pr_title: string;
    confidence: number;
  };
  validation?: {
    breaking_change_reproduced: boolean;
    repair_verified: boolean;
    invocation_id: string;
    tests_passed: number;
    tests_failed: number;
    patch_sha256: string;
    base_commit: string;
    repair_commit: string;
    command_results: {command: string; return_code: number; duration_ms: number; stdout_tail: string}[];
  };
  writeback?: {
    incident_document_urn: string;
    runbook_document_urn: string;
    assertion_urns: string[];
  };
  approval?: {
    decision: 'approve' | 'reject';
    actor: string;
    decided_at: string;
  };
  pull_request_url?: string;
  events: Event[];
  error?: string;
};

const terminalStates = new Set([
  'LEARNED',
  'REJECTED',
  'CONTEXT_UNAVAILABLE',
  'VALIDATION_FAILED',
  'MANUAL_REVIEW',
]);

const datahubUrl = import.meta.env.VITE_DATAHUB_URL || 'https://catalog.145-241-207-154.sslip.io';
const stgOrdersUrn = 'urn:li:dataset:(urn:li:dataPlatform:dbt,repairpilot.analytics_staging.stg_orders,PROD)';
const stgOrdersUrl = `${datahubUrl}/dataset/${stgOrdersUrn}`;

const progressByState: Record<string, {step: string; remaining: string}> = {
  DETECTED: {step: '1/6 · Detecting change', remaining: '~32s remaining'},
  CONTEXT_COLLECTED: {step: '2/6 · Reading DataHub', remaining: '~27s remaining'},
  POLICY_EVALUATED: {step: '3/6 · Applying policy', remaining: '~23s remaining'},
  BLOCKED: {step: '3/6 · Release blocked', remaining: '~20s remaining'},
  REPAIR_PROPOSED: {step: '4/6 · Generating bounded repair', remaining: '~15s remaining'},
  VALIDATING: {step: '5/6 · Running dbt build', remaining: '~8s remaining'},
  VERIFIED: {step: '5/6 · Proof recorded', remaining: 'Approval next'},
  AWAITING_APPROVAL: {step: '6/6 · Owner decision required', remaining: 'Ready now'},
  APPROVED: {step: '6/6 · Publishing evidence', remaining: '~3s remaining'},
  PUBLISHED: {step: '6/6 · Writing back to DataHub', remaining: '~2s remaining'},
  LEARNED: {step: 'Complete · Knowledge retained', remaining: 'Inspect evidence'},
};

function App() {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('Ready for a controlled live run');
  const [showDataHubGuide, setShowDataHubGuide] = useState(false);

  const refresh = useCallback(async (runId: string) => {
    const response = await fetch(`/api/v1/incidents/${runId}`);
    if (!response.ok) throw new Error('Could not refresh incident');
    const record = (await response.json()) as Incident;
    setIncident(record);
    return record;
  }, []);

  useEffect(() => {
    if (!incident || terminalStates.has(incident.state) || incident.state === 'AWAITING_APPROVAL') return;
    const timer = window.setInterval(() => refresh(incident.run_id).catch(() => undefined), 700);
    return () => window.clearInterval(timer);
  }, [incident, refresh]);

  useEffect(() => {
    if (!incident) return;
    const messages: Record<string, string> = {
      DETECTED: 'Dangerous schema change detected',
      CONTEXT_COLLECTED: 'DataHub MCP context verified',
      POLICY_EVALUATED: 'Deterministic release policy evaluated',
      BLOCKED: 'Unsafe release blocked before merge',
      REPAIR_PROPOSED: 'Bounded compatibility repair generated',
      VALIDATING: 'Running isolated dbt build',
      VERIFIED: 'Executable repair proof captured',
      AWAITING_APPROVAL: 'Repair proven — awaiting owner approval',
      APPROVED: 'Owner approval recorded',
      PUBLISHED: 'Validated patch published for review',
      LEARNED: 'Approved repair and reusable knowledge written back',
      REJECTED: 'Owner rejected repair — release remains blocked',
      CONTEXT_UNAVAILABLE: 'DataHub unavailable — failed closed',
      VALIDATION_FAILED: 'dbt validation failed — release remains blocked',
      MANUAL_REVIEW: 'Unexpected failure — manual review required',
    };
    setNotice(messages[incident.state] || incident.state);
  }, [incident?.state]);

  const start = async (mode: 'live' | 'replay') => {
    setBusy(true);
    setNotice(mode === 'live' ? 'Starting live MCP investigation' : 'Starting labeled replay');
    try {
      const response = await fetch('/api/v1/incidents', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({scenario: 'breaking-column-rename', execution_mode: mode}),
      });
      if (!response.ok) {
        if (response.status === 409 || response.status === 429) {
          throw new Error('Another judge is running the live demo. Try again shortly, or use the clearly labeled Replay.');
        }
        throw new Error(await response.text());
      }
      setIncident((await response.json()) as Incident);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Could not start incident');
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    setBusy(true);
    try {
      const response = await fetch('/api/v1/demo/reset', {method: 'POST'});
      if (!response.ok) throw new Error(await response.text());
      setIncident(null);
      setNotice('Demo reset: no incident state or validation schema remains');
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Reset failed');
    } finally {
      setBusy(false);
    }
  };

  const approve = async (decision: 'approve' | 'reject') => {
    if (!incident) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/v1/incidents/${incident.run_id}/approval`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({decision, actor: 'Revenue Analytics Owner'}),
      });
      if (!response.ok) throw new Error(await response.text());
      const record = (await response.json()) as Incident;
      setIncident(record);
      if (decision === 'approve') {
        window.setTimeout(() => refresh(record.run_id), 900);
      }
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Approval failed');
    } finally {
      setBusy(false);
    }
  };

  const stateTone = useMemo(() => {
    if (!incident) return 'ready';
    if (incident.state === 'BLOCKED') return 'blocked';
    if (incident.state === 'AWAITING_APPROVAL') return 'approval';
    if (incident.state === 'LEARNED' || incident.state === 'VERIFIED') return 'verified';
    if (terminalStates.has(incident.state)) return 'blocked';
    return 'active';
  }, [incident]);

  const progress = incident ? progressByState[incident.state] : undefined;
  const awaitingApproval = incident?.state === 'AWAITING_APPROVAL';

  return (
    <main>
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><ShieldAlert size={22} /></div>
          <div><strong>RepairPilot</strong><span>Incident-to-Repair Autopilot</span></div>
        </div>
        <div className="topbar-right">
          <span className={`mode-chip ${incident?.mode || 'live'}`}>{incident?.mode === 'replay' ? 'REPLAY' : 'LIVE SERVICE'}</span>
          <button className="catalog-link" onClick={() => setShowDataHubGuide(true)}>Inspect DataHub <ExternalLink size={14} /></button>
        </div>
      </header>

      <section className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">NORTHSTAR COMMERCE · CHANGE CONTROL</p>
          <h1>One renamed field.<br /><span>Four downstream assets at risk.</span></h1>
          <p className="lede">RepairPilot uses DataHub context to block the unsafe release, generate a compatible repair, prove it with dbt, and leave reusable knowledge behind.</p>
          <p className="execution-boundary"><Check size={13} /> Synthetic business data <span>·</span> Real execution</p>
          <div className="actions">
            <button className="primary" onClick={() => start('live')} disabled={busy || !!incident}>
              <Play size={16} fill="currentColor" /> Run live incident
            </button>
            <button className="secondary" onClick={() => start('replay')} disabled={busy || !!incident}>Replay evidence</button>
            <button className="reset-button" onClick={reset} disabled={busy} aria-label="Start a new run and reset the demo"><RefreshCcw size={16} /> New run / Reset</button>
          </div>
          <p className="judge-path"><strong>1</strong> Run (~35s) <ArrowRight /> <strong>2</strong> Approve repair <ArrowRight /> <strong>3</strong> Inspect write-back</p>
          <p className="notice"><Activity size={14} /> {notice}</p>
          {progress && <p className="run-progress"><span>{progress.step}</span><strong>{progress.remaining}</strong></p>}
          {awaitingApproval && <a className="approval-jump" href="#approval"><UserCheck size={15} /> Go to approval</a>}
        </div>
        <SchemaDiff />
      </section>

      <section className="status-strip">
        <div><span>Release decision</span><strong className={stateTone}>{incident?.risk?.action || 'PENDING'}</strong></div>
        <div><span>Risk score</span><strong>{incident?.risk ? `${incident.risk.score}/100` : '—'}</strong></div>
        <div><span>Current state</span><strong>{incident?.state || 'READY'}</strong></div>
        <div><span>Run ID</span><code>{incident?.run_id.slice(0, 8) || 'not-started'}</code></div>
      </section>

      <section className="workspace">
        <Timeline events={incident?.events || []} />
        <div className="panel-stack">
          <ContextPanel incident={incident} />
          <RiskPanel incident={incident} />
          <RepairPanel incident={incident} />
          <ValidationPanel incident={incident} />
          <ApprovalPanel incident={incident} busy={busy} approve={approve} />
          <MemoryPanel incident={incident} onInspectDataHub={() => setShowDataHubGuide(true)} />
        </div>
      </section>

      <footer><span>Block.</span><span>Repair.</span><span>Prove.</span><span>Remember.</span></footer>
      {showDataHubGuide && <DataHubGuide onClose={() => setShowDataHubGuide(false)} />}
    </main>
  );
}

function SchemaDiff() {
  return <article className="diff-card card">
    <div className="card-head"><FileCode2 size={16} /><span>models/staging/stg_orders.sql</span><code>proposed</code></div>
    <pre><span className="line muted">  tax_amount,</span>{'\n'}<span className="line removed">- gross_amount,</span>{'\n'}<span className="line added">+ gross_amount as gross_revenue,</span>{'\n'}<span className="line muted">  order_status</span></pre>
    <div className="diff-warning"><CircleStop size={15} /> Breaking contract detected before merge</div>
  </article>;
}

function Timeline({events}: {events: Event[]}) {
  const defaultSteps = ['DETECTED', 'CONTEXT_COLLECTED', 'BLOCKED', 'REPAIR_PROPOSED', 'VERIFIED', 'APPROVED', 'LEARNED'];
  const completed = new Set(events.map((event) => event.state));
  return <aside className="timeline card">
    <p className="section-label">AUTOPILOT TRACE</p>
    {defaultSteps.map((step, index) => <div className={`timeline-step ${completed.has(step) ? 'complete' : ''}`} key={step}>
      <span>{completed.has(step) ? <Check size={13} /> : index + 1}</span><div><strong>{step.replaceAll('_', ' ')}</strong><small>{events.findLast((event: Event) => event.state === step)?.message || 'Waiting'}</small></div>
    </div>)}
  </aside>;
}

function ContextPanel({incident}: {incident: Incident | null}) {
  const context = incident?.context;
  return <article className="card panel context-panel">
    <PanelTitle icon={<Network />} eyebrow="DATAHUB MCP" title="Verified blast radius" />
    {!context ? <Empty text="Lineage, ownership, governance, assertions, and queries will appear here." /> : <>
      <div className="metric-row">
        <Metric value={context.downstream_assets.length + context.downstream_dashboards.length} label="impacted assets" />
        <Metric value={context.owners[0]} label="accountable owner" />
        <Metric value={context.queries.length} label="usage queries" />
      </div>
      <div className="tag-row">{context.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
      <div className="lineage-row"><code>stg_orders.gross_amount</code><ArrowRight /><code>int_order_revenue</code><ArrowRight /><code>Executive Revenue Pulse</code></div>
      <div className="tool-row">{context.evidence.map((item) => <span key={item.tool}><Check size={12} /> {item.tool}</span>)}</div>
    </>}
  </article>;
}

function RiskPanel({incident}: {incident: Incident | null}) {
  const risk = incident?.risk;
  return <article className={`card panel risk-panel ${risk ? 'revealed' : ''}`}>
    <PanelTitle icon={<ShieldAlert />} eyebrow="DETERMINISTIC POLICY" title={risk ? `${risk.action}: ${risk.score}/100` : 'Release decision pending'} />
    {!risk ? <Empty text="The LLM cannot influence this policy decision." /> : <>
      <div className="score-track"><span style={{width: `${risk.score}%`}} /></div>
      <div className="rule-grid">{risk.matched_rules.map((rule) => <span key={rule}><Check size={12} /> {rule.replaceAll('_', ' ')}</span>)}</div>
      <p>{risk.rationale}</p>
    </>}
  </article>;
}

function RepairPanel({incident}: {incident: Incident | null}) {
  const repair = incident?.repair;
  return <article className="card panel repair-panel">
    <PanelTitle icon={<Sparkles />} eyebrow="DEEPSEEK V4 FLASH" title="Bounded repair proposal" />
    {!repair ? <Empty text="Repair generation starts only after the original change is blocked." /> : <>
      <p className="root-cause"><strong>Root cause</strong>{repair.root_cause}</p>
      <div className="operation-grid">{repair.operations.map((operation, index) => <div key={operation.operation}><span>0{index + 1}</span><strong>{operation.operation.replaceAll('_', ' ')}</strong><code>{operation.target.replace('warehouse/', '')}</code><p>{operation.rationale}</p></div>)}</div>
      <div className="confidence">Model confidence <strong>{Math.round(repair.confidence * 100)}%</strong></div>
    </>}
  </article>;
}

function ValidationPanel({incident}: {incident: Incident | null}) {
  const validation = incident?.validation;
  return <article className="card panel validation-panel">
    <PanelTitle icon={<Database />} eyebrow="ISOLATED DBT BUILD" title={validation?.repair_verified ? 'Repair proven' : 'Waiting for executable proof'} />
    {!validation ? <Empty text="The unsafe change must fail, then the repaired selection must pass." /> : <>
      <div className="proof-grid"><div><CircleStop /><strong>Breaking change reproduced</strong><span>Expected failure</span></div><div className="green"><Check /><strong>{validation.tests_passed} tests passed</strong><span>Zero failures</span></div></div>
      <code className="hash">GIT · {validation.base_commit.slice(0, 8)} → {validation.repair_commit.slice(0, 8)}</code>
      <code className="hash">PATCH SHA · {validation.patch_sha256.slice(0, 24)}…</code>
      <a className="artifact-link" href={`/api/v1/incidents/${incident?.run_id}/artifacts/repair.patch`}>Review Git patch <ExternalLink size={13} /></a>
    </>}
  </article>;
}

function ApprovalPanel({incident, busy, approve}: {incident: Incident | null; busy: boolean; approve: (decision: 'approve' | 'reject') => void}) {
  const awaiting = incident?.state === 'AWAITING_APPROVAL';
  return <article id="approval" className={`card panel approval-panel ${awaiting ? 'awaiting' : ''}`}>
    <PanelTitle icon={<UserCheck />} eyebrow="HUMAN AUTHORITY" title={incident?.approval ? `${incident.approval.decision}d by owner` : 'Owner approval'} />
    {!awaiting && !incident?.approval ? <Empty text="Approval unlocks only after the repair has executable proof." /> : awaiting ? <div className="approval-actions"><div><strong>Revenue Analytics Owner</strong><span>Reviewing a verified high-risk repair</span></div><button className="reject" onClick={() => approve('reject')} disabled={busy}>Reject</button><button className="approve" onClick={() => approve('approve')} disabled={busy}><Check size={15} /> Approve repair</button></div> : <p className="approved-copy"><Check size={15} /> Decision recorded with timestamp and run evidence.</p>}
  </article>;
}

function MemoryPanel({incident, onInspectDataHub}: {incident: Incident | null; onInspectDataHub: () => void}) {
  const writeback = incident?.writeback;
  return <article id="writeback" className="card panel memory-panel">
    <PanelTitle icon={<GitPullRequest />} eyebrow="DATAHUB WRITEBACK" title={writeback ? 'The next incident starts smarter' : 'Institutional memory'} />
    {!writeback ? <Empty text="Verified evidence, the assertion, and runbook are written back after approval." /> : <><div className="memory-grid"><button onClick={onInspectDataHub}><span>INCIDENT</span><strong>Root cause + proof</strong><ExternalLink /></button><button onClick={onInspectDataHub}><span>ASSERTION</span><strong>gross_revenue not null</strong><ExternalLink /></button><button onClick={onInspectDataHub}><span>RUNBOOK</span><strong>Safe column rename</strong><ExternalLink /></button>{incident?.pull_request_url && <a href={incident.pull_request_url} target="_blank"><span>GITHUB PR</span><strong>Review validated diff</strong><ExternalLink /></a>}</div><button className="inspect-writeback" onClick={onInspectDataHub}>Inspect DataHub write-back <ExternalLink size={13} /></button></>}
  </article>;
}

function DataHubGuide({onClose}: {onClose: () => void}) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="datahub-guide card" role="dialog" aria-modal="true" aria-labelledby="datahub-guide-title" onMouseDown={(event) => event.stopPropagation()}>
      <button className="modal-close" onClick={onClose} aria-label="Close DataHub access instructions">×</button>
      <p className="eyebrow">READ-ONLY JUDGE ACCESS</p>
      <h2 id="datahub-guide-title">Inspect the real DataHub graph</h2>
      <p>On first login, dismiss the Welcome Tour and the “Narrow your search” tip. The catalog contains synthetic demo metadata only.</p>
      <div className="credential-grid"><div><span>Username</span><code>judge@repairpilot.demo</code></div><div><span>Password</span><code>RepairPilot-Judge-2026!</code></div></div>
      <ol><li>Open the direct <code>stg_orders</code> asset.</li><li>Inspect Owner, Domain, Tags, Schema, Queries, Assertions, and field-level Lineage.</li><li>After approval, open Documents for the per-run Incident and shared Runbook.</li></ol>
      <div className="modal-actions"><a className="secondary-link" href={datahubUrl} target="_blank">DataHub home <ExternalLink size={14} /></a><a className="primary-link" href={stgOrdersUrl} target="_blank">Open stg_orders <ExternalLink size={14} /></a></div>
    </section>
  </div>;
}

function PanelTitle({icon, eyebrow, title}: {icon: React.ReactNode; eyebrow: string; title: string}) {
  return <div className="panel-title"><span>{icon}</span><div><p>{eyebrow}</p><h2>{title}</h2></div></div>;
}

function Metric({value, label}: {value: string | number; label: string}) {
  return <div className="metric"><strong>{value}</strong><span>{label}</span></div>;
}

function Empty({text}: {text: string}) { return <p className="empty">{text}</p>; }

export default App;
