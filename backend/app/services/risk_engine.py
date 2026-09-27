from app.models.manifest import ActionManifest
from app.models.policy import PolicyResult
from app.models.risk import RiskFactor, RiskReport
from app.models.verification import VerificationReport, VerificationStatus


class RiskEngine:
    """
    Deterministic 0-100 risk scoring engine.

    Risk factors:
    - Financial impact       35%
    - Reversibility          20%
    - Verification mismatch 25%
    - Policy severity        20%

    The engine does not:
    - access the database
    - call an LLM
    - make network requests
    - use randomness
    """

    FINANCIAL_WEIGHT = 0.35
    REVERSIBILITY_WEIGHT = 0.20
    DISCREPANCY_WEIGHT = 0.25
    POLICY_WEIGHT = 0.20

    def evaluate(
        self,
        manifest: ActionManifest,
        verification: VerificationReport,
        policy: PolicyResult,
    ) -> RiskReport:
        financial = self._financial_score(manifest)
        reversibility = self._reversibility_score(manifest)
        discrepancy = self._discrepancy_score(verification)
        policy_score = self._policy_score(policy)

        factors = {
            "financial": self._build_factor(
                score=financial,
                weight=self.FINANCIAL_WEIGHT,
                explanation="Risk from the financial value of the action.",
            ),
            "reversibility": self._build_factor(
                score=reversibility,
                weight=self.REVERSIBILITY_WEIGHT,
                explanation="Risk based on how difficult the action is to reverse.",
            ),
            "discrepancy": self._build_factor(
                score=discrepancy,
                weight=self.DISCREPANCY_WEIGHT,
                explanation="Risk caused by disagreement between agent claims and trusted evidence.",
            ),
            "policy": self._build_factor(
                score=policy_score,
                weight=self.POLICY_WEIGHT,
                explanation="Risk based on the severity of triggered policies.",
            ),
        }

        raw_score = sum(
            factor.weighted_score
            for factor in factors.values()
        )

        total_score = round(raw_score * 10, 2)

        return RiskReport(
            total_score=total_score,
            risk_level=self._risk_level(total_score),
            factors=factors,
        )

    @staticmethod
    def _build_factor(
        score: float,
        weight: float,
        explanation: str,
    ) -> RiskFactor:
        weighted_score = round(score * weight, 4)

        return RiskFactor(
            score=score,
            weight=weight,
            weighted_score=weighted_score,
            explanation=explanation,
        )

    @staticmethod
    def _financial_score(manifest: ActionManifest) -> float:
        amount = manifest.arguments.get("amount", 0)

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return 0.0

        if amount <= 0:
            return 0.0

        # ₹10,000 corresponds to a score of 10.
        score = (amount / 10000.0) * 10.0

        return min(10.0, score)

    @staticmethod
    def _reversibility_score(manifest: ActionManifest) -> float:
        action = manifest.action.lower()

        if action in {"read", "view", "lookup", "search"}:
            return 0.0

        if action in {"refund", "transfer", "payment"}:
            return 8.0

        if action in {"delete", "close_account", "terminate"}:
            return 10.0

        # Unknown state-changing actions get a moderate score.
        return 5.0

    @staticmethod
    def _discrepancy_score(
        verification: VerificationReport,
    ) -> float:
        if verification.status == VerificationStatus.MATCH:
            return 0.0

        if verification.status == VerificationStatus.MISSING_EVIDENCE:
            return 6.0

        if verification.status == VerificationStatus.MISMATCH:
            return 10.0

        if verification.status == VerificationStatus.ERROR:
            return 10.0

        return 0.0

    @staticmethod
    def _policy_score(
        policy: PolicyResult,
    ) -> float:
        if not policy.triggered_rules:
            return 0.0

        maximum_severity = max(
            rule.severity
            for rule in policy.triggered_rules
        )

        return min(10.0, float(maximum_severity))

    @staticmethod
    def _risk_level(total_score: float) -> str:
        if total_score < 30:
            return "LOW"

        if total_score < 60:
            return "MEDIUM"

        if total_score < 80:
            return "HIGH"

        return "CRITICAL"