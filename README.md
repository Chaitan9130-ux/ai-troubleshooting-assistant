# AI Troubleshooting Assistant for L1 and L2 Support

A local prototype that retrieves simulated support runbooks and presents ordered checks, conditional resolutions, escalation teams, and visible sources. It asks for more information when evidence is weak or ambiguous.

## Current milestone

The offline baseline is implemented. It uses TF-IDF and a deterministic response formatter, **not an LLM**. This follows the supplied phased approach, but the assignment's AI-formulated response requirement still needs an LLM integration before final submission. Do not describe the baseline as a completed generative AI application.

## Setup on Windows PowerShell

Requires Python 3.11–3.13. Open a terminal in this folder.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Activation is optional; these commands use the environment directly. If Python's bundled pip bootstrap fails and you already have uv installed:

```powershell
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Open the local URL printed by Streamlit. Stop the server with Ctrl+C. No API key, production access, or model downloads are needed. Package installation needs internet access; normal application operation is local. Streamlit's optional usage telemetry can be disabled with `--browser.gatherUsageStats false`.

## Project map

- `app.py`: Streamlit form, result display, source expansion, and notes download.
- `knowledge_base.json`: 15 simulated runbooks; no production tickets or credentials.
- `retrieval.py`: schema checks, TF-IDF indexing, similarity ranking, and abstention.
- `responses.py`: evidence-only formatting, retaining the source's diagnostic order.
- `tests/`: retrieval, validation, grounding, and Streamlit interaction tests.
- `presentation/`: seven-slide outline, demonstration script, and interview questions.

## Architecture and reasoning

User description → TF-IDF query vector → cosine similarity against runbook symptoms → evidence gate → formatted answer or clarification → visible source.

The search index includes titles, symptoms, and keyword aliases. It intentionally excludes resolution text to reduce matches caused by unrelated remediation vocabulary. English stop words are removed; unigrams and bigrams capture both words and phrases. No model is trained. TF-IDF is a classical information-retrieval technique, not semantic reasoning.

Default similarity threshold: 0.20. If no entry clears it, no fix is returned. If the top two eligible entries differ by less than 0.06, the app requests clarification and shows candidates without resolutions. Short generic queries also trigger clarification. Scores are lexical similarity, not calibrated confidence. Defaults are prototype heuristics checked on the included cases, not validated operating thresholds.

For a match, the formatter copies the selected source's checks, conditional resolution, and escalation team. A matching symptom does not establish a confirmed root cause. No remediation is executed. Ambiguous and unsupported inputs do not produce a resolution.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

The tests cover every runbook, paraphrases, unrelated queries, generic symptoms, near-tied retrieval, malformed data, input limits, source identity, check order, and attempts to override the fixed formatter. Streamlit AppTest exercises form submission, repeated queries, empty input, and example selection. See `TEST_RESULTS.md` for the actual verified run.

Manual demonstration: submit a payment API 500 query, expand KB-001, inspect checks and escalation, try `The service is down`, then `My keyboard is broken`. Verify no fix is presented for unsupported input. Download investigation notes. See the presentation folder for the full script.

## Assumptions and limitations

- Small, curated English sample corpus; all runbooks are simulated.
- No live logs, metrics, service inspection, ticket creation, or account actions.
- Word overlap can miss paraphrases and can match unrelated text containing familiar technical terms. Contradictions and negation are not understood reliably.
- Clarification is single-turn; include the original symptom when resubmitting with more context.
- Multiple simultaneous issues should be submitted separately.
- The tiny regression set cannot establish general retrieval accuracy or production safety.
- Fixed formatting prevents generated factual additions, but incorrect source material still yields incorrect guidance.
- A future LLM introduces new risks, costs, network requirements, and failure modes that the offline tests do not evaluate.

## Next phase: grounded LLM integration

Only call the model after a successful evidence gate. Supply the selected source as data, ask for structured output, require its ID, preserve conditional language, and validate returned source references. Keep retrieved source text visible. On API timeout, malformed output, or unsupported references, fall back to the labeled offline response. Test invented fixes, prompt injection, negation, ambiguity, and API failures. Source-ID validation alone does not prove generated statements are grounded; review or constrain individual steps as well.

## Contribution disclosure

This initial code, simulated records, tests, and documentation were generated with Codex assistance. Before presenting, review and modify them, run the tests yourself, and describe only the work you actually performed. No generative model runs inside the current app. Record any later model/provider and prompt changes here.

## Reference documentation

- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
