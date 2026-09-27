import { useState } from 'react'
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

function App() {
  const [selectedScenario, setSelectedScenario] = useState(null)

  const runScenario = (scenario) => {
    setSelectedScenario({
      ...scenario,
      loading: true,
    })

    // Backend connection will be added next.
    setTimeout(() => {
      setSelectedScenario({
        ...scenario,
        loading: false,
      })
    }, 500)
  }

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100">

      {/* Background glow */}
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

          <div className="flex items-center gap-3 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-4 py-2">

            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
            </span>

            <span className="text-sm font-medium text-emerald-300">
              Runtime Active
            </span>

          </div>

        </header>

        {/* STATUS CARDS */}
        <section className="mb-8 grid gap-4 md:grid-cols-3">

          <StatusCard
            icon={Activity}
            title="Governance Runtime"
            value="Operational"
            status="Online"
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
            value="Chain Verified"
            status="Secure"
          />

        </section>

        {/* MAIN GRID */}
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
                const active = selectedScenario?.id === scenario.id

                return (
                  <button
                    key={scenario.id}
                    onClick={() => runScenario(scenario)}
                    className={`group flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-all duration-200 ${
                      active
                        ? 'border-indigo-400/40 bg-indigo-500/10'
                        : 'border-white/10 bg-white/[0.02] hover:border-indigo-400/30 hover:bg-indigo-500/[0.06]'
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
                Each scenario will pass through verification, policy
                evaluation, risk scoring and the final decision gate.
              </p>

            </div>

          </section>

          {/* GOVERNANCE DECISION */}
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

              <div className="flex min-h-[390px] flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-black/10 text-center">

                <ShieldAlert className="mb-4 h-10 w-10 text-slate-600" />

                <h3 className="font-medium text-slate-300">
                  No action evaluated
                </h3>

                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                  Select a scenario from the left to send an agent action
                  through SAARTHI.
                </p>

              </div>

            ) : (

              <div className="space-y-5">

                <div className="rounded-xl border border-indigo-400/20 bg-indigo-500/[0.06] p-5">

                  <div className="flex items-center justify-between">

                    <div>

                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        Selected Scenario
                      </p>

                      <p className="mt-1 text-lg font-semibold">
                        {selectedScenario.label}
                      </p>

                    </div>

                    <Activity className="h-5 w-5 text-indigo-400" />

                  </div>

                </div>

                {selectedScenario.loading ? (

                  <div className="flex min-h-[260px] items-center justify-center">

                    <div className="text-center">

                      <RefreshCw className="mx-auto h-8 w-8 animate-spin text-indigo-400" />

                      <p className="mt-4 text-sm text-slate-400">
                        Running governance pipeline...
                      </p>

                    </div>

                  </div>

                ) : (

                  <>

                    <div className="rounded-xl border border-white/10 bg-black/10 p-6 text-center">

                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                        Awaiting Backend Verdict
                      </p>

                      <p className="mt-3 text-sm text-slate-500">
                        Backend integration will populate the real
                        verification, policy, risk and decision data.
                      </p>

                    </div>

                    <div className="grid gap-3 sm:grid-cols-3">

                      <MetricCard
                        title="Verification"
                        value="—"
                      />

                      <MetricCard
                        title="Policy"
                        value="—"
                      />

                      <MetricCard
                        title="Risk"
                        value="— / 100"
                      />

                    </div>

                  </>

                )}

              </div>

            )}

          </section>

        </div>

        {/* PIPELINE */}
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

        {/* AUDIT */}
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

            <div className="flex items-center gap-2 text-xs text-emerald-400">

              <span className="h-2 w-2 rounded-full bg-emerald-400" />

              Chain integrity verified

            </div>

          </div>

          <div className="mt-5 rounded-xl border border-dashed border-white/10 p-8 text-center">

            <p className="text-sm text-slate-500">
              Audit events will appear here after backend integration.
            </p>

          </div>

        </section>

        {/* FOOTER */}
        <footer className="py-8 text-center text-xs text-slate-600">
          SAARTHI • Runtime Governance for Autonomous AI
        </footer>

      </div>
    </div>
  )
}

function StatusCard({ icon: Icon, title, value, status }) {
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
            {value}
          </p>

        </div>

        <span className="ml-auto rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
          {status}
        </span>

      </div>

    </div>
  )
}

function MetricCard({ title, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/10 p-4">

      <p className="text-xs text-slate-500">
        {title}
      </p>

      <p className="mt-2 font-semibold text-slate-300">
        {value}
      </p>

    </div>
  )
}

export default App