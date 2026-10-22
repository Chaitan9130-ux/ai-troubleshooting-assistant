"""Run with: python -m streamlit run app.py"""
import streamlit as st
from retrieval import Retriever
from responses import format_response

st.set_page_config(page_title="Support Desk | Troubleshooting", page_icon="🔎", layout="wide")


@st.cache_resource
def get_retriever():
    return Retriever()


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
    st.info("Offline baseline: TF-IDF retrieval with template-based responses. No LLM is connected.")
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
        st.session_state["last_result"] = (query, result)

if "last_result" in st.session_state:
    previous_query, result = st.session_state["last_result"]
    st.subheader("Investigation guidance")
    st.caption(f"Submitted issue: {previous_query}")
    if result.status == "matched":
        st.success("Relevant source found — diagnosis still needs verification")
    else:
        st.warning("More information needed" if result.status == "ambiguous" else "No troubleshooting answer generated")
    st.markdown(format_response(result))
    for match in result.matches:
        with st.expander(f"Source {match.entry['id']} · {match.entry['title']}"):
            st.caption(f"TF-IDF similarity: {match.score:.3f} · simulated source")
            st.json(match.entry)
    st.download_button("Download investigation notes", format_response(result),
                       file_name="investigation-notes.md", mime="text/markdown")

st.divider()
st.caption("Guidance only. No systems are inspected and no commands are executed. Confirm evidence and follow your team's change process.")
