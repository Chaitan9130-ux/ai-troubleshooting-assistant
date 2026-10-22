# Build and understand the prototype

Use this guide to inspect the generated project one phase at a time. The files are implemented; work through the explanations and checks rather than presenting code you cannot explain.

## Phase 1 Launch locally

Follow README setup. Run Streamlit and identify the issue form and sidebar. Milestone: a local page opens without an exception.

## Phase 2 Understand the data

Open knowledge_base.json. Compare KB-001 (payment HTTP 500) with KB-002 (database connection failure). Notice that symptoms describe observations, checks collect evidence, and resolution text is conditional. Milestone: explain every field and add one realistic simulated record of your own.

## Phase 3 Understand retrieval

Read load_knowledge_base and Retriever in retrieval.py. The vectorizer converts symptoms into weighted word/phrase features. Cosine similarity ranks lexical overlap. The threshold filters weak results; close results and generic inputs ask for clarification. Milestone: explain why the highest-ranked entry may still be wrong.

## Phase 4 Understand response grounding

Read responses.py. A matched result copies diagnostic checks in order and displays the exact source. Other statuses produce no resolution. Milestone: compare a displayed answer with its expanded source.

## Phase 5 Understand the interface

Read app.py. The cached retriever avoids rebuilding the index on every interaction. A form submits the description; session state preserves results. If you edit the JSON while the app is running, clear Streamlit's cache or restart the server. Milestone: submit multiple issues and download notes.

## Phase 6 Verify behavior

Run pytest as shown in the README. Read test_retrieval.py and test_app.py. Add an independently worded query and one misleading query; inspect failures before changing thresholds. Milestone: report actual results and at least one limitation.

## Phase 7 Add generative AI before final submission

The baseline is not the complete AI formulation requirement. Integrate a model only after the evidence gate, label the chosen mode, validate sources and supported steps, and retain a deterministic fallback for provider failures. Add tests for timeout and unsupported generated claims. Milestone: demonstrate a real model response grounded in visible source material.

## Phase 8 Prepare to present

Use presentation/outline-and-demo.md. Replace generic contribution statements with your actual work. Rehearse within ten minutes and record a backup demonstration. Milestone: explain the architecture without reading the code aloud.
