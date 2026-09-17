# Security Policy 🔒

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | ✅ fully supported |
| 2.0.x   | ⚠️ best effort     |
| < 2.0   | ❌ unsupported     |

## Reporting a vulnerability

**Please do not open a public issue for security reports.**

- Email the maintainers privately (see profile / Discussions for the current contact), including:
  - affected version(s) and module (e.g. `sanitizer`, `security`, `api`),
  - steps to reproduce or proof of concept,
  - impact assessment if known.
- You will receive an acknowledgment within **72 hours**.
- We will coordinate a fix and credit you (unless you prefer anonymity). Please allow up to **90 days** for coordinated disclosure before publishing details.

## Scope notes

PyLedger is a financial library: we treat these as security-relevant — authentication/authorization bypass, injection (XSS/SQLi/CSV formula), audit-trail tampering, idempotency/double-posting flaws, and PII leakage in logs/exports/PDFs.

## Hardening pointers

See `README.md → Security hardening checklist` (sanitizers, RBAC, `PersistentAuditTrail.verify_chain()`, PII masking).
