from datetime import datetime, timezone
from uuid import uuid4

from app.models.manifest import ActionManifest
from app.models.policy import PolicyDecisionTarget, PolicyResult
from app.models.risk import RiskReport
from app.models.verdict import DecisionEnum, GovernanceVerdict
from app.models.verification import (
    VerificationReport,
    VerificationStatus,
)


class DecisionGate:
    """
    Deterministic final decision gate.

    Decision precedence:

    1. BLOCK
    2. RETRY
    3. HUMAN_REVIEW from policy
    4. HUMAN_REVIEW from high risk
    5. ALLOW
    6. Fallback HUMAN_REVIEW
    """

    RISK_REVIEW_THRESHOLD = 60.0

    def decide(
        self,
        manifest: ActionManifest,
        verification: VerificationReport,
        policy: PolicyResult,
        risk: RiskReport,
    ) -> GovernanceVerdict:

        decision, reason = self._determine_decision(
            verification=verification,
            policy=policy,
            risk=risk,
        )

        return GovernanceVerdict(
            action_id=manifest.action_id,
            agent_id=manifest.agent_id,
            action=manifest.action,
            decision=decision,
            reason=reason,
            verification=verification,
            policy=policy,
            risk=risk,
            audit_event_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def _determine_decision(
        cls,
        verification: VerificationReport,
        policy: PolicyResult,
        risk: RiskReport,
    ) -> tuple[DecisionEnum, str]:

        # 1. Blocking policy always wins.
        if policy.recommended_decision == PolicyDecisionTarget.BLOCK:
            return (
                DecisionEnum.BLOCK,
                "A blocking policy rule was triggered.",
            )

        # 2. Verification mismatch requires retry/recheck.
        if verification.status == VerificationStatus.MISMATCH:
            return (
                DecisionEnum.RETRY,
                "Trusted evidence disagrees with the agent claim; retry verification.",
            )

        # Verification errors should not be allowed through.
        if verification.status == VerificationStatus.ERROR:
            return (
                DecisionEnum.HUMAN_REVIEW,
                "Verification encountered an error and requires human review.",
            )

        # Missing evidence cannot safely be treated as verified.
        if verification.status == VerificationStatus.MISSING_EVIDENCE:
            return (
                DecisionEnum.HUMAN_REVIEW,
                "Required verification evidence is missing.",
            )

        # 3. Policy explicitly recommends human review.
        if (
            policy.recommended_decision
            == PolicyDecisionTarget.HUMAN_REVIEW
        ):
            return (
                DecisionEnum.HUMAN_REVIEW,
                "A policy rule requires human review.",
            )

        # 4. High risk requires human review.
        if risk.total_score >= cls.RISK_REVIEW_THRESHOLD:
            return (
                DecisionEnum.HUMAN_REVIEW,
                f"Risk score {risk.total_score} meets or exceeds the review threshold.",
            )

        # 5. Verified + low risk = allow.
        if (
            verification.status == VerificationStatus.MATCH
            and risk.total_score < cls.RISK_REVIEW_THRESHOLD
        ):
            return (
                DecisionEnum.ALLOW,
                "Verification passed and risk is below the review threshold.",
            )

        # 6. Safe fallback.
        return (
            DecisionEnum.HUMAN_REVIEW,
            "The action could not be safely classified for automatic approval.",
        )