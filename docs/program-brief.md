# AI Inference Infrastructure Lab - Program Brief

Owner: Edward Amartey
Status: Local CPU prototype
Last updated: October 7, 2026

## Problem and intended users

Developers evaluating model serving need a repeatable way to
run inference, validate requests, measure performance, and
understand the tradeoffs before moving to cloud infrastructure.

This project explores that workflow through a local prototype.
Developer needs below are hypotheses; customer interviews
and external user testing have not yet been conducted.

| Intended user | Hypothesized need | Planned validation |
|---|---|---|
| Application developer | Clear API contract and setup instructions | Ask a developer to run the service from a fresh checkout |
| ML practitioner | Identify the model and compare serving configurations | Review model metadata and reproducible benchmark results |
| Platform operator | Understand readiness, failures, and resource use | Test startup failures and collect operational measurements |

## Objective

Build a reproducible inference service and use measured
results to guide infrastructure decisions.

The current workload is sentiment classification using
DistilBERT on CPU. Generative AI, GPU execution, and
distributed deployment are future milestones.

## Scope

Current implementation:
- FastAPI service with health and prediction endpoints.
- Model loaded during application startup.
- Input validation and inference timing.
- Sequential and concurrent benchmark scripts.
- Raw concurrent request measurements saved as JSON.
- Hardware configuration and findings documented in README.

Planned:
- Fresh-environment setup verification.
- Automated API validation.
- Longer tests with varied inputs and resource measurements.
- Containerization and operational monitoring.
- Cloud deployment planning and a generative AI workload.

Outside the current milestone:
- Production customer traffic.
- Multi-tenant isolation.
- Distributed training or multi-node GPU orchestration.
- Production availability or capacity commitments.

## Requirements and acceptance criteria

| ID | Requirement | Acceptance evidence | Current status |
|---|---|---|---|
| R1 | Serve a pretrained model through an API | Valid request returns label, score, model, device, and inference time | Demonstrated locally |
| R2 | Reject invalid input | Empty, whitespace-only, missing, and overlength input return HTTP 422 | Empty input verified; remaining cases pending |
| R3 | Support reproducible setup | A fresh checkout installs dependencies and starts using documented commands | Pending |
| R4 | Preserve benchmark evidence | Reports include workload, concurrency, successes, failures, and request timings | Implemented for concurrent tests |
| R5 | Distinguish readiness from liveness | Readiness reflects model availability; startup failure is observable | Pending |
| R6 | Enable repeatable packaging | Container starts and passes the same API checks | Pending |
| R7 | Explain deployment decisions | Document resource needs, costs, risks, and rollback steps | Pending |

## Measurement approach

- Client latency: time from sending a request to reading its response.
- P95 latency: nearest-rank 95th percentile of successful request latencies.
- Throughput: successful requests divided by measured test duration.
- Failures: requests that raise an HTTP, timeout, parsing, or other client error.
- Resource use: CPU and memory measurements are planned.

Warm-up requests are excluded from measured results.
Latency and throughput are measured together with failures.
Passing API checks does not establish overall model accuracy.

Performance targets for a future pilot will be set after
validating the user workload and longer benchmark results.

## Evidence and decision

Three repeated runs tested 50 requests at each client
concurrency level: 1, 2, 4, and 8.

All 600 measured requests succeeded.

At concurrency four:
- Throughput ranged from 53.58 to 60.07 requests/sec.
- Per-run P95 latency ranged from 76.48 to 86.09 ms.

At concurrency eight:
- Throughput ranged from 45.58 to 59.79 requests/sec.
- Per-run P95 latency ranged from 147.18 to 220.85 ms.

Decision: investigate concurrency four as a candidate for
further testing. No server concurrency limit has been applied.

These short, fixed-input tests on one Windows machine do not
establish production capacity or identify the bottleneck.

## Roadmap and dependencies

| Milestone | Deliverable | Dependency | Exit condition |
|---|---|---|---|
| M1: Local baseline | API, benchmarks, and findings | Python environment and model download | Completed local demonstrations recorded |
| M2: Reproducibility | Setup guide and automated validation | M1 | Fresh checkout passes documented checks |
| M3: Operational evidence | Readiness, CPU/memory measurements, longer varied-input tests | M2 | Results support a documented operating decision |
| M4: Packaging | Container and rollback procedure | M2 and M3 | Container passes API and readiness checks |
| M5: Cloud evaluation | Deployment design and cost estimate | M4 | Resource choice and pilot criteria documented |
| M6: Generative AI extension | Text-generation service and workload-specific benchmarks | M5 planning | Model quality and serving performance evaluated |

## Risks and mitigations

| Risk | Potential impact | Mitigation or next action |
|---|---|---|
| Short fixed-input tests | Misleading capacity estimates | Test longer durations and varied input lengths |
| Client and API share one machine | Measurements include resource competition | Measure resources and later use a separate load client |
| Model download dependency | First startup may fail or be delayed | Document download behavior and test unavailable-model startup |
| Environment differences | Other developers may fail to reproduce results | Verify a fresh environment and containerize |
| Limited operational visibility | Failures may be hard to diagnose | Add readiness checks and structured operational logs |
| Sentiment model domain mismatch | Predictions may be unsuitable for other text | Evaluate representative labeled examples before claiming accuracy |
| Cloud resource cost | Unplanned expenditure during experiments | Estimate costs and define a budget before provisioning |

## Ownership and collaboration

Edward Amartey owns implementation, documentation, and
experiment execution for this individual portfolio project.

Future reviewer roles:
- Developer reviewer: test setup instructions and API usability.
- ML reviewer: review workload suitability and quality evaluation.
- Platform reviewer: review readiness, observability, and packaging.

These are proposed review roles, not an existing staffed team.

## Rollout and rollback criteria

Current release scope: local development only.

Before a container demonstration:
- Verify setup from a fresh environment.
- Pass valid and invalid request checks.
- Verify readiness and startup failure behavior.
- Save benchmark results with environment details.
- Record the tested commit and container image identifier.
- Demonstrate restarting the previous tested version.

Before a cloud pilot:
- Define representative workloads and measurable acceptance targets.
- Document authentication, access controls, resource sizing, and costs.
- Verify monitoring and rollback in the target environment.

Rollback approach:
Stop the candidate deployment and restart the previous tested
commit or image. Verify readiness and run API smoke checks.
The rollback procedure has not yet been implemented or tested.

## Evidence references

- [Project overview and results](../README.md)
- [Concurrent benchmark script](../benchmark_concurrent.py)
