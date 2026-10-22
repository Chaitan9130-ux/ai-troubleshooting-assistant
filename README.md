# AI Troubleshooting Assistant for L1 and L2 Support

Retrieve simulated runbooks and optionally ask Gemini to formulate a tentative assessment. Unsupported or ambiguous issues receive clarification rather than an invented fix.

Live app: https://chaitan-ai-troubleshooting-assistant.streamlit.app/

## Current milestone

Gemini integration is implemented using Google's generateContent REST API with structured JSON output. No real key has been supplied yet, so live authentication, model access, latency, and answer quality remain unverified. Source-only mode works without a key. A configured key is not proof of a working connection: generated mode appears only after a successful validated response.

## Local setup on Windows PowerShell

Requires Python 3.11–3.13. Open a terminal in this folder.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

If Python's bundled pip bootstrap fails and you already have uv installed:

```powershell
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Open the local URL printed by Streamlit; stop with Ctrl+C. Source-only mode needs no API key. Gemini mode needs internet access and a Gemini key. The REST adapter uses Python's standard library; no Gemini SDK dependency is required.

## Configure Gemini privately

Do not paste real keys in chat, source files, the example file, or GitHub.

Locally, create `.streamlit/secrets.toml`, copy `secrets.example.toml` into it, and replace the placeholder privately there. The real secrets file is excluded from Git and the source ZIP. Alternatively set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` in the server environment; environment values take priority over Streamlit secrets.

For the hosted app, open **Manage app → Settings → Secrets**, paste the example settings, replace the placeholder privately with your key, and save. No secret belongs in the public interface.

The default model is `gemini-3.8-flash`, as shown in Google's documentation when this phase was implemented. Set `GEMINI_MODEL` to another model available to your key if needed; it must support generateContent structured output. Unsupported models fall back rather than silently switching providers.

Choose **Gemini + sources**, submit `The payment API is returning a 500 error`, and confirm the response says **Gemini assessment + verified source guidance**. A fallback message means Gemini was not used successfully. This mode sends your submitted description and the selected simulated runbook to Google. Do not submit credentials or private support data.

## Architecture and grounding

Description → TF-IDF retrieval → evidence gate → optional Gemini request → validation → assessment and authoritative runbook fields, or a labeled source-only fallback.

The 15-entry JSON knowledge base contains IDs, symptoms, keywords, ordered checks, conditional resolutions, escalation teams, and sources. TF-IDF indexes title/symptom/keyword unigrams and bigrams. The minimum cosine similarity is 0.20; eligible top results within 0.06 trigger clarification, as do short generic descriptions. These are prototype heuristics, not calibrated diagnosis probabilities. Restart the app or clear Streamlit's cache after changing the knowledge base.

Gemini runs only for a matched entry, a configured key, and selected Gemini mode. Unknown, ambiguous, empty, and overlong queries bypass the API. The system instruction treats input as data and asks for a tentative assessment with no new actions, plus exact copies of source guidance. JSON Schema constrains structure; application code independently checks the source ID, all checks in order, resolution, and escalation team. Any changed action field, unsupported source, refusal, incomplete response, malformed JSON, or provider/network error triggers fallback. Authoritative actions are rendered from the original runbook.

The assessment is generated prose whose semantic grounding cannot be mechanically verified by these checks. It is displayed separately as plain text and labeled for verification. Prompt instructions reduce unsupported claims but do not guarantee their absence. The assessment is not a confirmed diagnosis.

Requests use a key header, a fixed HTTPS Google endpoint, no redirects, a 20-second socket timeout, a 64 KB response-read cap, and a 2,048-token output limit. The socket timeout is not a strict total wall-clock deadline. There are no automatic retries. Form submissions trigger calls; session state reuses answers on rerenders. A 20-second per-session cooldown reduces accidental repeated calls, but is not a global spending limit or protection against new visitor sessions. Requests consume the configured owner's API quota. This is a public prototype, not a production service.

## Project map

- `app.py`: mode selection, private server configuration, form, sources, and notes download.
- `retrieval.py`: knowledge-base validation, TF-IDF ranking, and abstention.
- `knowledge_base.json`: 15 simulated runbooks.
- `responses.py`: deterministic source formatting and fallback.
- `gemini.py`: REST request, prompt/schema, validation, and sanitized errors.
- `secrets.example.toml`: placeholder settings only.
- `tests/`: retrieval, Gemini mock/transport, and Streamlit interaction tests.
- `presentation/`: seven-slide outline and demo/Q&A script.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

See TEST_RESULTS.md for actual runs. Tests use dummy keys and mocked transport; they never call Google. They cover retrieval, abstention, source fidelity, altered actions and invalid sources, malformed/truncated output, timeout/quota handling, secret-safe errors, no-key fallback, UI modes, session reuse, and cooldown.

Before claiming live Gemini readiness, configure the key privately and verify a real generated assessment, visible sources, clarification behavior, and authentication/quota fallback. Passing mock tests does not establish real model quality or retrieval accuracy.

## Limitations and contribution

All support data is simulated. There is no system inspection, remediation, ticket creation, account action, multi-turn memory, or access control. Lexical retrieval can miss synonyms and misunderstand negation, contradictions, or multiple issues. Wrong documentation can still yield wrong guidance. Generated prose requires human review.

The initial code, data, Gemini integration, tests, and documentation were generated with Codex assistance. Review and test the project yourself, and describe only your actual contribution when presenting. Real Gemini execution is still pending the key.

## References

- [Gemini generateContent API](https://ai.google.dev/api/generate-content)
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output)
- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
