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

## Automated API validation
Run: .\.venv\Scripts\python.exe validate_api.py (with the API server running).
Verified October 7, 2026: 9/9 checks passed, covering health, prediction response fields, and invalid inputs. These checks verify API behavior, not overall model accuracy.

## Environment reproduction check

Verified October 7, 2026 on Windows with Python 3.13.3: created a new .venv-repro environment, installed requirements.txt using the PyTorch CPU package index, and confirmed pip check reported no broken requirements. Started the API using this environment and passed all 9 automated API checks.

Scope: tested on the same computer and repository using the existing model cache. A fresh clone, a separate machine, and an uncached model download have not yet been verified.

## Readiness checks

Verified October 8, 2026: all 10 automated API checks passed, including GET /ready returning HTTP 200 with model_loaded set to true.

A separate Python process called the readiness function without loading the model and verified status code 503 with {"status": "not_ready", "model_loaded": false}.

Scope: readiness checks whether the model object is present. It does not verify inference accuracy or available capacity. The API finishes loading the model before accepting requests, so the 503 case was tested directly rather than through a startup HTTP request.


## CPU and memory measurement

Measured October 8, 2026 using the local CPU inference API.

Benchmark results: [Saved JSON](results/concurrency_20261008T043823896625Z.json)

Each concurrency level attempted 50 requests after warm-up.

| Concurrent requests | Requests/second | Mean latency (ms) | p95 latency (ms) |
|---|---:|---:|---:|
| 1 | 33.32 | 29.87 | 42.16 |
| 2 | 45.98 | 43.01 | 53.39 |
| 4 | 48.91 | 80.05 | 97.34 |
| 8 | 52.81 | 146.64 | 176.79 |

### API process resource readings

Resource readings were collected using PowerShell Get-Process.

| Measurement | Idle sample | Benchmark window |
|---|---:|---:|
| Measurement duration (seconds) | 6.32 | 6.35 |
| CPU usage, with 100% representing one logical processor | 0.00% | 634.71% |
| Working set at the end of the measurement (MiB) | 238.08 | 256.93 |

CPU usage was calculated as the change in accumulated API process CPU time divided by elapsed wall-clock time, multiplied by 100.

### Interpretation and limitations

Increasing concurrency from 4 to 8 improved throughput by approximately 8%, while p95 latency increased by approximately 82%. This run demonstrates a throughput and response-time tradeoff.

Resource measurements cover the API process only. The benchmark window includes warm-up and all concurrency levels; CPU usage is an average across that window, not a reading for each concurrency level. Memory readings are snapshots, not peak memory measurements.

These short tests on one computer do not establish production capacity, sustained reliability, or a CPU bottleneck.

## Docker deployment

The CPU inference API was built and tested in a Linux Docker container
using Docker Desktop on Windows.

### Build and start

Run these commands from the project folder:

```powershell
docker build -t ai-inference-lab:v0.1 .
docker run -d --name ai-inference-api -p 127.0.0.1:8001:8000 ai-inference-lab:v0.1
docker logs -f ai-inference-api
```

Wait for `Application startup complete`.
Press Ctrl+C to exit the log view; the container keeps running.

The API is available at http://localhost:8001/docs.
The model downloads on first startup and is cached inside the container.
Creating a replacement container requires another download.

### Validate the container

```powershell
.\.venv-repro\Scripts\python.exe -c "import validate_api; validate_api.BASE_URL = 'http://127.0.0.1:8001'; validate_api.main()"
```

Verified on October 9, 2026: **10/10 checks passed**.

Checks cover health, readiness, positive and negative predictions,
response fields, and rejection of six invalid input cases.
They verify API behavior, not overall model accuracy or production capacity.

### Stop and restart

```powershell
docker stop ai-inference-api
docker start ai-inference-api
```

After restarting, wait for the model to load before sending requests.
### Restart validation

On October 9, 2026, the existing container was manually restarted with
`docker restart ai-inference-api`. After startup, `/ready` returned
`ready` with `model_loaded: true`, and all 10 API validation checks passed again.

This verifies functionality after a manual restart of the same container.
Crash recovery, replacement-container recovery, and recovery time were not measured.
### Manual rollback exercise

Verified on October 9, 2026:

1. Tagged the working image as `ai-inference-lab:rollback-v0.1`
   and confirmed its image ID matched `ai-inference-lab:v0.1`.
2. Simulated a startup configuration failure on port 8002 by overriding
   the launch command to reference `missing_module:app`.
3. Confirmed the candidate logged an import error and exited with code 3.
4. Started a new container, `ai-inference-rollback`, on port 8002
   using the verified rollback image and its default launch command.
5. Ran the API validation script against port 8002: **10/10 checks passed**.

This exercise verifies manual recovery from an invalid launch command.
The candidate and rollback used the same image; no application-version
rollback, automatic failover, traffic switching, or recovery-time
measurement was performed. The original API remained on port 8001.