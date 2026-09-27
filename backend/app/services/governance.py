from app.models.manifest import ActionManifest
from app.models.verdict import GovernanceVerdict

from app.services.verifier import GroundTruthVerifier
from app.services.policy_engine import PolicyEngine
from app.services.risk_engine import RiskEngine
from app.services.decision_gate import DecisionGate
from app.audit.ledger import AuditLedger


class GovernanceService:
    """
    Main SAARTHI runtime governance pipeline.

    Flow:

        ActionManifest
            ↓
        Ground Truth Verification
            ↓
        Policy Evaluation
            ↓
        Risk Assessment
            ↓
        Decision Gate
            ↓
        Audit Ledger
            ↓
        GovernanceVerdict
    """

    def __init__(
        self,
        verifier=None,
        policy_engine=None,
        risk_engine=None,
        decision_gate=None,
        audit_ledger=None,
    ):
        self.verifier = verifier or GroundTruthVerifier()
        self.policy_engine = policy_engine or PolicyEngine()
        self.risk_engine = risk_engine or RiskEngine()
        self.decision_gate = decision_gate or DecisionGate()
        self.audit_ledger = audit_ledger or AuditLedger()

    def evaluate(self, manifest: ActionManifest) -> GovernanceVerdict:
        """
        Execute the complete SAARTHI governance pipeline.
        """

        # ---------------------------------------------------------
        # Stage 1: Ground-truth verification
        # ---------------------------------------------------------
        verification = self.verifier.verify(manifest)

        # ---------------------------------------------------------
        # Stage 2: Policy evaluation
        # ---------------------------------------------------------
        policy = self.policy_engine.evaluate(manifest)

        # ---------------------------------------------------------
        # Stage 3: Risk assessment
        # ---------------------------------------------------------
        risk = self.risk_engine.evaluate(
            manifest,
            verification,
            policy,
        )

        # ---------------------------------------------------------
        # Stage 4: Final decision
        # ---------------------------------------------------------
        decision = self.decision_gate.decide(
            manifest,
            verification,
            policy,
            risk,
        )

        # ---------------------------------------------------------
        # Stage 5: Create audit payload
        # ---------------------------------------------------------
        audit_payload = {
            "manifest": manifest.model_dump(mode="json"),
            "verification": verification.model_dump(mode="json"),
            "policy": policy.model_dump(mode="json"),
            "risk": risk.model_dump(mode="json"),
        }

        # ---------------------------------------------------------
        # Stage 6: Commit decision to audit ledger
        # ---------------------------------------------------------
        audit_record = self.audit_ledger.append(
            action_id=manifest.action_id,
            agent_id=manifest.agent_id,
            action=manifest.action,
            decision=decision.decision.value,
            reason=decision.reason,
            risk_score=risk.total_score,
            payload=audit_payload,
        )

        # ---------------------------------------------------------
        # Stage 7: Build final governance verdict
        # ---------------------------------------------------------
        verdict = GovernanceVerdict(
            action_id=manifest.action_id,
            agent_id=manifest.agent_id,
            action=manifest.action,
            decision=decision.decision,
            reason=decision.reason,
            verification=verification,
            policy=policy,
            risk=risk,
            audit_event_id=audit_record.event_id,
            timestamp=audit_record.timestamp,
        )

        return verdict