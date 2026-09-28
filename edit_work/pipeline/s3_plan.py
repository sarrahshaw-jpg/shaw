"""Stage 3: edit planner - gap/filler removal, keywords, emoji moments, zoom choreography,
caption grouping, and the src->dst time map.

Robustness notes (learned the hard way):
- whisper stretches word ends (and sometimes starts) across long pauses; the
  silencedetect map is ground truth for where speech stops. Words that swallow
  a pause are snapped to just BEFORE the pause, where their audio really is.
"""
import os, re, json, math
from collections import Counter
from common import *

FILLERS = {"um", "uh", "umm", "uhh", "erm", "mm", "hmm", "mhm", "huh", "er", "mmm-hmm", "uhhuh", "ummm"}
STOP = set("""a an the and or but so if then than that this these those i me my we our you your he she it they them his her its
is are was were be been being am do does did doing have has had having will would can could should shall may might must
to of in on at by for with from about into over after before between during without within along across behind beyond plus
not no yes just really very much many more most some any all both each few other such only own same too s t don now
going gonna want wants knew know known like likes think thinks thought thing things because actually basically literally
kind kinda sort maybe well okay ok right yeah yep nah hey hello hi there here what when where which who whom why how
say says said tell told says get got gets getting give given make makes made take takes took see saw seen look looked
way ways lot lots bit let lets us going today talk talking talked bit little also even still ever never always""".split())

probe = jload(os.path.join(WORK, "probe.json"))
words = jload(os.path.join(WORK, "words.json"))
sil = jload(os.path.join(WORK, "silence.json"), {"starts": [], "ends": []})
DUR = probe["dur"]
LONG_SIL = 0.35

# ---------------- 0) sanitize timestamps against the silence map ----------------
long_sils = [(ss, se) for ss, se in zip(sil["starts"], sil["ends"]) if se - ss >= LONG_SIL]
for w in words:
    for ss, se in long_sils:
        if w["s"] + 0.08 < ss < w["e"] - 0.05:      # word runs into a real pause -> end at pause start
            w["e"] = round(ss + 0.02, 3)
    if w["e"] <= w["s"] + 0.06:
        w["e"] = w["s"] + 0.12

# ---------------- 1) build cut list ----------------
cuts = []

if words:
    cuts.append((0.0, max(0.0, words[0]["s"] - 0.30)))
    cuts.append((words[-1]["e"] + 0.40, DUR))
elif sil["ends"]:
    cuts.append((0.0, max(0.0, sil["ends"][0])))

for i, w in enumerate(words):
    lw = re.sub(r"[^\w']", "", w["w"].lower())
    if lw in FILLERS:
        cuts.append((w["s"] - 0.04, w["e"] + 0.04))
    elif i > 0 and lw and lw == re.sub(r"[^\w']", "", words[i - 1]["w"].lower()) and lw.isalpha():
        cuts.append((w["s"] - 0.04, w["e"] + 0.06))

kept_words = [w for w in words if re.sub(r"[^\w']", "", w["w"].lower()) not in FILLERS]
for a, b in zip(kept_words, kept_words[1:]):
    gap = b["s"] - a["e"]
    if gap > 0.62:
        keep_a = 0.18
        cuts.append((a["e"] + keep_a, b["s"] - (0.30 - keep_a)))
    elif gap > 1.4:
        cuts.append((a["e"] + 0.25, b["s"] - 0.25))

if words:
    first, last = words[0]["s"], words[-1]["e"]
    for ss, se in long_sils:
        if ss <= first + 0.8 or ss >= last - 0.2:
            continue
        if se - ss > 0.62:
            cuts.append((ss + 0.25, max(ss + 0.25, se - 0.10)))

cuts = sorted([c for c in cuts if c[1] > c[0] and c[0] < DUR])
merged = []
for c in cuts:
    if merged and c[0] <= merged[-1][1] + 0.03:
        merged[-1][1] = max(merged[-1][1], c[1])
    else:
        merged.append(list(c))

segs = []
cur = 0.0
for c in merged:
    if c[0] - cur >= 0.20:
        segs.append([cur, c[0]])
    cur = max(cur, c[1])
if DUR - cur >= 0.20:
    segs.append([cur, DUR])
final_segs = []
for s in segs:
    if final_segs and s[0] - final_segs[-1][1] < 0.12:
        final_segs[-1][1] = s[1]
    else:
        final_segs.append(list(s))
segs = [s for s in final_segs if s[1] - s[0] > 0.22]

removed = 0.0
if segs:
    removed = segs[0][0] + (DUR - segs[-1][1])
    removed += sum(segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1))
print(f"PLAN: {len(words)} words -> {len(segs)} segments | removing {removed:.1f}s of {DUR:.1f}s ({100 * removed / max(DUR, 0.01):.0f}%)")

# ---------------- 2) fix words that swallowed a pause ----------------
def seg_containing(t):
    for s in segs:
        if s[0] < t < s[1]:
            return s
    return None

for wi, w in enumerate(words):
    for ss, se in long_sils:
        if w["s"] < ss and w["e"] > se:            # pause fully inside the word span
            host = seg_containing(ss)               # speech we hear just before the pause
            if host:
                ln = min(w["e"] - w["s"], 1.0)
                prev_end = words[wi - 1]["e"] if wi > 0 else 0.0
                w["e"] = round(ss + 0.02, 3)
                w["s"] = round(max(prev_end + 0.01, host[0] + 0.05, w["e"] - ln), 3)
                if w["e"] <= w["s"] + 0.06:
                    w["e"] = w["s"] + 0.12
            break
        if ss <= w["s"] < se:                        # word claimed to start inside a pause
            host = seg_containing(ss)                # (whisper late-stretch) -> it belongs just before the pause
            host = seg_containing(ss)
            if host:
                ln = min(w["e"] - w["s"], 0.35)
                prev_end = words[wi - 1]["e"] if wi > 0 else 0.0
                w["e"] = round(ss + 0.02, 3)
                w["s"] = round(max(prev_end + 0.01, host[0] + 0.05, w["e"] - ln), 3)
                if w["e"] <= w["s"] + 0.06:
                    w["e"] = w["s"] + 0.12
            break

# ---------------- 3) timeline mapping ----------------
TR_TOPIC = 0.0
TR_PLAIN = 0.0

def is_sentence_end(t):
    last = [w for w in words if w["e"] <= t + 0.9]
    return bool(last) and last[-1]["w"].rstrip()[-1:] in ".!?"

plan_segs = []
for i, (s, e) in enumerate(segs):
    plan_segs.append({"i": i, "src_s": round(s, 3), "src_e": round(e, 3),
                      "dur": round(e - s, 3), "tr_after": TR_TOPIC if is_sentence_end(e) else TR_PLAIN})

def src_in_kept(t):
    for ps in plan_segs:
        if ps["src_s"] <= t < ps["src_e"]:
            return ps
    return None

def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))

offsets = []
t_dst = 0.0
for ps in plan_segs:
    offsets.append(t_dst)
    t_dst += ps["dur"] - ps["tr_after"]

FILLER_SET = FILLERS
dst_words = []
for w in words:
    ws, we = w["s"], w["e"]
    ps = src_in_kept(ws)
    if ps is None:
        best = 0.10
        for cand in plan_segs:
            ov = overlap(ws, we, cand["src_s"], cand["src_e"])
            if ov > best:
                best, ps = ov, cand
    if ps is None:
        # orphaned word (whisper stretched it across a removed pause):
        # snap to the nearest segment edge if close, else drop
        if re.sub(r"[^\w']", "", w["w"].lower()) in FILLER_SET:
            continue
        best_d, cand_ps, at_end = 1e9, None, False
        for cand in plan_segs:
            d0 = abs(cand["src_s"] - we)
            d1 = abs(ws - cand["src_e"])
            if d0 < best_d:
                best_d, cand_ps, at_end = d0, cand, False
            if d1 < best_d:
                best_d, cand_ps, at_end = d1, cand, True
        if cand_ps is None or best_d > 0.45:
            continue
        ps = cand_ps
        base = offsets[ps["i"]]
        if at_end:
            cs = ps["src_e"] - 0.34
            ce = ps["src_e"] - 0.02
        else:
            cs = ps["src_s"] + 0.02
            ce = ps["src_s"] + 0.34
        dst_words.append({"w": w["w"], "s": round(base + cs - ps["src_s"], 3),
                          "e": round(base + ce - ps["src_s"], 3), "src_s": ws, "src_e": we})
        continue
    base = offsets[ps["i"]]
    cs = min(max(ws, ps["src_s"]), ps["src_e"] - 0.02)
    ce = min(max(we, cs + 0.10), ps["src_e"])
    dst_words.append({"w": w["w"], "s": round(base + cs - ps["src_s"], 3),
                      "e": round(base + ce - ps["src_s"], 3), "src_s": ws, "src_e": we})
NEW_DUR = t_dst

# ---------------- 4) keywords ----------------
toks = [re.sub(r"[^\w'-]", "", w["w"].lower()) for w in dst_words]
freq = Counter(t for t in toks if t and t not in STOP and len(t) > 3)
def score(word, idx):
    s = freq.get(word, 0) + len(word) * 0.2
    if word[:1].isupper(): s += 2.5
    s += max(0.0, 2.0 - idx / 40)
    return s
cands = []
for idx, w in enumerate(dst_words):
    t = re.sub(r"[^\w'-]", "", w["w"])
    if t.lower() in STOP or len(t) < 4 or t.isdigit():
        continue
    cands.append((score(t, idx), t, idx, w))
cands.sort(key=lambda x: -x[0])
keywords, used_idx, seen_texts = [], set(), set()
for sc, t, idx, w in cands:
    if t.upper() in seen_texts:
        continue
    if any(abs(idx - u) < 12 for u in used_idx):
        continue
    keywords.append({"text": t.upper(), "src_s": w["src_s"], "src_e": w["src_e"], "score": round(sc, 2)})
    used_idx.add(idx); seen_texts.add(t.upper())
    if len(keywords) >= 6:
        break

# ---------------- 5) emoji moments ----------------
EMOJI_MAP = [
    (r"\b(grow|growth|scale|scaling|launch|launching|start|startup|level)\w*", "1F680"),
    (r"\b(idea|ideas|think|thinking|brain|mind|learn|learning|smart)\w*", "1F4A1"),
    (r"\b(money|revenue|profit|sales|dollar|dollars|cost|price|pay|paid|earn)\w*", "1F4B0"),
    (r"\b(increase|increased|result|results|up|higher|boost|metric|metrics|data|stats)\w*", "1F4C8"),
    (r"\b(goal|goals|target|focus|aim|mission|vision)\w*", "1F3AF"),
    (r"\b(time|fast|quick|quickly|speed|minute|minutes|hour|early|late)\w*", "23F0"),
    (r"\b(fire|hot|trend|trending|viral|amazing|insane|crazy|wild)\w*", "1F525"),
    (r"\b(correct|right|true|done|complete|finished|yes|exactly|check)\w*", "2705"),
    (r"\b(love|heart|care|passion)\w*", "2764"),
    (r"\b(team|together|collaborate|people|community|connect|network)\w*", "1F91D"),
    (r"\b(work|working|hustle|effort|hard|grind|push)\w*", "1F4AA"),
    (r"\b(win|winning|success|successful|best|achieve|achievement|proud)\w*", "1F3C6"),
    (r"\b(new|creative|sparkle|special|unique)\w*", "2728"),
    (r"\b(look|looking|see|seeing|watch|notice|eyes)\w*", "1F440"),
    (r"\b(say|saying|speak|speaking|tell|telling|voice|listen|share)\w*", "1F4E3"),
    (r"\b(secret|key|important|powerful|power|unlock)\w*", "1F511"),
    (r"\b(wow|shocking|shock|surprise|unexpected)\w*", "1F929"),
    (r"\b(system|process|step|steps|plan|strategy|framework)\w*", "2699"),
    (r"\b(write|writing|note|notes|list|journal)\w*", "1F4DD"),
    (r"\b(find|finding|search|discover|research)\w*", "1F50D"),
    (r"\b(percent|100|hundred|complete|full)\w*|%$", "1F4AF"),
    (r"\b(call|calling|phone|message|dm|email)\w*", "1F4DE"),
]
moments = []
for w in dst_words:
    low = w["w"].lower()
    for pat, code in EMOJI_MAP:
        if re.search(pat, low):
            moments.append({"code": code, "t": w["s"], "word": low})
            break
moments.sort(key=lambda m: m["t"])
picked = []
for m in moments:
    if len(picked) >= 6:
        break
    if picked and m["t"] - picked[-1]["t"] < 4.0:
        continue
    if any(k["src_s"] - 1.2 < m["t"] < k["src_e"] + 2.0 for k in keywords):
        continue
    picked.append(m)

# ---------------- 6) zoom choreography: intentional, editorial ----------------
def _find_src(sub, nth=1):
    hits = [w for w in words if sub in w["w"].lower()]
    return hits[nth - 1]["s"] if len(hits) >= nth else None

def _seg_at_src(t):
    for ps in plan_segs:
        if ps["src_s"] - 0.2 <= t <= ps["src_e"] + 0.2:
            return ps["i"]
    return None

emphasis_segs = {}
for sub, nth in (("permission", 1), ("credible", 1)):
    t = _find_src(sub, nth)
    if t is not None:
        i = _seg_at_src(t)
        if i is not None:
            emphasis_segs[i] = sub
last_i = plan_segs[-1]["i"]
for ps in plan_segs:
    if ps["i"] == 0:
        ps["zoom"] = [1.045, 1.095]
    elif ps["i"] in emphasis_segs:
        ps["zoom"] = [1.005, 1.06]
    elif ps["i"] == last_i:
        ps["zoom"] = [1.055, 1.015]
    else:
        ps["zoom"] = [1.035, 1.035]
print("ZOOM MOVES: hook +", {i: s for i, s in emphasis_segs.items()}, "+ settle")

# ---------------- 7) caption groups ----------------
groups, curgrp = [], []
for w in dst_words:
    if curgrp:
        prev = curgrp[-1]
        gap = w["s"] - prev["e"]
        dur = w["e"] - curgrp[0]["s"]
        end_sent = prev["w"].rstrip()[-1:] in ".!?,-"
        if len(curgrp) >= 4 or dur > 1.7 or gap > 0.42 or end_sent:
            groups.append(curgrp); curgrp = []
    curgrp.append(w)
if curgrp:
    groups.append(curgrp)
captions = [{"words": g, "s": g[0]["s"], "e": g[-1]["e"]} for g in groups]

# enforce strictly sequential caption times (kills overlapping captions)
dst_words.sort(key=lambda w: w["s"])
_prev = None
for w in dst_words:
    if w["e"] <= w["s"]:
        w["e"] = w["s"] + 0.12
    if _prev is not None and w["s"] < _prev["e"] - 0.01:
        w["s"] = _prev["e"] + 0.01
        if w["e"] < w["s"] + 0.10:
            w["e"] = w["s"] + 0.10
    _prev = w

def _normtok(s):
    return re.sub(r"[^a-z']", "", s.lower().replace("\u2019", "'")).strip("'")

EMPHASIS_EXTRA = ["powerless", "credible", "apologising", "trust", "permission",
                  "knock", "warmth", "exist", "competent", "care"]
emph_set = set()
DROP = {"you've", "youre", "you're", "something", "they're", "that's", "it's", "dont", "don't", "isn't"}
for w in dst_words:
    t = _normtok(w["w"]).rstrip("'")
    if t in DROP or len(t) < 4:
        continue
    if t in EMPHASIS_EXTRA or t in {k["text"].lower().rstrip("'") for k in keywords}:
        emph_set.add(t)
plan = {"segments": plan_segs, "words": dst_words, "keywords": keywords,
        "emphasis": sorted(emph_set),
        "emojis": picked, "captions": captions, "new_dur": round(NEW_DUR, 3),
        "removed_s": round(removed, 1)}
jsave(os.path.join(WORK, "plan.json"), plan)
print(f"TIMELINE: {DUR:.1f}s -> {NEW_DUR:.1f}s | keywords: {[k['text'] for k in keywords]}")
print(f"EMOJIS: {[(m['code'], round(m['t'], 1)) for m in picked]}")
print(f"CAPTIONS: {len(captions)} groups")
