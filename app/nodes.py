from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


@dataclass
class SqlPlan:
    sql: str
    filters: Dict[str, Any]
    tables: List[str]
    columns: List[str]


class TextToSqlAgent:
    """Simple, deterministic Text-to-SQL agent using a known schema.

    This mimics a LangChain-style agent by producing a structured plan that
    the orchestrator can execute.
    """

    def __init__(self, table_name: str, columns: List[str]) -> None:
        self.table_name = table_name
        self.columns = columns

    def plan(self, question: str) -> SqlPlan:
        text = normalize_text(question)
        filters: Dict[str, Any] = {}
        select_columns = [
            "nct_id",
            "study_title",
            "phase",
            "status",
            "condition",
            "enrollment",
            "start_date",
            "completion_date",
            "sponsor",
        ]

        if "phase" in text:
            for phase in ["phase 1", "phase 2", "phase 3", "phase 4"]:
                if phase in text:
                    filters["phase"] = phase.title()
                    break

        for status in ["recruiting", "completed", "active"]:
            if status in text:
                filters["status"] = status.title()
                break

        conditions = [
            "breast cancer",
            "type 2 diabetes",
            "melanoma",
            "hypertension",
            "influenza",
            "alzheimer's disease",
            "lung cancer",
            "depression",
            "obesity",
            "rheumatoid arthritis",
        ]
        for condition in conditions:
            if condition in text:
                filters["condition"] = condition.title()
                break

        if "sponsor" in text or "fund" in text:
            for sponsor in [
                "national cancer institute",
                "acme biotech",
                "university health network",
                "cardiotech inc",
                "global vaccines",
                "neuro pharma",
                "onco research",
                "behavioral health institute",
                "wellness labs",
                "arthritis foundation",
            ]:
                if sponsor in text:
                    filters["sponsor"] = sponsor.title()
                    break

        sql = f"SELECT {', '.join(select_columns)} FROM {self.table_name}"
        if filters:
            clauses = [f"{key} = :{key}" for key in filters]
            sql = f"{sql} WHERE {' AND '.join(clauses)}"
        sql = f"{sql} ORDER BY start_date DESC"

        return SqlPlan(
            sql=sql,
            filters=filters,
            tables=[self.table_name],
            columns=select_columns,
        )


class ClinOpsNode:
    """Operational node that formats trial operations insights."""

    def summarize(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not rows:
            return {
                "message": "No trials matched the filters.",
                "count": 0,
            }

        earliest = min(rows, key=lambda row: row["start_date"])
        latest = max(rows, key=lambda row: row["start_date"])
        return {
            "count": len(rows),
            "earliest_start": earliest["start_date"],
            "latest_start": latest["start_date"],
        }


class InsightGeneratorNode:
    """Generates lightweight insights for the response payload."""

    def summarize(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_phase: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        total_enrollment = 0

        for row in rows:
            by_phase[row["phase"]] = by_phase.get(row["phase"], 0) + 1
            by_status[row["status"]] = by_status.get(row["status"], 0) + 1
            total_enrollment += row["enrollment"]

        return {
            "by_phase": by_phase,
            "by_status": by_status,
            "total_enrollment": total_enrollment,
        }


class Orchestrator:
    """Coordinates agent planning and node execution."""

    def __init__(
        self,
        text_to_sql: TextToSqlAgent,
        clin_ops: ClinOpsNode,
        insight_generator: InsightGeneratorNode,
    ) -> None:
        self.text_to_sql = text_to_sql
        self.clin_ops = clin_ops
        self.insight_generator = insight_generator

    def run(self, question: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        plan = self.text_to_sql.plan(question)
        return {
            "plan": {
                "sql": plan.sql,
                "filters": plan.filters,
                "tables": plan.tables,
                "columns": plan.columns,
            },
            "clin_ops": self.clin_ops.summarize(rows),
            "insights": self.insight_generator.summarize(rows),
        }
