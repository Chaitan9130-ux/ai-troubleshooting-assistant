"""Run with: python -m streamlit run app.py"""
import os
import time
import streamlit as st
from retrieval import Retriever
from responses import format_response
from gemini import DEFAULT_MODEL, GeneratedAnswer, generate_answer

st.set_page_config(page_title="Support Desk | Troubleshooting", page_icon="🔎", layout="wide")


@st.cache_resource
def get_retriever():
    return Retriever()


def setting(name, default=""):
    """Server-side configuration only; never collect a shared key in the public UI."""
    value = os.environ.get(name)
    if value is None:
        try:
            value = st.secrets.get(name, default)
        except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
            value = default
    return str(value).strip()


api_key = setting("GEMINI_API_KEY")
if api_key == "REPLACE_WITH_YOUR_KEY":
    api_key = ""
model = setting("GEMINI_MODEL", DEFAULT_MODEL)


st.title("AI Troubleshooting Assistant")
st.caption("L1 / L2 SUPPORT · SIMULATED KNOWLEDGE BASE")
st.write("Find documented checks, understand possible causes, and route an escalation.")

try:
    retriever = get_retriever()
except (ValueError, OSError) as exc:
    st.error(f"Could not load the knowledge base: {exc}")
    st.stop()

with st.sidebar:
    st.subheader("Prototype guide")
    st.write(f"{len(retriever.entries)} simulated support runbooks")
    response_mode = st.selectbox("Response mode", ["Source only", "Gemini + sources"])
    if api_key:
        st.success("Gemini key configured; live connection not checked.")
    else:
        st.info("Gemini awaits an API key. Source-only guidance remains available.")
    if response_mode == "Gemini + sources":
        st.caption("This mode sends your description and the matched simulated runbook to Google Gemini.")
        st.caption(f"Configured model: {model}")
    st.caption("Similarity measures word overlap, not the probability of a correct diagnosis.")
    st.write("Sample queries")
    for example in ("The payment API is returning a 500 error", "Cannot connect to the database", "The service is down", "My keyboard is broken"):
        if st.button(example, use_container_width=True):
            st.session_state["issue"] = example
            st.session_state.pop("last_result", None)
    st.caption("Use simulated descriptions. Do not enter credentials or private logs.")

with st.form("issue_form"):
    query = st.text_area("Describe the technical issue", key="issue", height=130,
                         max_chars=2000, placeholder="Include the service, exact error, and when it started.")
    submitted = st.form_submit_button("Find troubleshooting guidance", type="primary")

if submitted:
    with st.spinner("Searching the sample runbooks…"):
        result = retriever.search(query)
        generated = GeneratedAnswer("offline", notice="Source-only response; Gemini was not called.")
        if response_mode == "Gemini + sources":
            last_call = st.session_state.get("last_gemini_call", 0)
            now = time.monotonic()
            if result.status == "matched" and api_key and now - last_call < 20:
                generated = GeneratedAnswer("offline", notice="Wait 20 seconds between Gemini requests. Showing the source-based fallback.")
            else:
                if result.status == "matched" and api_key:
                    st.session_state["last_gemini_call"] = now
                with st.spinner("Preparing source-grounded guidance…"):
                    generated = generate_answer(query, result, api_key, model)
        st.session_state["last_result"] = (query, result, generated)

if "last_result" in st.session_state:
    stored = st.session_state["last_result"]
    previous_query, result = stored[:2]
    generated = stored[2] if len(stored) == 3 else GeneratedAnswer("offline", notice="Source-only response from the previous app version.")
    st.subheader("Investigation guidance")
    st.caption(f"Submitted issue: {previous_query}")
    if result.status == "matched":
        st.success("Relevant source found — diagnosis still needs verification")
    else:
        st.warning("More information needed" if result.status == "ambiguous" else "No troubleshooting answer generated")
    if generated.mode == "gemini":
        st.caption("Response mode: Gemini assessment + verified source guidance")
        st.write("**Gemini assessment — verify against the source**")
        st.text(generated.assessment)
    else:
        st.caption(f"Response mode: source only. {generated.notice}")
    st.markdown(format_response(result))
    for match in result.matches:
        with st.expander(f"Source {match.entry['id']} · {match.entry['title']}"):
            st.caption(f"TF-IDF similarity: {match.score:.3f} · simulated source")
            st.json(match.entry)
    notes = (f"Gemini assessment (interpretation, not a confirmed diagnosis):\n{generated.assessment}\n\n"
             if generated.mode == "gemini" else f"Source-only response. {generated.notice}\n\n") + format_response(result)
    st.download_button("Download investigation notes", notes,
                       file_name="investigation-notes.md", mime="text/markdown")

st.divider()
st.caption("Guidance only. No systems are inspected and no commands are executed. Confirm evidence and follow your team's change process.")
