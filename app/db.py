from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "clinical_trials.csv"
TABLE_NAME = "clinical_trials"


class TrialDatabase:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._load_seed_data()

    def _load_seed_data(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE clinical_trials (
                nct_id TEXT PRIMARY KEY,
                study_title TEXT,
                phase TEXT,
                status TEXT,
                condition TEXT,
                enrollment INTEGER,
                start_date TEXT,
                completion_date TEXT,
                sponsor TEXT
            )
            """
        )
        with DATA_PATH.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = [
                (
                    row["nct_id"],
                    row["study_title"],
                    row["phase"],
                    row["status"],
                    row["condition"],
                    int(row["enrollment"]),
                    row["start_date"],
                    row["completion_date"],
                    row["sponsor"],
                )
                for row in reader
            ]
        cursor.executemany(
            """
            INSERT INTO clinical_trials (
                nct_id, study_title, phase, status, condition, enrollment,
                start_date, completion_date, sponsor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.connection.commit()

    def query(self, sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        cursor = self.connection.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def schema(self) -> Dict[str, List[str]]:
        return {TABLE_NAME: [
            "nct_id",
            "study_title",
            "phase",
            "status",
            "condition",
            "enrollment",
            "start_date",
            "completion_date",
            "sponsor",
        ]}
