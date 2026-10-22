# Hosted prototype

Public app: https://chaitan-ai-troubleshooting-assistant.streamlit.app/

Repository: https://github.com/Chaitan9130-ux/ai-troubleshooting-assistant

Deployed on 22 October 2026 through Streamlit Community Cloud from branch `main`, entry point `app.py`, Python 3.13 (cloud runtime reported 3.13.16). No API keys or application secrets were configured.

## Hosted browser checks

- Payment API HTTP 500: displayed KB-001, ordered diagnostic checks, conditional resolution, and Application Support escalation.
- Generic service-down query: requested clarification and showed KB-006 as a possible source without a resolution.
- Broken keyboard query: acknowledged insufficient evidence and gave no troubleshooting fix.

The cloud build installed dependencies successfully. Streamlit's platform replaced transitive pyarrow 26.0.0 with 24.0.0 as part of its compatibility handling; the hosted environment therefore differs from the original local environment.

The first deployment was the template-based retrieval baseline. The next code version adds optional Gemini generation; its live provider check remains pending a privately configured API key. Use the README configuration instructions and select Gemini + sources to test it.
