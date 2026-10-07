import json
import math
import statistics
from time import perf_counter
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8000/predict"
PAYLOAD = json.dumps(
    {"text": "I really enjoyed this movie."}
).encode("utf-8")


def send_request():
    request = Request(
        URL,
        data=PAYLOAD,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = perf_counter()
    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read())

    latency_ms = (perf_counter() - start) * 1000
    return latency_ms, result["inference_ms"]


print("Sending 5 warm-up requests...")
for _ in range(5):
    send_request()

print("Measuring 50 sequential requests...")
latencies = []
inference_times = []
start = perf_counter()

for _ in range(50):
    latency, inference = send_request()
    latencies.append(latency)
    inference_times.append(inference)

elapsed = perf_counter() - start
ordered = sorted(latencies)
p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]

print(f"Successful requests: {len(latencies)}")
print(f"Mean request latency: {statistics.mean(latencies):.2f} ms")
print(f"Median request latency: {statistics.median(latencies):.2f} ms")
print(f"P95 request latency: {p95:.2f} ms")
print(f"Mean inference time: {statistics.mean(inference_times):.2f} ms")
print(f"Sequential throughput: {len(latencies) / elapsed:.2f} requests/sec")