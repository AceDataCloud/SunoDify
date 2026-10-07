"""Fixed Ace Data Cloud APIs; submission is never retried automatically."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urlsplit

import requests

SERVICE = {
    "family": "suno",
    "prefix": "/suno",
    "media": "audio",
    "default": "chirp-v6",
    "models": ["chirp-v6", "chirp-v6-wild", "chirp-v6-mini", "chirp-v5-5", "chirp-v5"],
}
BASE = "https://api.acedata.cloud"
TERMINAL_FAILURES = {"failed", "error", "cancelled", "canceled", "rejected"}
TERMINAL_SUCCESS = {"complete", "completed", "succeeded", "succeed", "success", "finished"}


class AceDataSunoError(RuntimeError):
    pass


def integer(value: Any, field: str, low: int, high: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer.")
    try:
        number = int(value)
        if float(value) != number or not low <= number <= high:
            raise ValueError
        return number
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"{field} must be an integer from {low} to {high}.") from None


def https_urls(value: Any, required: bool = False) -> list[str]:
    if not value:
        if required:
            raise ValueError("At least one reference image URL is required.")
        return []
    if isinstance(value, str):
        value = json.loads(value) if value.strip().startswith("[") else value.splitlines()
    if not isinstance(value, list) or not 1 <= len(value) <= 16:
        raise ValueError("Provide 1–16 public HTTPS image URLs.")
    result = []
    for url in value:
        if not isinstance(url, str):
            raise ValueError("Each reference must be a public HTTPS URL.")
        url = url.strip()
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Each reference must be a public HTTPS URL without user credentials.")
        result.append(url)
    return result


def required_text(params: dict[str, Any], name: str) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required.")
    return value.strip()


def choice(params: dict[str, Any], name: str, allowed: list[str], default: str) -> str:
    value = params.get(name) or default
    if value not in allowed:
        raise ValueError(f"Unsupported {name} value.")
    return value


def safe_result(value: Any) -> Any:
    """Return output fields, excluding saved request, identity and routing metadata."""
    fields = {
        "data",
        "content",
        "success",
        "id",
        "task_id",
        "trace_id",
        "state",
        "status",
        "model",
        "image_url",
        "audio_url",
        "video_url",
        "last_frame_url",
        "url",
        "title",
        "lyric",
        "duration",
        "width",
        "height",
        "created",
        "format",
        "items",
        "_id",
        "languages",
        "tags",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "usage",
    }
    if isinstance(value, dict):
        return {k: safe_result(v) for k, v in value.items() if k in fields}
    if isinstance(value, list):
        return [safe_result(v) for v in value]
    return value


def media_urls(value: Any) -> list[str]:
    urls = []
    keys = {"image": {"url", "image_url"}, "audio": {"audio_url"}, "video": {"video_url"}}[
        SERVICE["media"]
    ]

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in keys and isinstance(v, str) and v.startswith("https://"):
                    urls.append(v)
                elif k in {"data", "content"}:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(value)
    return list(dict.fromkeys(urls))


class AceDataSunoClient:
    def __init__(self, bearer_token: str) -> None:
        key = bearer_token
        if not isinstance(key, str) or not key.strip():
            raise ValueError("An Ace Data Cloud API key is required.")
        self.key = key.strip().removeprefix("Bearer ").strip()
        if not self.key:
            raise ValueError("An Ace Data Cloud API key is required.")

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        model_header: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        if model_header:
            headers["model"] = model_header
        try:
            with requests.request(
                method,
                BASE + path,
                headers=headers,
                json=payload,
                params=query,
                timeout=(10, 60),
                allow_redirects=False,
            ) as response:
                if response.status_code != 200:
                    hints = {
                        400: "Check inputs and model access.",
                        401: "Check the API key.",
                        403: "Check permissions and content restrictions.",
                        429: "Rate limited; wait before trying again.",
                    }
                    raise AceDataSunoError(
                        f"Ace Data Cloud HTTP {response.status_code}. "
                        + hints.get(
                            response.status_code,
                            "Service unavailable. Check request history before resubmitting.",
                        )
                    )
                body = response.json()
        except requests.RequestException:
            raise AceDataSunoError(
                "Connection failed. Do not resubmit blindly; check request history for an accepted task."
            ) from None
        except ValueError:
            raise AceDataSunoError("The API returned an invalid JSON response.") from None
        if not isinstance(body, dict):
            raise AceDataSunoError("The API returned an invalid result.")
        if body.get("success") is False or body.get("error"):
            raise AceDataSunoError(
                "The API reported a failure. Check the request in the Ace Data Cloud console."
            )
        return body

    def validate(self) -> None:
        self.request(
            "POST",
            SERVICE["prefix"] + "/tasks",
            {"action": "retrieve", "id": "00000000-0000-0000-0000-000000000000"},
        )

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        if action == "task":
            task_id = required_text(params, "task_id")
            wait = integer(params.get("wait_seconds", 0), "wait_seconds", 0, 240)
            deadline = time.monotonic() + wait
            while True:
                body = self.request(
                    "POST", SERVICE["prefix"] + "/tasks", {"action": "retrieve", "id": task_id}
                )
                result = self.normalise(body, task_id, retrieved=True)
                if result["status"] != "pending" or time.monotonic() >= deadline:
                    return result
                time.sleep(min(5, max(0, deadline - time.monotonic())))
        if action not in {"generate", "edit"}:
            raise ValueError("Unsupported operation.")
        payload, path, model_header = self.payload(action, params)
        body = self.request("POST", path, payload, model_header=model_header)
        return self.normalise(body, str(body.get("task_id") or body.get("id") or ""))

    def payload(self, action: str, p: dict[str, Any]) -> tuple[dict[str, Any], str, str | None]:
        model = choice(p, "model", SERVICE["models"], SERVICE["default"])
        data = {"model": model, "async": True}
        header = None
        data.update(
            action="generate",
            custom=bool(p.get("custom", False)),
            instrumental=bool(p.get("instrumental", False)),
        )
        if data["custom"]:
            data["style"] = required_text(p, "style")
            if not data["instrumental"]:
                data["lyric"] = required_text(p, "lyric")
        else:
            data["prompt"] = required_text(p, "prompt")
        for name in ["title", "style", "lyric"]:
            if p.get(name):
                data[name] = p[name]
        data["duration"] = integer(p.get("duration", 30), "duration", 10, 360)
        path = "/suno/audios"
        return (data, path, header)

    def normalise(
        self, body: dict[str, Any], task_id: str, retrieved: bool = False
    ) -> dict[str, Any]:
        if retrieved and (not body):
            return {"status": "pending", "task_id": task_id, "media_urls": [], "result": {}}
        result = body.get("response") if retrieved else body
        if not isinstance(result, dict):
            return {"status": "pending", "task_id": task_id, "media_urls": [], "result": {}}
        data = result.get("data")
        states = [str(result[k]).lower() for k in ["state", "status"] if result.get(k)]
        if isinstance(data, dict):
            states += [str(data[k]).lower() for k in ["state", "status"] if data.get(k)]
        if isinstance(data, list):
            states += [
                str(item[k]).lower()
                for item in data
                if isinstance(item, dict)
                for k in ["state", "status"]
                if item.get(k)
            ]
        if (
            result.get("success") is False
            or result.get("error")
            or any((s in TERMINAL_FAILURES for s in states))
        ):
            raise AceDataSunoError(
                f"Generation failed for task {task_id}. Check the console for details."
            )
        urls = media_urls(result)
        done = bool(urls) and (not states or all((s in TERMINAL_SUCCESS for s in states)))
        done = bool(urls) and (
            all((s in TERMINAL_SUCCESS for s in states))
            if states
            else bool(body.get("finished_at"))
        )
        if not task_id and (not done):
            raise AceDataSunoError(
                "No task ID or completed media returned; check request history before resubmitting."
            )
        return {
            "status": "succeeded" if done else "pending",
            "task_id": task_id,
            "media_urls": urls if done else [],
            "result": safe_result(result),
        }
