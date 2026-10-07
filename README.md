# AI Inference Infrastructure Lab

A hands-on project exploring model serving, input validation,
performance measurement, and infrastructure planning.

## Current implementation

- FastAPI service running locally on CPU.
- Pretrained DistilBERT model for sentiment classification.
- Model loaded once during application startup.
- Prediction responses include label, model score, and inference time.
- Input validation rejects empty text and limits input to 2,000 characters.
- Sequential benchmark script measures request latency and throughput.

This milestone serves a sentiment classification model.
Generative AI serving, GPU execution, and distributed deployment
are planned extensions.

## Endpoints

| Endpoint | Purpose |
|---|---|
| GET /health | Service health check |
| POST /predict | Sentiment prediction and inference timing |
| /docs | Interactive API documentation |

## Run locally

From the project folder in PowerShell, with dependencies installed:

    .\.venv\Scripts\python.exe -m uvicorn main:app

Open http://127.0.0.1:8000/docs to test the API.

The first startup downloads the pretrained model.

## Local validation

| Test input | Expected result | Observed result |
|---|---|---|
| I really enjoyed this movie. | 200 / POSITIVE | Passed |
| This movie was terrible and boring. | 200 / NEGATIVE | Passed |
| Empty text | 422 validation error | Passed |

These checks verify basic behavior, not overall model accuracy.

## Local CPU benchmark

Keep the API running and execute this in a second terminal:

    .\.venv\Scripts\python.exe benchmark.py

Method: 5 warm-up requests followed by 50 measured sequential
requests using the same sentence: "I really enjoyed this movie."
Warm-up requests are excluded from the results.

| Metric | Result |
|---|---:|
| Successful measured requests | 50/50 |
| Mean request latency | 26.58 ms |
| Median request latency | 22.29 ms |
| P95 request latency | 42.10 ms |
| Mean inference time | 20.87 ms |
| Sequential throughput | 37.55 requests/sec |

Request latency is measured by the client. Inference time is
measured inside the API around the classification pipeline.

These results represent one local Windows CPU run.
They do not establish concurrent-load capacity or production
performance. Hardware specifications and repeated runs are
needed for stronger comparisons.

## Planned milestones

- Record hardware specifications and benchmark results.
- Test concurrent requests and measure failures.
- Containerize the service.
- Add monitoring and readiness checks.
- Evaluate cloud deployment and CPU/GPU tradeoffs.
- Document requirements, risks, rollout criteria, and roadmap.
- Extend the lab to a generative AI workload.

## Benchmark environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| CPU | 12th Gen Intel Core i7-1265U |
| Physical cores | 10 |
| Logical processors | 12 |
| Reported RAM | 15.6 GiB |
| Inference device | CPU |
| Python | 3.13.3 |

The API and benchmark client ran on the same machine.
Package versions are recorded in requirements.txt.

## Concurrent CPU benchmark

Method: 5 sequential warm-up requests, followed by 50 measured
requests at each client concurrency level. All requests used
the same sentence. The API and client ran on the same machine.

| Client concurrency | Successful | Failed | Requests/sec | Mean latency (ms) | P95 latency (ms) |
|---|---:|---:|---:|---:|---:|
| 1 | 50 | 0 | 42.36 | 23.50 | 33.20 |
| 2 | 50 | 0 | 57.08 | 34.48 | 39.73 |
| 4 | 50 | 0 | 63.35 | 62.02 | 71.24 |
| 8 | 50 | 0 | 59.20 | 132.91 | 185.79 |

Four concurrent requests achieved the highest throughput in
this run. Increasing concurrency to eight reduced throughput
and increased latency. This suggests diminishing returns
under these test conditions; the bottleneck has not been isolated.

These are short local tests, not production capacity estimates.
Latency statistics include successful requests only.
Individual request measurements are saved in the results folder.

Run the benchmark with:

    .\.venv\Scripts\python.exe benchmark_concurrent.py

Next: repeat measurements and investigate CPU utilization
before selecting a concurrency limit.

## Repeated concurrency tests

Three additional runs measured 50 requests at each concurrency
level: 600 measured requests succeeded, with zero failures.

| Concurrency | Throughput range (requests/sec) | P95 latency range (ms) |
|---|---:|---:|
| 1 | 34.04-39.18 | 36.56-39.38 |
| 2 | 45.27-48.09 | 46.20-59.48 |
| 4 | 53.58-60.07 | 76.48-86.09 |
| 8 | 45.58-59.79 | 147.18-220.85 |

Ranges show the minimum and maximum per-run results.
Eight concurrent requests had higher P95 latency than four
in every run, while its throughput advantage varied.

Decision: investigate concurrency four as a candidate for
further testing. No server concurrency limit has been applied.
Longer tests, varied inputs, and CPU measurements are needed
before setting an operating limit.
