"""Evidence-only formatter; does not call an LLM or execute remediation."""


def format_response(result):
    if result.status != "matched":
        lines = [result.message]
        if result.matches:
            lines += ["", "Possible source entries (diagnosis not confirmed):"]
            lines += [f"- {m.entry['id']}: {m.entry['title']}" for m in result.matches]
        return "\n".join(lines)
    entry = result.matches[0].entry
    return "\n".join([
        result.message, "", f"### {entry['title']}", "", "**Diagnostic checks**",
        *[f"{i}. {step}" for i, step in enumerate(entry["diagnostic_checks"], 1)],
        "", "**Conditional resolution**", entry["resolution"], "",
        f"**Escalation:** {entry['escalation_team']}",
        "Include timestamps, request IDs, relevant redacted errors, and checks already completed.",
        "", f"**Source:** {entry['source']} ({entry['id']})",
    ])
