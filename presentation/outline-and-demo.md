# Ten-minute presentation outline

This is a slide content outline and speaking guide, not a PowerPoint deck. Replace test-result placeholders with the verified results in TEST_RESULTS.md. Present the Gemini integration honestly: mock tests pass, but a real provider check remains pending until a key is configured.

## Slide 1 Problem and objective — 1 minute

L1/L2 engineers spend time searching repeated symptoms. The prototype retrieves relevant runbooks, presents ordered checks, and shows the evidence. It uses only simulated data.

## Slide 2 Architecture — 1 minute

Show this flow: Streamlit input → TF-IDF retrieval → evidence gate → optional Gemini structured output → source validation → assessment with source-backed guidance, or fallback. JSON supplies the index and authoritative action fields.

## Slide 3 Knowledge base and retrieval — 1 minute

15 records cover APIs, connectivity, identity, capacity, jobs, and configuration. Explain fields using KB-001. Explain word overlap, 0.20 minimum similarity, 0.06 ambiguity margin, and why similarity is not diagnosis confidence.

## Slide 4 Live demonstration — 3 minutes

1. Launch the application before presenting.
2. Enter `The payment API is returning a 500 error` and submit.
3. Show ordered checks, conditional resolution, and Application Support escalation.
4. Expand KB-001 and compare its checks with the response.
5. Submit `The service is down`. Explain why more context is needed.
6. Submit `My keyboard is broken`. Show the insufficient-evidence response.
7. Select Gemini + sources and show a real generated assessment only after a key has been privately configured and verified. Otherwise demonstrate the labeled no-key fallback.
8. Download notes if time permits.

Backup: keep the app running and use README examples if live input is interrupted. Record a demo yourself before submission; no recording is included in this project.

## Slide 5 Testing — 1 minute

Show the 52 passing tests from TEST_RESULTS.md, distinguishing mocked Gemini tests from live API verification. Explain coverage of all 15 runbooks, unknown inputs, near ties, source fidelity, and UI interaction. Distinguish a small regression suite from evidence of real-world accuracy.

## Slide 6 Limitations and safeguards — 1 minute

Lexical retrieval can miss synonyms or misunderstand negation. Thresholds are heuristic. Fixed formatting does not independently validate runbook correctness. Sources are visible, resolutions conditional, and no actions are executed.

## Slide 7 Next phase and contribution — 2 minutes

Gemini phrasing, structured output validation, and fallback are implemented. Next: verify a real key and assess generated narrative using a larger independently written evaluation set. Disclose Codex assistance and your actual review, modifications, and testing.

## Q and A preparation

- Why TF-IDF? Small corpus, transparent ranking, quick local setup; limited semantic recall.
- Is Gemini working live? Integration and mocked tests are complete; claim live readiness only after verifying a real request.
- What prevents invented fixes? Action fields must match the source exactly or the generated result is discarded. The separate generated assessment still requires human review.
- Why these thresholds? Prototype defaults tested on a small suite; require separate evaluation to calibrate.
- What if documentation is wrong? Grounding is not correctness; owners must review and version runbooks.
- What would production require? Access controls, redaction, auditability, source ownership, broader evaluation, operational monitoring, and a controlled remediation workflow.
