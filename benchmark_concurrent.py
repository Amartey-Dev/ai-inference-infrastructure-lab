import json
import math
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8000/predict"
REQUESTS_PER_TEST = 50
CONCURRENCY_LEVELS = [1, 2, 4, 8]
PAYLOAD = json.dumps(
    {"text": "I really enjoyed this movie."}
).encode("utf-8")


def send_request(request_id):
    request = Request(
        URL,
        data=PAYLOAD,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = perf_counter()

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read())

        return {
            "request_id": request_id,
            "success": True,
            "latency_ms": (perf_counter() - start) * 1000,
            "inference_ms": result["inference_ms"],
            "error": None,
        }
    except Exception as error:
        return {
            "request_id": request_id,
            "success": False,
            "latency_ms": (perf_counter() - start) * 1000,
            "inference_ms": None,
            "error": f"{type(error).__name__}: {error}",
        }


def run_test(concurrency):
    print(f"\nTesting up to {concurrency} concurrent requests...")

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        start = perf_counter()
        results = list(
            executor.map(send_request, range(REQUESTS_PER_TEST))
        )
        elapsed = perf_counter() - start

    successful = [item for item in results if item["success"]]
    latencies = sorted(item["latency_ms"] for item in successful)

    summary = {
        "concurrency": concurrency,
        "attempted": len(results),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "elapsed_seconds": round(elapsed, 3),
        "successful_requests_per_second": round(
            len(successful) / elapsed, 2
        ),
        "mean_latency_ms": (
            round(statistics.mean(latencies), 2)
            if latencies else None
        ),
        "p95_latency_ms": (
            round(latencies[math.ceil(0.95 * len(latencies)) - 1], 2)
            if latencies else None
        ),
    }

    print(json.dumps(summary, indent=2))
    return {"summary": summary, "requests": results}


def main():
    print("Sending 5 sequential warm-up requests...")
    for request_id in range(5):
        result = send_request(request_id)
        if not result["success"]:
            print(f"Warm-up failed: {result['error']}")
            print("Check that the API is running, then try again.")
            return

    tests = [run_test(level) for level in CONCURRENCY_LEVELS]

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "url": URL,
        "text": "I really enjoyed this movie.",
        "warmup_requests": 5,
        "requests_per_test": REQUESTS_PER_TEST,
        "latency_scope": "Successful requests only",
        "tests": tests,
    }

    output_folder = Path(__file__).resolve().parent / "results"
    output_folder.mkdir(exist_ok=True)
    filename = datetime.now(timezone.utc).strftime(
        "concurrency_%Y%m%dT%H%M%S%fZ.json"
    )
    output_path = output_folder / filename
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
    