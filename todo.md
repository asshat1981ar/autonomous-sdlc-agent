# Codebase Analysis TODO List

## File: app.py

### Overview
Main application entry point for the orchestrator system. Handles both API and CLI modes.

### Key Findings
- [IMPROVEMENT] Environment variable "AI_MODE" has no default value documentation (Line 7)
- [REFACTOR] Metrics server port is hardcoded (8001) (Line 11)
- [DOCS] Missing docstring for AgentRegistry usage (Line 14)
- [TEST] No test coverage for CLI mode branch (Line 19)
- [IMPROVEMENT] API host/port could be configurable (Line 21)

### Recommendations
- Add configuration file support for ports/hosts
- Document environment variables
- Add CLI mode tests
- Consider dependency injection for registry/metrics
- Priority: Medium

---
## File: components/OrchestratorDashboard.tsx

### Overview
Main dashboard component for task orchestration and monitoring.

### Key Findings
- [IMPROVEMENT] Uses mock data (sampleTasks) instead of real API calls (Line 13)
- [TEST] Missing test coverage for retry/reroute functionality (Line 33, 43)
- [PERF] No memoization of task list components (Line 62)
- [UI] No loading/error states for API calls (Line 20)
- [TYPES] Task interface could be shared/common type (Line 4)

### Recommendations
- Implement real API integration
- Add loading/error states
- Create shared types file
- Add component tests
- Consider virtualization for large task lists
- Priority: High

---
## File: components/SystemPromptEditor.tsx

### Overview
Component for editing and managing the system prompt used for AI interactions.

### Key Findings
- [SECURITY] Uses localStorage without validation (Line 7)
- [IMPROVEMENT] No debounce on auto-save (Line 19)
- [TEST] Missing test coverage for error states (Line 11)
- [UI] Alert() used for confirmation (Line 15)
- [PERF] Unnecessary localStorage write on every change (Line 19)

### Recommendations
- Add input sanitization
- Implement proper toast notifications
- Add debounce for auto-save
- Consider context/API for prompt storage
- Add character limit validation
- Priority: Medium

---
## File: src/routes/api_routes.ts

### Overview
Express router defining API endpoints for task management, agent registry, knowledge graph, system utilities, and authentication.

### Key Findings
- [TODO] Many endpoints return "Not Implemented" status (501), indicating incomplete functionality.
- [SECURITY] Auth middleware is a placeholder and does not enforce authentication.
- [IMPROVEMENT] Tenant ID extraction is basic; consider validation and error handling.
- [REFACTOR] Error handling is repetitive; could be abstracted.
- [TEST] No tests found for API routes.
- [DOCS] Missing API documentation for endpoints.
- [PERF] No rate limiting or throttling on endpoints.

### Recommendations
- Implement missing endpoint logic.
- Replace placeholder auth middleware with real authentication.
- Add validation and error handling for tenant ID.
- Refactor error handling to middleware.
- Add comprehensive API tests.
- Add API documentation (Swagger/OpenAPI).
- Implement rate limiting.
- Priority: High

---
