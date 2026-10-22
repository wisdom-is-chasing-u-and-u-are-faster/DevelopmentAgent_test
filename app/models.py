"""
app/models.py — Pydantic Data Models and RFC 7807 Problem Detail Envelopes.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# RFC 7807 Error Envelope
# ---------------------------------------------------------------------------
class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank", description="URI reference identifying the problem type")
    title: str = Field(..., description="Short, human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(default=None, description="URI reference identifying specific occurrence")

# ---------------------------------------------------------------------------
# Health Probe
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    database: str = "connected"

# ---------------------------------------------------------------------------
# Agent Models
# ---------------------------------------------------------------------------
class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., min_length=2, max_length=128)
    model: str = Field(..., min_length=2, max_length=128)
    system_prompt: Optional[str] = Field(default="")
    capabilities: Optional[List[str]] = Field(default_factory=list)

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    model: str
    system_prompt: Optional[str] = ""
    capabilities: List[str] = Field(default_factory=list)
    pass_rate: float = 0.0
    latency_p95: int = 0
    runs_evaluated: int = 0
    status: str = "active"
    created_at: str

class AgentListResponse(BaseModel):
    items: List[AgentResponse]
    total: int

# ---------------------------------------------------------------------------
# Dataset Models
# ---------------------------------------------------------------------------
class DatasetCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    domain: str = Field(..., min_length=2, max_length=128)
    test_count: Optional[int] = Field(default=0, ge=0)
    test_cases: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class DatasetResponse(BaseModel):
    id: str
    name: str
    domain: str
    test_count: int = 0
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str

class DatasetListResponse(BaseModel):
    items: List[DatasetResponse]
    total: int

# ---------------------------------------------------------------------------
# Run Models
# ---------------------------------------------------------------------------
class RunCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    mode: str = Field(..., min_length=2, max_length=64)
    agent_ids: List[str] = Field(..., min_length=1)
    dataset_id: str = Field(..., min_length=1)
    concurrency: Optional[int] = Field(default=1, ge=1, le=64)
    judge_model: Optional[str] = Field(default="gpt-4o")

class RunResponse(BaseModel):
    id: str
    name: str
    status: str
    mode: str
    agent_ids: List[str] = Field(default_factory=list)
    dataset_id: Optional[str] = None
    concurrency: int = 1
    judge_model: Optional[str] = "gpt-4o"
    pass_rate: float = 0.0
    judge_agreement: float = 0.0
    completed_steps: int = 0
    total_steps: int = 0
    created_at: str

class RunDetailResponse(BaseModel):
    id: str
    name: str
    status: str
    pass_rate: float
    judge_agreement: float
    completed_steps: int
    total_steps: int

class RunListResponse(BaseModel):
    items: List[RunResponse]
    total: int

# ---------------------------------------------------------------------------
# Trajectory Models
# ---------------------------------------------------------------------------
class TrajectoryResponse(BaseModel):
    id: str
    run_id: str
    agent_id: Optional[str] = None
    agent_name: str
    status: str
    turns: List[Dict[str, Any]] = Field(default_factory=list)
    a2a_cards: List[Dict[str, Any]] = Field(default_factory=list)
    judge_evaluation: Dict[str, Any] = Field(default_factory=dict)
    created_at: str

class TrajectoryDetailResponse(BaseModel):
    id: str
    run_id: str
    agent_name: str
    status: str
    turns: List[Dict[str, Any]] = Field(default_factory=list)
    a2a_cards: List[Dict[str, Any]] = Field(default_factory=list)
    judge_evaluation: Dict[str, Any] = Field(default_factory=dict)

class TrajectoryListResponse(BaseModel):
    items: List[TrajectoryResponse]
    total: int

# ---------------------------------------------------------------------------
# Annotation Models
# ---------------------------------------------------------------------------
class AnnotationCreateRequest(BaseModel):
    trajectory_id: str = Field(..., min_length=1)
    verdict: str = Field(..., min_length=2, max_length=64)
    taxonomy: str = Field(..., min_length=2, max_length=128)
    notes: Optional[str] = Field(default="")
    evaluator: str = Field(..., min_length=2, max_length=128)

class AnnotationResponse(BaseModel):
    id: str
    trajectory_id: str
    evaluator: str
    verdict: str
    taxonomy: str
    notes: Optional[str] = ""
    created_at: str

class AnnotationListResponse(BaseModel):
    items: List[AnnotationResponse]
    total: int

# ---------------------------------------------------------------------------
# Telemetry Models
# ---------------------------------------------------------------------------
class CollaborationTelemetryResponse(BaseModel):
    total_cards: int
    precision_rate: float
    avg_latency_ms: float
    consensus_rate: float
