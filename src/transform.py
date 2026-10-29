
"""Flatten Vercel /v6/deployments list and add relative ages."""
from datetime import datetime, timezone


def _age(ms):
    if not ms:
        return ""
    try:
        created = datetime.fromtimestamp(int(ms) / 1000.0, tz=timezone.utc)
    except (ValueError, TypeError, OSError):
        return ""
    secs = int((datetime.now(timezone.utc) - created).total_seconds())
    if secs < 0:
        secs = 0
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{secs // 60}m"
    if secs < 86400:
        return f"{secs // 3600}h"
    return f"{secs // 86400}d"


def run(input):
    deps = input.get("deployments") or input.get("data") or []
    if isinstance(input, list):
        deps = input

    items = []
    for d in deps[:10]:
        meta = d.get("meta") or {}
        state = d.get("readyState") or d.get("state") or "—"
        target = d.get("target") or "preview"
        if target is None:
            target = "preview"
        msg = meta.get("githubCommitMessage") or meta.get("gitlabCommitMessage") or ""
        branch = meta.get("githubCommitRef") or meta.get("gitlabCommitRef") or ""
        items.append({
            "name": d.get("name") or "—",
            "state": state,
            "target": target,
            "branch": branch,
            "message": (msg or "")[:80],
            "age": _age(d.get("createdAt") or d.get("created")),
            "url": d.get("url") or "",
            "uid": d.get("uid") or "",
        })

    ready = sum(1 for i in items if i["state"] == "READY")
    errors = sum(1 for i in items if i["state"] == "ERROR")
    building = sum(1 for i in items if i["state"] in ("BUILDING", "QUEUED", "INITIALIZING"))

    return {
        "deployments": items,
        "count": len(items),
        "ready_count": ready,
        "error_count": errors,
        "building_count": building,
        "latest": items[0] if items else None,
    }
