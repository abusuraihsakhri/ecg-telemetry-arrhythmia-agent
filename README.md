# ECG Telemetry Arrhythmia Agent

### [Open the Live Application →](https://abusuraihsakhri.github.io/ecg-telemetry-arrhythmia-agent/)

This repository contains **experimental, rule-based Python evaluation utilities** and a static browser demonstration. They accept synthetic numeric metrics and flags; they **do not ingest ECG waveforms** or detect actual cardiac arrhythmias. The current thresholds are demonstration constants, **not validated clinical cutoffs**.

**Not for diagnosis, clinical alarm routing, or patient care.** No accuracy, sensitivity, specificity, regulatory approval, HIPAA compliance, or clinical validation is established.

## Browser demonstration

Open [`web/index.html`](web/index.html) locally in a modern browser. Select **Local browser demo** (default), enter synthetic inputs, evaluate the three rules and optionally export the JSON report. The local mode requires no server, dependencies, or network access and produces **no HMAC signature**.

The interface also offers **Connected API** mode for an application independently hosted at the same origin with a `POST /api/audit` endpoint. The static GitHub Pages version uses local mode by default. API mode will report connection errors instead of fabricating responses.

The browser rules follow the separate generic-worker demonstration: primary metric >25; secondary metric >12 or the synthetic critical flag; selected status-descriptor keywords. Metrics have arbitrary units. This is **not** equivalent to the independent `tele_pulse.py` or package-coordinator rules, which currently use different thresholds.

## Python setup

Requires Python 3.9 or later.

```bash
python -m pip install -e ".[server,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python -m pytest -q
```

The signing key is required for imports and runs using the **generic** `agents/` pipeline. A new random key is appropriate for local tests. A production audit deployment would additionally require persistent key management and tamper-resistant log storage, which are **not** implemented here.

## Existing command-line workflows

Three separate entry points exist; they have different input schemas and rules:

```bash
# Generic Pydantic workers with in-process HMAC audit log
python cli.py audit --task-id DEMO-001 --target SYNTH-001 --primary 28 --secondary 13
python cli.py verify-audit

# Standalone TelePulse demonstration
python tele_pulse.py audit --case-id SYNTH-001 --primary 24 --secondary 14
python tele_pulse.py batch -i sample.csv -o results.csv

# Installable package coordinator
python -m ecg_telemetry_arrhythmia_agent.cli audit --case-id SYNTH-001
ecg-telemetry-arrhythmia-agent audit --case-id SYNTH-001
```

The `python cli.py batch -i ... -o ...` and package CLI batch modes accept CSV, report invalid rows, and export summary columns. Outputs from the three implementations are **not interchangeable**.

## REST API

For **local, synthetic-data testing only**:

```bash
uvicorn agents.api:app --host 127.0.0.1 --port 8000
# or use the package-specific app:
uvicorn ecg_telemetry_arrhythmia_agent.server:create_app --factory --host 127.0.0.1 --port 8000
```

The generic API exposes `GET /health`, `GET /metrics` (JSON counters), `POST /api/audit`, `POST /api/chat` (mock response), and `GET /api/audit/logs`. Use `/docs` for its generated OpenAPI reference. Neither API includes authentication or access controls. Do **not** expose them on an untrusted network or submit identifiable health data. `agents.base.PHIGuard` is a limited pattern-based filter, **not** comprehensive de-identification.

### Audit trail scope

The generic pipeline signs audit-entry metadata and payload hashes using HMAC-SHA256 and now verifies the signatures and hash-chain links. Logs reside in process memory; they are **not persistent, append-only, or tamper-proof**. Restarting the process loses the audit log. Neither the static browser demo nor the other two Python pipelines provide this HMAC audit mechanism.

## Deployment and testing

```bash
python -m pytest -q
python -m compileall -q agents ecg_telemetry_arrhythmia_agent
docker compose up --build
```

The Docker image runs the generic API on container port 8000. Docker Compose needs `AUDIT_SECRET_KEY` set in a local `.env` file (see `.env.example`). The browser is a separate static application under `web/`, not automatically served by the API. GitHub Actions runs Python tests and browser JavaScript syntax checks, with a separate workflow configured to publish `web/` to GitHub Pages. Deployment requires successful GitHub Pages setup and is not evidence of medical readiness.

No external font, script, or JavaScript package is required by the browser demo. It uses modern browser features (Fetch, Blob download, and standard DOM APIs).

## Limitations

The codebase retains several historical, partly overlapping implementations for compatibility. The `enrichment.py` suite and generic worker labels are rule prototypes, not validated cardiac electrophysiology algorithms. The `agents.llm_factory` implementation returns a deterministic mock for every configured provider; no actual external or local language-model integration is provided. No real-time physiological waveform ingestion, QTc estimation, AF-burden estimation, or ECG annotation pipeline is implemented.

## License

MIT. See [LICENSE](LICENSE).
