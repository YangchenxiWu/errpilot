"""Typed failures for fail-closed synthetic harness gates."""


class HarnessError(Exception):
    """Base class for harness failures."""


class CaseSpecError(HarnessError):
    """The machine-readable case specification is invalid or incomplete."""


class ProvenanceMismatch(HarnessError):
    """RAW evidence and the ErrPilot handoff do not share one source execution."""


class WorkspaceAccessError(HarnessError):
    """A synthetic adapter attempted to leave its ordinary workspace view."""


class AgentFailure(HarnessError):
    """A deterministic synthetic adapter simulates an attributable agent failure."""


class ArtifactCollision(HarnessError):
    """A run attempted to reuse an existing workspace or evidence directory."""
