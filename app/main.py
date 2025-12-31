from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.db import TABLE_NAME, TrialDatabase
from app.nodes import ClinOpsNode, InsightGeneratorNode, Orchestrator, TextToSqlAgent

app = FastAPI(title="Clinical Trials LangChain Orchestrator")

database = TrialDatabase()

text_to_sql = TextToSqlAgent(TABLE_NAME, database.schema()[TABLE_NAME])
clin_ops = ClinOpsNode()
insight_generator = InsightGeneratorNode()
orchestrator = Orchestrator(text_to_sql, clin_ops, insight_generator)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    plan: dict
    results: list
    clin_ops: dict
    insights: dict


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query_trials(request: QueryRequest) -> QueryResponse:
    plan = text_to_sql.plan(request.question)
    rows = database.query(plan.sql, plan.filters)
    orchestration = orchestrator.run(request.question, rows)
    return QueryResponse(
        question=request.question,
        plan=orchestration["plan"],
        results=rows,
        clin_ops=orchestration["clin_ops"],
        insights=orchestration["insights"],
    )
