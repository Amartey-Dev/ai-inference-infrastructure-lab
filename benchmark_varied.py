import json
import math
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from itertools import count
from pathlib import Path
from threading import Lock
from time import perf_counter
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8003"
DURATION_SECONDS = 60
CONCURRENCY = 4

INPUTS = [
    {"name": "short", "text": "I really enjoyed this movie."},
    {
        "name": "medium",
        "text": (
            "The service was helpful and the instructions were clear. "
            "However, the response sometimes took longer than expected. "
        ) * 4,
    },
    {
        "name": "long",
        "text": (
            "The application completed my request successfully. "
            "I appreciated the clear instructions, although waiting "
            "for a response was sometimes frustrating. "
        ) * 12,
    },
]


def send_request(request_id, sample):
    request = Request(
        BASE_URL + "/predict",
        data=json.dumps({"text": sample["text"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = perf_counter()
    record = {
        "request_id": request_id,
        "input_name": sample["name"],
        "characters": len(sample["text"]),
        "success": False,
        "inference_ms": None,
        "error": None,
    }

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read())

        inference_ms = result["inference_ms"]
        if (
            not isinstance(inference_ms, (int, float))
            or isinstance(inference_ms, bool)
            or not math.isfinite(inference_ms)
            or inference_ms < 0
        ):
            raise ValueError("Invalid inference_ms in response")

        record["success"] = True
        record["inference_ms"] = inference_ms
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"

    record["latency_ms"] = (perf_counter() - start) * 1000
    return record


def summarize(records):
    successful = [item for item in records if item["success"]]
    latencies = sorted(item["latency_ms"] for item in successful)
    return {
        "attempted": len(records),
        "successful": len(successful),
        "failed": len(records) - len(successful),
        "mean_latency_ms": (
            round(statistics.mean(latencies), 2) if latencies else None
        ),
        "p95_latency_ms": (
            round(latencies[math.ceil(0.95 * len(latencies)) - 1], 2)
            if latencies else None
        ),
    }


def main():
    if any(not 1 <= len(item["text"]) <= 2000 for item in INPUTS):
        raise ValueError("Every input must contain 1 to 2000 characters")

    print("Sending 9 sequential warm-up requests...")
    for request_id in range(9):
        result = send_request(request_id, INPUTS[request_id % 3])
        if not result["success"]:
            raise SystemExit(f"Warm-up failed: {result['error']}")

    request_ids = count()
    lock = Lock()

    def worker(deadline):
        records = []
        while True:
            with lock:
                if perf_counter() >= deadline:
                    break
                request_id = next(request_ids)
            sample = INPUTS[request_id % len(INPUTS)]
            records.append(send_request(request_id, sample))
        return records

    timestamp = datetime.now(timezone.utc)
    print(f"Running {DURATION_SECONDS} seconds at concurrency {CONCURRENCY}...")
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        start = perf_counter()
        deadline = start + DURATION_SECONDS
        futures = [executor.submit(worker, deadline) for _ in range(CONCURRENCY)]
        records = [item for future in futures for item in future.result()]
        elapsed = perf_counter() - start

    records.sort(key=lambda item: item["request_id"])
    summary = summarize(records)
    summary["elapsed_seconds_including_drain"] = round(elapsed, 3)
    summary["successful_requests_per_second"] = round(
        summary["successful"] / elapsed, 2
    )
    by_input = {
        sample["name"]: summarize(
            [item for item in records if item["input_name"] == sample["name"]]
        )
        for sample in INPUTS
    }

    report = {
        "timestamp_utc": timestamp.isoformat(),
        "base_url": BASE_URL,
        "target_duration_seconds": DURATION_SECONDS,
        "concurrency": CONCURRENCY,
        "warmup_requests_excluded": 9,
        "inputs": INPUTS,
        "method": "Workers send another request after each response; no retries.",
        "latency_scope": "Successful requests only; client round-trip latency.",
        "limitations": (
            "Synthetic workload on one computer; not an accuracy evaluation "
            "or production capacity estimate. Character counts are not token "
            "counts. The API truncates model input to 512 tokens."
        ),
        "summary": summary,
        "by_input": by_input,
        "requests": records,
    }

    output_folder = Path(__file__).resolve().parent / "results"
    output_folder.mkdir(exist_ok=True)
    output_path = output_folder / timestamp.strftime(
        "varied_%Y%m%dT%H%M%S%fZ.json"
    )
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({"summary": summary, "by_input": by_input}, indent=2))
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()