# Agent Development Guide

## Build/Test Commands
- **Frontend**: `npm run dev` (development), `npm run build` (production), `npm run preview` (preview)
- **Backend**: `python3 main.py` (development), `python3 -m pytest` (tests)
- **Full Stack**: Start backend (`python3 main.py`) then frontend (`npm run dev`)

## Architecture Overview
- **Frontend**: React 19 + Vite + TypeScript, single-page app with multi-agent collaboration UI
- **Backend**: Flask + SQLAlchemy + SQLite, RESTful API with async AI orchestration
- **AI Integration**: Multi-provider support (Gemini, Claude, OpenAI, Blackbox) with 5 collaboration paradigms
- **Database**: SQLite with Agent, Session, Task, and Collaboration models
- **Key Services**: AI providers orchestration, bridge services, GitHub integration, project state management

## Code Style Guidelines
- **Python**: Use type hints, async/await patterns, proper error handling with try/except
- **TypeScript**: Strict typing, interface definitions, functional React components with hooks
- **Imports**: Relative imports with `.ts` extensions for TypeScript, absolute imports for Python modules
- **Naming**: camelCase for TypeScript, snake_case for Python, PascalCase for React components
- **Error Handling**: Comprehensive error catching with user-friendly messages
- **File Structure**: Component-based organization, services layer for business logic
- **API**: RESTful endpoints with `/api` prefix, consistent JSON response format with success/error fields
