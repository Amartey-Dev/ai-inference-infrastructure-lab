import json
import math
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8000"
MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"


def call_api(path, payload=None):
    data = (
        json.dumps(payload).encode("utf-8")
        if payload is not None else None
    )
    request = Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if data is not None else "GET",
    )

    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_health():
    status, body = call_api("/health")
    require(status == 200, f"Expected HTTP 200, got {status}")
    require(body == {"status": "ok"}, f"Unexpected response: {body}")


def check_prediction(text, expected_label):
    status, body = call_api("/predict", {"text": text})
    require(status == 200, f"Expected HTTP 200, got {status}")
    require(
        body.get("label") == expected_label,
        f"Expected {expected_label}, got {body.get('label')}",
    )
    require(body.get("model") == MODEL_ID, "Incorrect model identifier")
    require(body.get("device") == "cpu", "Expected CPU device")

    score = body.get("score")
    require(
        type(score) in (int, float)
        and math.isfinite(score)
        and 0 <= score <= 1,
        "Score must be a finite number between 0 and 1",
    )

    timing = body.get("inference_ms")
    require(
        type(timing) in (int, float)
        and math.isfinite(timing)
        and timing >= 0,
        "Inference time must be a finite, nonnegative number",
    )


def check_invalid(payload):
    status, body = call_api("/predict", payload)
    require(status == 422, f"Expected HTTP 422, got {status}")
    require(
        isinstance(body.get("detail"), list) and body["detail"],
        "Expected validation error details",
    )


def main():
    tests = [
        ("Health endpoint", check_health, ()),
        (
            "Positive prediction and response fields",
            check_prediction,
            ("I really enjoyed this movie.", "POSITIVE"),
        ),
        (
            "Negative prediction and response fields",
            check_prediction,
            ("This movie was terrible and boring.", "NEGATIVE"),
        ),
        ("Empty text rejected", check_invalid, ({"text": ""},)),
        ("Whitespace rejected", check_invalid, ({"text": "   "},)),
        ("Missing text rejected", check_invalid, ({},)),
        ("Overlength text rejected", check_invalid, ({"text": "a" * 2001},)),
        ("Null text rejected", check_invalid, ({"text": None},)),
        ("Numeric text rejected", check_invalid, ({"text": 123},)),
    ]

    passed = 0
    for name, test, arguments in tests:
        try:
            test(*arguments)
            print(f"PASS: {name}")
            passed += 1
        except Exception as error:
            print(f"FAIL: {name} - {type(error).__name__}: {error}")

    print(f"\nResults: {passed}/{len(tests)} checks passed")
    print("These checks verify API behavior, not overall model accuracy.")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())