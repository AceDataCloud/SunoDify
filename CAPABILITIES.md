# Suno capability mapping

Compared with [MCPs at f0eed10abf31](https://github.com/AceDataCloud/MCPs/tree/f0eed10abf310824cb4c33d4944c63d3654ac95b/suno) and the public API contract at PlatformBackend `fa94598267a82545fb1afed6ee26bafd6cbb9ca7`.

Includes music actions, lyrics, media formats, voices, personas, custom models and projects. Voice/custom-model operations require authorized source recordings. Model creation has its own API price; review current pricing before use.

| MCP function | Dify equivalent | Notes |
|---|---|---|
| `suno_list_models` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `suno_list_actions` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `suno_get_lyric_format_guide` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `suno_generate_music` | `suno_generate_audios` | Set action=generate |
| `suno_generate_custom_music` | `suno_generate_audios` | Set action=generate |
| `suno_extend_music` | `suno_generate_audios` | Set action=extend |
| `suno_cover_music` | `suno_generate_audios` | Set action=cover |
| `suno_concat_music` | `suno_generate_audios` | Set action=concat |
| `suno_generate_with_persona` | `suno_generate_audios` | Set action=artist_consistency |
| `suno_remaster_music` | `suno_generate_audios` | Set action=remaster |
| `suno_stems_music` | `suno_generate_audios` | Set action=stems |
| `suno_replace_section` | `suno_generate_audios` | Set action=replace_section |
| `suno_upload_extend` | `suno_generate_audios` | Set action=upload_extend |
| `suno_upload_cover` | `suno_generate_audios` | Set action=upload_cover |
| `suno_mashup_music` | `suno_generate_audios` | Set action=mashup |
| `suno_all_stems_music` | `suno_generate_audios` | Set action=all_stems |
| `suno_generate_with_persona_vox` | `suno_generate_audios` | Set action=artist_consistency_vox |
| `suno_underpainting` | `suno_generate_audios` | Set action=underpainting |
| `suno_overpainting` | `suno_generate_audios` | Set action=overpainting |
| `suno_samples_music` | `suno_generate_audios` | Set action=samples |
| `suno_generate_inspo` | `suno_generate_audios` | Set action=inspo |
| `suno_generate_lyrics` | `suno_generate_lyrics` |  |
| `suno_get_task` | `suno_task_retrieve` | Set action=retrieve |
| `suno_get_tasks_batch` | `suno_tasks_retrieve_batch` | Set action=retrieve_batch |
| `suno_get_mp4` | `suno_get_mp4` |  |
| `suno_get_timing` | `suno_get_timing` |  |
| `suno_extract_vocals` | `suno_create_vox_audio` |  |
| `suno_get_wav` | `suno_get_wav` |  |
| `suno_get_mp3` | `suno_get_mp3` |  |
| `suno_get_midi` | `suno_get_midi` |  |
| `suno_optimize_style` | `suno_enhance_style` |  |
| `suno_mashup_lyrics` | `suno_mashup_lyrics` |  |
| `suno_upload_audio` | `suno_upload_reference_audio` |  |
| `suno_create_voice` | `suno_create_voice` |  |
| `suno_create_persona` | `suno_create_persona` |  |
| `suno_list_personas` | `suno_list_personas` |  |
| `suno_delete_persona` | `suno_delete_persona` |  |
| `suno_create_custom_model` | `suno_custom_models` | Set action=create |
| `suno_get_custom_model` | `suno_custom_models` | Set action=retrieve |
| `suno_list_custom_models` | `suno_custom_models` | Set action=retrieve_batch |
| `suno_generate_with_custom_model` | `suno_custom_models` | Set action=generate |
| `suno_archive_custom_model` | `suno_custom_models` | Set action=delete |

## Parameter equivalents

- `suno_replace_section`: `result_mode` → replace_section_result_mode.
- `suno_get_tasks_batch`: `task_ids` → ids.
- `suno_get_custom_model`: `model_id` → id.
- `suno_generate_with_custom_model`: `model_id` → id.
- `suno_archive_custom_model`: `model_id` → id.

## Verification boundary

Contract examples and regression tests cover request validation, transport and task handling. Actual Dify browser cases are recorded separately in `tests/e2e-results.json` and `tests/e2e-audit.json` when available. A schema test is not a successful paid generation. Unsupported service availability and untested advanced combinations must not be described as passed.
