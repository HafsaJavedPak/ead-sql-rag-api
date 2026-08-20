---
title: EAD SQL RAG API
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# EAD SQL RAG API

Authenticated, multi-user FastAPI backend for conversational text-to-SQL over
the Economic Affairs Division dataset. This Space runs the API container only
(`Dockerfile.spaces`). PostgreSQL (users, conversations, message history),
analytics MySQL, the LLM, and tracing are all external managed services
(Neon, Aiven, Groq, Langfuse Cloud) — see the deploy guide in the source
repository.

- API docs are disabled in this deployment (`APP_ENV=production`).
- `GET /health/live` and `GET /health/ready` report readiness.
- Full source and deployment walkthrough:
  https://github.com/YOUR_GITHUB_USERNAME/ead-sql-rag-api/blob/master/docs/deploy-huggingface-spaces.md

This `README.md` is specific to the Hugging Face Space (its YAML frontmatter
above is what tells Spaces to build `Dockerfile.spaces` and route to port
8000). It is a separate file from the project's own `README.md` in the
source repository, pushed only to this Space's git remote.
