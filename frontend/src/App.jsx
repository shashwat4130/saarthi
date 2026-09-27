import { useEffect, useState } from 'react'
import {
  Activity,
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  UserCheck,
  Ban,
  Database,
  LockKeyhole,
  ChevronRight,
} from 'lucide-react'

import {
  checkHealth,
  runScenario as runScenarioApi,
  getAuditEvents,
  verifyAuditChain,
} from './services/api'

const scenarios = [
  {
    id: 'valid_action',
    label: 'Valid Action',
    icon: ShieldCheck,
    description: 'Verified low-risk action',
  },
  {
    id: 'hallucinated_claim',
    label: 'Hallucinated Claim',
    icon: RefreshCw,
    description: 'Evidence mismatch',
  },
  {
    id: 'risky_refund',
    label: 'Risky Refund',
    icon: UserCheck,
    description: 'High-value transaction',
  },
  {
    id: 'critical_block',
    label: 'Critical Block',
    icon: Ban,
    description: 'Policy violation',
  },
]

const decisionConfig = {
  ALLOW: {
    icon: ShieldCheck,
    title: 'ACTION ALLOWED',
    className:
      'border-emerald-400/30 bg-emerald-500/10 text-emerald-300',
  },
  RETRY: {
    icon: RefreshCw,
    title: 'RETRY REQUIRED',
    className:
      'border-amber-400/30 bg-amber-500/10 text-amber-300',
  },
  HUMAN_REVIEW: {
    icon: UserCheck,
    title: 'HUMAN REVIEW',
    className:
      'border-blue-400/30 bg-blue-500/10 text-blue-300',
  },
  BLOCK: {
    icon: Ban,
    title: 'ACTION BLOCKED',
    className:
      'border-red-400/30 bg-red-500/10 text-red-300',
  },
}

function App() {
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [verdict, setVerdict] = useState(null)
  const [loading, setLoading] = useState(false)
  const [backendOnline, setBackendOnline] = useState(false)
  const [auditValid, setAuditValid] = useState(false)
  const [auditEvents, setAuditEvents] = useState([])
  const [error, setError] = useState('')

  const refreshAudit = async () => {
    try {
      const [events, chain] = await Promise.all([
        getAuditEvents(20),
        verifyAuditChain(),
      ])

      setAuditEvents(Array.isArray(events) ? events : [])
      setAuditValid(Boolean(chain?.valid))
    } catch (err) {
      console.error('Audit refresh failed:', err)
    }
  }

  const runScenario = async (scenario) => {
    setSelectedScenario(scenario)
    setLoading(true)
    setVerdict(null)
    setError('')

    try {
      const result = await runScenarioApi(scenario.id)

      /*
       * Demo endpoint returns:
       *
       * {
       *   action: {...},
       *   verdict: {...}
       * }
       *
       * The dashboard needs the nested governance verdict.
       */
      const governanceVerdict = result?.verdict || result

      setVerdict(governanceVerdict)

      await refreshAudit()
    } catch (err) {
      console.error('Scenario failed:', err)

      setError(
        err.response?.data?.detail ||
          err.message ||
          'Unable to connect to SAARTHI backend.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const initializeBackend = async () => {
      try {
        await checkHealth()
        setBackendOnline(true)
        await refreshAudit()
      } catch (err) {
        console.error('Backend unavailable:', err)
        setBackendOnline(false)
      }
    }

    initializeBackend()

    const interval = setInterval(refreshAudit, 3000)

    return () => clearInterval(interval)
  }, [])

  const decision = verdict?.decision
  const config = decision ? decisionConfig[decision] : null
  const DecisionIcon = config?.icon

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100">

      {/* Background */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />
        <div className="absolute -right-40 top-20 h-96 w-96 rounded-full bg-violet-600/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6 py-6 lg:px-8">

        {/* HEADER */}
        <header className="mb-8 flex flex-col gap-5 border-b border-white/10 pb-6 sm:flex-row sm:items-center sm:justify-between">

          <div className="flex items-center gap-4">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-indigo-400/30 bg-indigo-500/10 shadow-lg shadow-indigo-950/30">
              <ShieldCheck className="h-6 w-6 text-indigo-400" />
            </div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                SAARTHI
              </h1>

              <p className="text-sm text-slate-400">
                Runtime Governance & Safety Layer
              </p>
            </div>

          </div>

          <div
            className={`flex items-center gap-3 rounded-full border px-4 py-2 ${
              backendOnline
                ? 'border-emerald-400/20 bg-emerald-400/5'
                : 'border-red-400/20 bg-red-400/5'
            }`}
          >

            <span
              className={`h-2.5 w-2.5 rounded-full ${
                backendOnline
                  ? 'bg-emerald-400'
                  : 'bg-red-400'
              }`}
            />

            <span
              className={`text-sm font-medium ${
                backendOnline
                  ? 'text-emerald-300'
                  : 'text-red-300'
              }`}
            >
              {backendOnline
                ? 'Runtime Active'
                : 'Backend Offline'}
            </span>

          </div>

        </header>

        {/* STATUS CARDS */}
        <section className="mb-8 grid gap-4 md:grid-cols-3">

          <StatusCard
            icon={Activity}
            title="Governance Runtime"
            value={
              backendOnline
                ? 'Operational'
                : 'Offline'
            }
            status={
              backendOnline
                ? 'Online'
                : 'Offline'
            }
          />

          <StatusCard
            icon={Database}
            title="Trusted State"
            value="SQLite Connected"
            status="Ready"
          />

          <StatusCard
            icon={LockKeyhole}
            title="Audit Integrity"
            value={
              auditValid
                ? 'Chain Verified'
                : 'Checking...'
            }
            status={
              auditValid
                ? 'Secure'
                : 'Pending'
            }
          />

        </section>

        {/* MAIN DASHBOARD */}
        <div className="grid gap-6 lg:grid-cols-[1fr_1.35fr]">

          {/* SCENARIOS */}
          <section className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 shadow-2xl shadow-black/20">

            <div className="mb-5">

              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-400">
                Runtime Simulation
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                Test Agent Actions
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Send a proposed action through the governance pipeline.
              </p>

            </div>

            <div className="space-y-3">

              {scenarios.map((scenario) => {

                const Icon = scenario.icon
                const active =
                  selectedScenario?.id === scenario.id

                return (
                  <button
                    key={scenario.id}
                    onClick={() => runScenario(scenario)}
                    disabled={loading}
                    className={`group flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-all duration-200 ${
                      active
                        ? 'border-indigo-400/40 bg-indigo-500/10'
                        : 'border-white/10 bg-white/[0.02] hover:border-indigo-400/30 hover:bg-indigo-500/[0.06]'
                    } ${
                      loading
                        ? 'cursor-wait opacity-70'
                        : ''
                    }`}
                  >

                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-800/80">
                      <Icon className="h-5 w-5 text-indigo-400" />
                    </div>

                    <div className="min-w-0 flex-1">

                      <p className="font-medium text-slate-100">
                        {scenario.label}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {scenario.description}
                      </p>

                    </div>

                    <ChevronRight className="h-5 w-5 text-slate-600 transition-transform group-hover:translate-x-1 group-hover:text-indigo-400" />

                  </button>
                )
              })}

            </div>

            <div className="mt-5 rounded-xl border border-white/5 bg-black/10 p-4">

              <p className="text-xs leading-5 text-slate-500">
                Each scenario passes through verification, policy
                evaluation, risk scoring and the final decision gate.
              </p>

            </div>

          </section>

          {/* DECISION */}
          <section className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 shadow-2xl shadow-black/20">

            <div className="mb-5">

              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-400">
                Governance Decision
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                Live Action Assessment
              </h2>

            </div>

            {!selectedScenario ? (

              <EmptyState />

            ) : loading ? (

              <div className="flex min-h-[390px] items-center justify-center rounded-xl border border-dashed border-white/10 bg-black/10">

                <div className="text-center">

                  <RefreshCw className="mx-auto h-9 w-9 animate-spin text-indigo-400" />

                  <p className="mt-4 font-medium text-slate-300">
                    Running governance pipeline
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    Verifying evidence, policies and risk...
                  </p>

                </div>

              </div>

            ) : error ? (

              <div className="flex min-h-[390px] items-center justify-center rounded-xl border border-red-400/20 bg-red-500/5 p-8 text-center">

                <div>

                  <Ban className="mx-auto h-10 w-10 text-red-400" />

                  <h3 className="mt-4 font-semibold text-red-300">
                    Backend Request Failed
                  </h3>

                  <p className="mt-2 text-sm text-slate-400">
                    {error}
                  </p>

                </div>

              </div>

            ) : verdict ? (

              <div className="space-y-4">

                {/* FINAL DECISION */}
                <div
                  className={`rounded-2xl border p-6 ${
                    config?.className ||
                    'border-white/10 bg-white/5 text-slate-200'
                  }`}
                >

                  <div className="flex items-center gap-4">

                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-black/20">

                      {DecisionIcon && (
                        <DecisionIcon className="h-7 w-7" />
                      )}

                    </div>

                    <div>

                      <p className="text-xs uppercase tracking-[0.2em] opacity-70">
                        Final Decision
                      </p>

                      <p className="mt-1 text-2xl font-bold">
                        {decision || 'UNKNOWN'}
                      </p>

                      <p className="mt-1 text-sm opacity-80">
                        {config?.title || 'Governance Result'}
                      </p>

                    </div>

                  </div>

                  <div className="mt-5 border-t border-current/10 pt-4">

                    <p className="text-sm leading-6 opacity-90">
                      {safeText(verdict.reason)}
                    </p>

                  </div>

                </div>

                {/* METRICS */}
                <div className="grid gap-3 sm:grid-cols-3">

                  <MetricCard
                    title="Verification"
                    value={safeText(
                      verdict.verification?.status,
                    )}
                    subtext={
                      verdict.verification?.verified
                        ? 'Verified'
                        : 'Mismatch detected'
                    }
                  />

                  <MetricCard
                    title="Risk Score"
                    value={
                      verdict.risk?.total_score !== undefined
                        ? String(
                            verdict.risk.total_score,
                          )
                        : '—'
                    }
                    subtext={safeText(
                      verdict.risk?.risk_level,
                      'Risk assessment',
                    )}
                  />

                  <MetricCard
                    title="Policy"
                    value={safeText(
                      verdict.policy?.decision,
                    )}
                    subtext={
                      Array.isArray(
                        verdict.policy?.triggered_rules,
                      )
                        ? `${verdict.policy.triggered_rules.length} rule(s) triggered`
                        : 'Policy evaluated'
                    }
                  />

                </div>

                {/* ACTION DETAILS */}
                <div className="rounded-xl border border-white/10 bg-black/10 p-5">

                  <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    Action Details
                  </p>

                  <div className="grid gap-4 sm:grid-cols-2">

                    <Detail
                      label="Action"
                      value={verdict.action}
                    />

                    <Detail
                      label="Agent"
                      value={verdict.agent_id}
                    />

                    <Detail
                      label="Action ID"
                      value={verdict.action_id}
                    />

                    <Detail
                      label="Audit Event"
                      value={verdict.audit_event_id}
                    />

                  </div>

                </div>

                {/* VERIFICATION DETAILS */}
                {verdict.verification && (
                  <div className="rounded-xl border border-white/10 bg-black/10 p-5">

                    <p className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                      Verification Details
                    </p>

                    <div className="mt-4 grid gap-4 sm:grid-cols-2">

                      <Detail
                        label="Status"
                        value={
                          verdict.verification.status
                        }
                      />

                      <Detail
                        label="Verified"
                        value={
                          verdict.verification.verified
                            ? 'YES'
                            : 'NO'
                        }
                      />

                      <Detail
                        label="Checked Fields"
                        value={
                          verdict.verification
                            .checked_fields
                        }
                      />

                      <Detail
                        label="Discrepancies"
                        value={
                          verdict.verification
                            .discrepancies
                        }
                      />

                    </div>

                  </div>
                )}

              </div>

            ) : null}

          </section>

        </div>

        {/* GOVERNANCE PIPELINE */}
        <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.025] p-5">

          <div className="mb-5">

            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-400">
              Governance Pipeline
            </p>

            <h2 className="mt-2 text-xl font-semibold">
              How SAARTHI Controls the Action
            </h2>

          </div>

          <div className="grid gap-3 md:grid-cols-5">

            {[
              ['01', 'Verify', 'Ground truth'],
              ['02', 'Policy', 'Rules'],
              ['03', 'Risk', '0–100 score'],
              ['04', 'Decision', 'Safety gate'],
              ['05', 'Audit', 'Hash chain'],
            ].map(([number, title, subtitle]) => (

              <div
                key={number}
                className="rounded-xl border border-white/10 bg-black/10 p-4"
              >

                <span className="text-xs font-semibold text-indigo-400">
                  {number}
                </span>

                <p className="mt-2 font-medium">
                  {title}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {subtitle}
                </p>

              </div>

            ))}

          </div>

        </section>

        {/* AUDIT TIMELINE */}
        <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.025] p-5">

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

            <div>

              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-400">
                Cryptographic Audit
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                Decision Timeline
              </h2>

            </div>

            <div className="flex items-center gap-2 text-xs">

              <span
                className={`h-2 w-2 rounded-full ${
                  auditValid
                    ? 'bg-emerald-400'
                    : 'bg-amber-400'
                }`}
              />

              <span
                className={
                  auditValid
                    ? 'text-emerald-400'
                    : 'text-amber-400'
                }
              >
                {auditValid
                  ? 'Chain integrity verified'
                  : 'Checking chain'}
              </span>

            </div>

          </div>

          {auditEvents.length === 0 ? (

            <div className="mt-5 rounded-xl border border-dashed border-white/10 p-8 text-center">

              <p className="text-sm text-slate-500">
                No audit events yet.
              </p>

            </div>

          ) : (

            <div className="mt-5 space-y-2">

              {auditEvents.slice(0, 8).map((event) => (

                <div
                  key={event.event_id}
                  className="flex items-center gap-4 rounded-xl border border-white/5 bg-black/10 p-4"
                >

                  <div className="h-2.5 w-2.5 shrink-0 rounded-full bg-indigo-400" />

                  <div className="min-w-0 flex-1">

                    <p className="font-medium">
                      {safeText(event.action)}
                    </p>

                    <p className="truncate text-xs text-slate-500">
                      {safeText(event.event_id)}
                    </p>

                  </div>

                  <span className="rounded-full border border-white/10 px-3 py-1 text-xs">
                    {safeText(event.decision)}
                  </span>

                  <span className="hidden text-xs text-slate-500 sm:block">
                    Risk {safeText(event.risk_score)}
                  </span>

                </div>

              ))}

            </div>

          )}

        </section>

        <footer className="py-8 text-center text-xs text-slate-600">
          SAARTHI • Runtime Governance for Autonomous AI
        </footer>

      </div>
    </div>
  )
}

/* ==================================================
   HELPERS
================================================== */

function safeText(value, fallback = '—') {
  if (value === null || value === undefined) {
    return fallback
  }

  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch {
      return '[Object]'
    }
  }

  return String(value)
}

function StatusCard({
  icon: Icon,
  title,
  value,
  status,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">

      <div className="flex items-center gap-3">

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
          <Icon className="h-5 w-5 text-indigo-400" />
        </div>

        <div>

          <p className="text-xs text-slate-500">
            {title}
          </p>

          <p className="mt-1 font-medium">
            {safeText(value)}
          </p>

        </div>

        <span className="ml-auto rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
          {safeText(status)}
        </span>

      </div>

    </div>
  )
}

function MetricCard({
  title,
  value,
  subtext,
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/10 p-4">

      <p className="text-xs text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-lg font-semibold text-slate-200">
        {safeText(value)}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {safeText(subtext)}
      </p>

    </div>
  )
}

function Detail({
  label,
  value,
}) {
  return (
    <div>

      <p className="text-xs uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <pre className="mt-1 max-h-32 overflow-auto whitespace-pre-wrap break-words font-sans text-sm text-slate-300">
        {safeText(value)}
      </pre>

    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex min-h-[390px] flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-black/10 text-center">

      <ShieldAlert className="mb-4 h-10 w-10 text-slate-600" />

      <h3 className="font-medium text-slate-300">
        No action evaluated
      </h3>

      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
        Select a scenario from the left to send an agent
        action through SAARTHI.
      </p>

    </div>
  )
}

export default App