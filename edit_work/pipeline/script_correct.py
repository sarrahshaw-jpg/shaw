"""Correct the ASR transcript using the user's verified script.
Aligns the provided script (with punctuation) to whisper word TIMINGS.
words_asr.json (raw whisper) -> words.json (corrected text, whisper timings).
"""
import os, re, json
from difflib import SequenceMatcher
from common import *

USER_SCRIPT = """'Sorry, can I ask something?' Seven words. And the first one has just cost you a little of the room — but not for the reason you've been told.
You've heard the advice: stop apologising. The research is more interesting than that. In a series of studies at Harvard, a small, unnecessary apology — 'sorry about the rain!' — actually made people trust the speaker more. They read it as care. So 'sorry' isn't the problem.
The problem is the permission. 'Can I ask something?' turns a question into a request to exist. Linguists have a name for this whole family of habits — hedges, disclaimers, asking to speak. Powerless speech. And decades of studies say the same thing: people who speak this way are judged less competent and less credible, for exactly the same content.
The room isn't grading your question. It's grading the way you knocked.
So keep the warmth and drop the knock. 'Quick question.' 'One thing before we move on.' The question arrives already standing up.
Ask the question. Don't ask permission to ask it."""

def norm(tok):
    return re.sub(r"[^a-z']", "", tok.lower().replace("\u2019", "'"))

def main():
    asr_path = os.path.join(WORK, "words_asr.json")
    if not os.path.exists(asr_path):                      # preserve raw whisper once
        words = jload(os.path.join(WORK, "words.json"))
        jsave(asr_path, words)
    words = jload(asr_path)

    # display tokens keep punctuation; matching keys are normalized
    raw_disp = [t.strip() for t in USER_SCRIPT.replace("**", "").split()]
    disp, keys = [], []
    for t in raw_disp:
        t = t.replace("\u2019", "'").strip()
        if not norm(t):
            continue                                       # lone dashes etc.
        disp.append(t)
        keys.append(norm(t).strip("'"))

    wkeys = [norm(w["w"]).strip("'") for w in words]
    sm = SequenceMatcher(None, wkeys, keys, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out.append({"w": disp[j1 + k], "s": words[i1 + k]["s"], "e": words[i1 + k]["e"]})
        elif tag == "replace":
            n, m = i2 - i1, j2 - j1
            for k in range(max(n, m)):
                if k >= m:
                    break
                if k < n:
                    ws, we = words[i1 + k]["s"], words[i1 + k]["e"]
                else:
                    ws = we = (out[-1]["e"] if out else words[i1 - 1]["e"]) + 0.18
                out.append({"w": disp[j1 + k], "s": ws, "e": we})
        elif tag == "insert":
            prev_e = out[-1]["e"] if out else max(0.05, words[0]["s"] - 0.2)
            nxt_s = words[i1]["s"] if i1 < len(words) else prev_e + 0.4
            m = j2 - j1
            span = max(0.14, min(0.6, (nxt_s - prev_e) * 0.55 / m))
            t0 = prev_e + 0.03
            for k in range(m):
                out.append({"w": disp[j1 + k], "s": round(t0, 3), "e": round(t0 + span, 3)})
                t0 += span
        # 'delete': whisper hallucination -> drop
    jsave(os.path.join(WORK, "words.json"), out)
    print(f"SCRIPT FIX: {len(words)} asr words -> {len(out)} corrected words")
    print(" ".join(x["w"] for x in out)[:400], "...")

if __name__ == "__main__":
    main()
