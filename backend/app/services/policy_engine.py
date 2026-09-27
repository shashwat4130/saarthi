import json
from pathlib import Path
from typing import Any

from app.models.manifest import ActionManifest
from app.models.policy import (
    PolicyDecisionTarget,
    PolicyOperator,
    PolicyResult,
    PolicyRule,
    TriggeredPolicy,
)


class PolicyEngine:
    """
    Deterministic policy evaluation engine.

    The engine:
    - Loads rules from policies.json
    - Evaluates an ActionManifest against those rules
    - Does not access the database
    - Does not call an LLM
    - Does not make network requests
    - Does not use randomness
    """

    def __init__(self, policies_path: str = "policies.json") -> None:
        self.policies_path = Path(policies_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> list[PolicyRule]:
        if not self.policies_path.exists():
            raise FileNotFoundError(
                f"Policy file not found: {self.policies_path}"
            )

        with self.policies_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [
            PolicyRule.model_validate(rule)
            for rule in data.get("rules", [])
        ]

    def evaluate(self, manifest: ActionManifest) -> PolicyResult:
        triggered_rules: list[TriggeredPolicy] = []

        for rule in self.rules:
            # Only evaluate rules intended for this action.
            if rule.action != manifest.action:
                continue

            actual_value = self._get_field_value(
                manifest,
                rule.field,
            )

            if self._matches(
                actual_value,
                rule.operator,
                rule.value,
            ):
                triggered_rules.append(
                    TriggeredPolicy(
                        rule_id=rule.rule_id,
                        field=rule.field,
                        actual_value=actual_value,
                        expected_value=rule.value,
                        operator=rule.operator,
                        severity=rule.severity,
                        target_decision=rule.target_decision,
                        explanation=rule.description,
                    )
                )

        recommended_decision = self._get_recommended_decision(
            triggered_rules
        )

        return PolicyResult(
            passed=len(triggered_rules) == 0,
            triggered_rules=triggered_rules,
            recommended_decision=recommended_decision,
        )

    @staticmethod
    def _get_field_value(
        manifest: ActionManifest,
        field: str,
    ) -> Any:
        """
        Resolve fields such as:

            arguments.amount
            arguments.account_status
            action
            agent_id
        """

        parts = field.split(".")
        current: Any = manifest

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)

            if current is None:
                return None

        return current

    @staticmethod
    def _matches(
        actual: Any,
        operator: PolicyOperator,
        expected: Any,
    ) -> bool:
        if actual is None:
            return False

        if operator == PolicyOperator.GREATER_THAN:
            try:
                return actual > expected
            except TypeError:
                return False

        if operator == PolicyOperator.LESS_THAN:
            try:
                return actual < expected
            except TypeError:
                return False

        if operator == PolicyOperator.EQUALS:
            return actual == expected

        if operator == PolicyOperator.NOT_EQUALS:
            return actual != expected

        if operator == PolicyOperator.CONTAINS:
            try:
                return expected in actual
            except TypeError:
                return False

        return False

    @staticmethod
    def _get_recommended_decision(
        triggered_rules: list[TriggeredPolicy],
    ) -> PolicyDecisionTarget | None:
        if not triggered_rules:
            return None

        # Deterministic precedence:
        # BLOCK > HUMAN_REVIEW > ALLOW
        priority = {
            PolicyDecisionTarget.BLOCK: 3,
            PolicyDecisionTarget.HUMAN_REVIEW: 2,
            PolicyDecisionTarget.ALLOW: 1,
        }

        strongest_rule = max(
            triggered_rules,
            key=lambda rule: priority[rule.target_decision],
        )

        return strongest_rule.target_decision