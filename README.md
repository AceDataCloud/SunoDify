# Suno for Dify

Use the Ace Data Cloud Suno APIs in Dify workflows. Maintained by Ace Data Cloud. The plugin is free; API calls require your own authorized account and use the current service pricing.

## Setup

1. Activate the service at [Ace Data Cloud](https://platform.acedata.cloud/console/applications), check [current pricing](https://platform.acedata.cloud/models), and create an API token with the required service access.
2. Install from [Dify Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/suno). This version is published and was installed through the official Marketplace flow in Dify CE 1.17.1 with signature verification enabled. Installation is optional; this does not mean Dify preinstalls the plugin.
3. In Dify's **Plugins / Tools** page, authorize this provider with **Bearer Token** (`acedata_bearer_token`). Do not include credentials in prompts or exported workflows. Credential validation never generates media. Authorization performs a read-only task query.

## Tools

| Tool | API |
|---|---|
| `suno_generate_audios` | `POST /suno/audios` |
| `suno_generate_lyrics` | `POST /suno/lyrics` |
| `suno_upload_reference_audio` | `POST /suno/upload` |
| `suno_get_mp4` | `POST /suno/mp4` |
| `suno_get_mp3` | `POST /suno/mp3` |
| `suno_get_wav` | `POST /suno/wav` |
| `suno_get_midi` | `POST /suno/midi` |
| `suno_get_timing` | `POST /suno/timing` |
| `suno_create_vox_audio` | `POST /suno/vox` |
| `suno_enhance_style` | `POST /suno/style` |
| `suno_mashup_lyrics` | `POST /suno/mashup-lyrics` |
| `suno_create_voice` | `POST /suno/voices` |
| `suno_create_persona` | `POST /suno/persona` |
| `suno_list_personas` | `GET /suno/persona` |
| `suno_delete_persona` | `DELETE /suno/persona` |
| `suno_custom_models` | `POST /suno/custom-models` |
| `suno_projects` | `POST /suno/projects` |
| `suno_task_retrieve` | `POST /suno/tasks` |
| `suno_tasks_retrieve_batch` | `POST /suno/tasks` |

See [CAPABILITIES.md](CAPABILITIES.md) for the current MCP comparison and parameter equivalents. All exposed inputs follow the current published API; model combinations and availability still depend on the service.

## Run a workflow

For generation, use **Start → generation tool → task retrieval → Output**. Fill the prompt/text and model, and enter arrays/objects as JSON. Optional values can be left empty. The example requests in [tests/contract-examples.json](https://github.com/AceDataCloud/SunoDify/blob/main/tests/contract-examples.json) show valid shapes; example.org URLs are placeholders that must be replaced with your own accessible media.

A submission can return `status=pending` with `task_id`. Save that ID, then use the retrieval tool with `wait_seconds=0` to read once, or 1–240 for a bounded wait. If still pending, query the same task again. Disable automatic retries on generation nodes. No paid request is automatically retried and no substitute model is selected.

`status`, `success`, `task_id`, `trace_id`, `media_urls`, `data`, and `result` are available as Dify variables. Only a terminal successful result has `success=true`; intermediate previews remain pending. Batch queries preserve the state of each item. Terminal task failures raise a tool error. Synchronous search, text and management results are returned directly in `data`/`result`. The plugin does not execute model-generated tools.

Includes music actions, lyrics, media formats, voices, personas, custom models and projects. Voice/custom-model operations require authorized source recordings. Model creation has its own API price; review current pricing before use.

Task/query calls retry transport failures at most twice. Generation has one attempt and a 10-second connect / 60-second read timeout. After a timeout, inspect [request history](https://platform.acedata.cloud/console/usages) before resubmitting; the accepted task may still be running. Delete/archive operations require `confirm=true`.

## Branding and privacy

The plugin uses the exact existing system asset recorded in [branding provenance](https://github.com/AceDataCloud/SunoDify/blob/main/tests/branding-source.json), for both light and dark icons. No logo was generated or redrawn. Asset SHA256: `d2ccb1c0039519a68913ad447114f8f9ecca161ffc2105cd61c414e06f8747d9`.

Requests go directly to `https://api.acedata.cloud`. The plugin passes reference URLs to that API and returns media links; it does not fetch arbitrary reference URLs. Dify may fetch/render output links under its own policies. Never submit media you lack permission to process. See [PRIVACY.md](PRIVACY.md).

API charges are recorded in Credits in your Ace Data Cloud account. Check the actual usage ledger; Dify execution counts are not a billing ledger. USD = Credits × your current package price / amount.

## Development and evidence

Python 3.12 is required. Install `requirements.txt`, then run:

```sh
python -m pytest tests -q
ruff check .
ruff format --check .
dify plugin package .
```

Source contracts, MCP mappings, brand provenance and offline cases are in `tests/`. Recorded real Dify results state their exact coverage; they do not establish all models/options or Dify Cloud/Marketplace installation. See [tests/README.md](https://github.com/AceDataCloud/SunoDify/blob/main/tests/README.md).

- Source: https://github.com/AceDataCloud/SunoDify
- Issues: https://github.com/AceDataCloud/SunoDify/issues
- Contact: dev@acedata.cloud
- License: MIT
- [Simplified Chinese](readme/README_zh_Hans.md)

## Official Marketplace verification

[Install from Dify Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/suno). Version 0.0.1 was downloaded and installed through the official Marketplace flow on October 8, 2026, with signature verification enabled and no remote-debug process. The installed plugin then completed the recorded real Dify workflow. [Verification data](tests/marketplace-acceptance.json) and [original Dify screenshot](tests/evidence/marketplace-20261008.png) document the exact scope. This proves optional Marketplace availability, not default installation or featured placement.

The installed tool queried a previously generated, completed task and returned its final media. The generation itself was not repeated; earlier generation evidence remains separate.
