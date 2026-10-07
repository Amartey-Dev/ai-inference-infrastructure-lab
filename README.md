## Local validation

The API serves a pretrained DistilBERT sentiment model on CPU.

| Test input | Expected result | Observed result |
|---|---|---|
| I really enjoyed this movie. | 200 / POSITIVE | Passed |
| This movie was terrible and boring. | 200 / NEGATIVE | Passed |
| Empty text | 422 validation error | Passed |

Sample inference times were 169.38 ms for the positive request
and 32.9 ms for the negative request. These are individual
measurements, not a performance benchmark.

Endpoints:
- GET /health: service health check
- POST /predict: sentiment prediction with model score and inference timing
- /docs: interactive API documentation