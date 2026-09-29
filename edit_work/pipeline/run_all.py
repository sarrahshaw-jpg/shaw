"""Orchestrator: run the full pipeline. Usage: python3 run_all.py /path/to/source.mp4 [stage]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

SRC = sys.argv[1]
start_at = sys.argv[2] if len(sys.argv) > 2 else "1"
os.makedirs(WORK, exist_ok=True)

STAGES = ["1", "2", "3", "4", "5", "6", "7", "8"]
run_from = STAGES.index(start_at) if start_at in STAGES else 0

def stage(n, fn):
    if STAGES.index(n) < run_from:
        return
    t0 = time.time()
    print(f"\n=== STAGE {n} ===")
    fn()
    print(f"=== stage {n} done in {time.time()-t0:.1f}s ===")

stage("1", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s1_probe_audio.py '{SRC}'"))
stage("2", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s2_transcribe.py && python3 script_correct.py"))
stage("3", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s3_plan.py"))
stage("4", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s4_faces.py '{SRC}'"))
stage("5", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s5_graphics.py"))
for V in ("ld", "ig"):
    stage("6", (lambda v: lambda: os.system(
        f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s6_segments.py {v} '{SRC}'"))(V))
    stage("7", (lambda v: lambda: os.system(
        f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s7_final.py {v}"))(V))
stage("8", lambda: os.system(f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 s8_deliverables.py"))
print("\nALL DONE")
