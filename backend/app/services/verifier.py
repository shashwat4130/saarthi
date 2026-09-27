import json
from pathlib import Path
from time import perf_counter
from typing import Any

from app.models.manifest import ActionManifest
from app.models.verification import (
    Discrepancy,
    VerificationReport,
    VerificationStatus,
)


class GroundTruthVerifier:
    """
    Deterministic verifier that compares agent-provided claims
    against trusted mock data.

    Trusted data:
        agent/mock_data/customers.json
        agent/mock_data/accounts.json
        agent/mock_data/orders.json

    The verifier:
    - performs read-only JSON access
    - never modifies trusted data
    - never calls an LLM
    - never makes network requests
    - produces deterministic results
    """

    REQUIRED_REFUND_EVIDENCE = (
        "customer_id",
        "balance",
        "eligible_refund",
        "order_status",
    )

    def __init__(self, data_dir: str | Path | None = None) -> None:
        if data_dir is None:
            # backend/app/services/verifier.py
            #          ↑
            # parents[3] = saarthi/
            self.data_dir = (
                Path(__file__).resolve().parents[3]
                / "agent"
                / "mock_data"
            )
        else:
            self.data_dir = Path(data_dir)

        self.customers_file = self.data_dir / "customers.json"
        self.accounts_file = self.data_dir / "accounts.json"
        self.orders_file = self.data_dir / "orders.json"

    def verify(
        self,
        manifest: ActionManifest,
    ) -> VerificationReport:
        start = perf_counter()

        try:
            customers = self._load_json(self.customers_file)
            accounts = self._load_json(self.accounts_file)
            orders = self._load_json(self.orders_file)

            if manifest.action == "issue_refund":
                report = self._verify_refund(
                    manifest,
                    customers,
                    accounts,
                    orders,
                )
            else:
                report = self._verify_generic(
                    manifest,
                    customers,
                    accounts,
                    orders,
                )

            elapsed_ms = round(
                (perf_counter() - start) * 1000,
                3,
            )

            return report.model_copy(
                update={
                    "execution_time_ms": elapsed_ms,
                }
            )

        except Exception as exc:
            elapsed_ms = round(
                (perf_counter() - start) * 1000,
                3,
            )

            return VerificationReport(
                verified=False,
                status=VerificationStatus.ERROR,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="verifier",
                        agent_value=None,
                        trusted_value=None,
                        delta=None,
                        reason=f"Verification error: {exc}",
                    )
                ],
                execution_time_ms=elapsed_ms,
            )

    def _verify_refund(
        self,
        manifest: ActionManifest,
        customers: list[dict[str, Any]],
        accounts: list[dict[str, Any]],
        orders: list[dict[str, Any]],
    ) -> VerificationReport:

        arguments = manifest.arguments
        evidence = manifest.evidence

        customer_id = arguments.get("customer_id")
        order_id = arguments.get("order_id")
        requested_amount = arguments.get("amount")

        customer = self._find_by_id(
            customers,
            "customer_id",
            customer_id,
        )

        account = self._find_by_id(
            accounts,
            "customer_id",
            customer_id,
        )

        order = self._find_by_id(
            orders,
            "order_id",
            order_id,
        )

        checked_fields: list[str] = []
        discrepancies: list[Discrepancy] = []

        # -------------------------------------------------
        # Required trusted records
        # -------------------------------------------------

        if customer is None:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.ERROR,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="arguments.customer_id",
                        agent_value=customer_id,
                        trusted_value=None,
                        delta=None,
                        reason="Customer was not found in trusted data.",
                    )
                ],
            )

        if order is None:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.ERROR,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="arguments.order_id",
                        agent_value=order_id,
                        trusted_value=None,
                        delta=None,
                        reason="Order was not found in trusted data.",
                    )
                ],
            )

        if account is None:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.ERROR,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="account.customer_id",
                        agent_value=customer_id,
                        trusted_value=None,
                        delta=None,
                        reason="Account was not found in trusted data.",
                    )
                ],
            )

        # -------------------------------------------------
        # Required evidence
        # -------------------------------------------------

        missing_fields = [
            field
            for field in self.REQUIRED_REFUND_EVIDENCE
            if field not in evidence
        ]

        if missing_fields:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.MISSING_EVIDENCE,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field=f"evidence.{field}",
                        agent_value=None,
                        trusted_value=customer.get(field)
                        if field in customer
                        else order.get(field),
                        delta=None,
                        reason="Required evidence field is missing.",
                    )
                    for field in missing_fields
                ],
            )

        # -------------------------------------------------
        # Compare agent evidence with trusted state
        # -------------------------------------------------

        self._compare(
            field="customer_id",
            agent_value=evidence["customer_id"],
            trusted_value=customer["customer_id"],
            checked_fields=checked_fields,
            discrepancies=discrepancies,
        )

        self._compare(
            field="balance",
            agent_value=evidence["balance"],
            trusted_value=customer["balance"],
            checked_fields=checked_fields,
            discrepancies=discrepancies,
        )

        self._compare(
            field="eligible_refund",
            agent_value=evidence["eligible_refund"],
            trusted_value=customer["eligible_refund"],
            checked_fields=checked_fields,
            discrepancies=discrepancies,
        )

        self._compare(
            field="order_status",
            agent_value=evidence["order_status"],
            trusted_value=order["order_status"],
            checked_fields=checked_fields,
            discrepancies=discrepancies,
        )

        # -------------------------------------------------
        # Verify action against trusted constraints
        # -------------------------------------------------

        checked_fields.append("arguments.customer_id")
        if order["customer_id"] != customer_id:
            discrepancies.append(
                Discrepancy(
                    field="arguments.customer_id/order.customer_id",
                    agent_value=customer_id,
                    trusted_value=order["customer_id"],
                    delta=None,
                    reason="The order belongs to a different customer.",
                )
            )

        checked_fields.append("arguments.amount")
        if not isinstance(requested_amount, (int, float)):
            discrepancies.append(
                Discrepancy(
                    field="arguments.amount",
                    agent_value=requested_amount,
                    trusted_value="numeric",
                    delta=None,
                    reason="Refund amount must be numeric.",
                )
            )
        elif requested_amount <= 0:
            discrepancies.append(
                Discrepancy(
                    field="arguments.amount",
                    agent_value=requested_amount,
                    trusted_value="> 0",
                    delta=None,
                    reason="Refund amount must be greater than zero.",
                )
            )
        elif requested_amount > customer["eligible_refund"]:
            discrepancies.append(
                Discrepancy(
                    field="arguments.amount",
                    agent_value=requested_amount,
                    trusted_value=customer["eligible_refund"],
                    delta=float(
                        requested_amount
                        - customer["eligible_refund"]
                    ),
                    reason="Requested refund exceeds the trusted eligible refund amount.",
                )
            )

        checked_fields.append("account.authorization_status")
        if account["authorization_status"] != "AUTHORIZED":
            discrepancies.append(
                Discrepancy(
                    field="account.authorization_status",
                    agent_value=account["authorization_status"],
                    trusted_value="AUTHORIZED",
                    delta=None,
                    reason="Account is not authorized for the action.",
                )
            )

        checked_fields.append("order.order_status")
        if order["order_status"] != "DELIVERED":
            discrepancies.append(
                Discrepancy(
                    field="order.order_status",
                    agent_value=order["order_status"],
                    trusted_value="DELIVERED",
                    delta=None,
                    reason="Refund requires a delivered order.",
                )
            )

        status = (
            VerificationStatus.MATCH
            if not discrepancies
            else VerificationStatus.MISMATCH
        )

        return VerificationReport(
            verified=not discrepancies,
            status=status,
            checked_fields=checked_fields,
            discrepancies=discrepancies,
        )

    def _verify_generic(
        self,
        manifest: ActionManifest,
        customers: list[dict[str, Any]],
        accounts: list[dict[str, Any]],
        orders: list[dict[str, Any]],
    ) -> VerificationReport:
        """
        Generic fallback for actions that do not yet have
        an action-specific verification contract.
        """

        customer_id = manifest.arguments.get("customer_id")

        if customer_id is None:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.MISSING_EVIDENCE,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="arguments.customer_id",
                        agent_value=None,
                        trusted_value=None,
                        delta=None,
                        reason="Customer ID is required for verification.",
                    )
                ],
            )

        customer = self._find_by_id(
            customers,
            "customer_id",
            customer_id,
        )

        if customer is None:
            return VerificationReport(
                verified=False,
                status=VerificationStatus.ERROR,
                checked_fields=[],
                discrepancies=[
                    Discrepancy(
                        field="arguments.customer_id",
                        agent_value=customer_id,
                        trusted_value=None,
                        delta=None,
                        reason="Customer was not found in trusted data.",
                    )
                ],
            )

        return VerificationReport(
            verified=True,
            status=VerificationStatus.MATCH,
            checked_fields=["arguments.customer_id"],
            discrepancies=[],
        )

    @staticmethod
    def _compare(
        field: str,
        agent_value: Any,
        trusted_value: Any,
        checked_fields: list[str],
        discrepancies: list[Discrepancy],
    ) -> None:
        checked_fields.append(field)

        if agent_value == trusted_value:
            return

        delta = None

        if isinstance(agent_value, (int, float)) and isinstance(
            trusted_value,
            (int, float),
        ):
            delta = float(agent_value - trusted_value)

        discrepancies.append(
            Discrepancy(
                field=f"evidence.{field}",
                agent_value=agent_value,
                trusted_value=trusted_value,
                delta=delta,
                reason=(
                    f"Agent-provided {field} does not match "
                    "trusted ground truth."
                ),
            )
        )

    @staticmethod
    def _find_by_id(
        records: list[dict[str, Any]],
        key: str,
        value: Any,
    ) -> dict[str, Any] | None:
        for record in records:
            if record.get(key) == value:
                return record

        return None

    @staticmethod
    def _load_json(
        path: Path,
    ) -> list[dict[str, Any]]:
        if not path.exists():
            raise FileNotFoundError(
                f"Trusted data file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                f"Expected a JSON list in {path}"
            )

        return data