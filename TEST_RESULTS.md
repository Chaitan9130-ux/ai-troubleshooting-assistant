# Verified baseline results

Run date: 22 October 2026. Windows, Python 3.13.13, Streamlit 1.50.0, scikit-learn 1.8.0, pytest 8.4.2.

Result: **30 passed in 4.33 seconds**, exit code 0.

| Coverage | Cases | Result |
| --- | ---: | --- |
| Known issue retrieval, one per runbook | 15 | Passed |
| Unsupported issues | 4 | Passed |
| Generic symptoms without a fabricated fix | 3 | Passed |
| Empty and overlong input | 1 | Passed |
| Near-tied candidate clarification | 1 | Passed |
| Source fidelity and diagnostic order | 1 | Passed |
| User instructions cannot override fixed formatter | 1 | Passed |
| Duplicate source rejection | 1 | Passed |
| Invalid retrieval configuration | 1 | Passed |
| Streamlit form submission, repeated queries, empty input | 1 | Passed |
| Streamlit example selection | 1 | Passed |

The initial test run passed 29 cases but hit a sandbox temporary-directory permissions error while setting up the remaining case. No application assertion failed. Re-running with TEMP, TMP, and pytest's base temporary directory inside the workspace completed all 30 cases.

Verified command from the project directory in this environment:

```powershell
New-Item -ItemType Directory -Path '../../work/test-temp' -Force | Out-Null
$env:TEMP = (Resolve-Path '../../work/test-temp').Path
$env:TMP = $env:TEMP
.\.venv\Scripts\python.exe -m pytest tests -v --basetemp '../../work/test-temp/pytest-run-2'
```

For normal development, use the simpler README command. If using --basetemp, choose a disposable test-only directory: pytest can clear its contents.

Server check: launched on 127.0.0.1:8501 and GET /_stcore/health returned `ok`.

UI interactions were verified with Streamlit AppTest. Browser rendering, visual layout, and the file-download interaction were not manually verified. No LLM, API timeout handling, production integration, or independently sampled accuracy benchmark is covered by these results.
