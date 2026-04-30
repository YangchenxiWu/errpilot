# Error Bundle Schema

An error bundle is the compact handoff artifact ErrPilot will eventually produce
from a failed command. It should be readable by humans, stable enough for tests,
and safe to hand to an approved downstream coding agent.

This is a schema sketch, not a finalized contract.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ErrPilotErrorBundle",
  "type": "object",
  "required": ["schema_version", "run", "failure", "context", "handoff"],
  "properties": {
    "schema_version": {
      "type": "string",
      "examples": ["0.1"]
    },
    "run": {
      "type": "object",
      "required": ["run_id", "command", "cwd", "exit_code"],
      "properties": {
        "run_id": { "type": "string" },
        "command": {
          "type": "array",
          "items": { "type": "string" }
        },
        "cwd": { "type": "string" },
        "exit_code": { "type": "integer" },
        "started_at": { "type": "string", "format": "date-time" },
        "duration_ms": { "type": "integer", "minimum": 0 }
      }
    },
    "failure": {
      "type": "object",
      "properties": {
        "kind": { "type": "string" },
        "summary": { "type": "string" },
        "message": { "type": "string" },
        "stack": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "file": { "type": "string" },
              "line": { "type": "integer" },
              "function": { "type": "string" }
            }
          }
        }
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "files": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": { "type": "string" },
              "language": { "type": "string" },
              "excerpt": { "type": "string" },
              "redacted": { "type": "boolean" }
            }
          }
        },
        "stdout_tail": { "type": "string" },
        "stderr_tail": { "type": "string" }
      }
    },
    "triage": {
      "type": "object",
      "properties": {
        "severity": { "type": "integer", "minimum": 1, "maximum": 5 },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "reason": { "type": "string" }
      }
    },
    "handoff": {
      "type": "object",
      "properties": {
        "recommended_target": {
          "type": "string",
          "enum": ["codex", "aider", "gemini", "openhands"]
        },
        "requires_approval": { "type": "boolean" }
      }
    }
  }
}
```
