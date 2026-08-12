import json
import re
import sys

# ==========================================
# TOOL DEFINITIONS (Live Connections)
# ==========================================

def tool_read_telemetry_log(log_path=".benchmark_telemetry.json"):
    """Tool: Reads local benchmark telemetry log file."""
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
        return data[-1]
    except FileNotFoundError:
        return None

def tool_parse_portfolio_doc(doc_path="index.html"):
    """Tool: Parses claimed list latency and categorical claims from portfolio HTML."""
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Latency Extraction
        latency_match = re.search(r"Standard Python List.*?(\d+\.\d+)s", content, re.DOTALL)
        claimed_latency = float(latency_match.group(1)) if latency_match else None
        
        # Categorical Assertion Extraction
        has_nasm_mouse = "mouse click" in content.lower() and "nasm" in content.lower()

        return {
            "claimed_list_latency": claimed_latency,
            "has_nasm_mouse_claim": has_nasm_mouse,
            "raw_text": content
        }
    except FileNotFoundError:
        return None

# ==========================================
# GUARDRAIL INTERACTION (Step 7)
# ==========================================

def guardrail_confirm_rerun():
    """Guardrail: Requires explicit user confirmation before executing benchmark harness."""
    print("\n[GUARDRAIL PROMPT] Benchmark re-run requested.")
    print("Execution parameters: N=100,000, 3 trials, GC disabled. Estimated runtime: ~10 seconds.")
    response = input("Do you approve triggering a local benchmark harness execution? (y/N): ").strip().lower()
    return response in ['y', 'yes']

# ==========================================
# AGENT EXECUTION LOOP
# ==========================================

def run_telemetry_guard_agent(doc_path="index.html", log_path=".benchmark_telemetry.json", threshold=0.05, override_claimed_latency=None):
    print("=== [TelemetryGuard Agent Loop Initiated] ===")
    
    # Tool Call 1: Parse Document
    print(f"-> Calling Tool: tool_parse_portfolio_doc('{doc_path}')")
    doc_data = tool_parse_portfolio_doc(doc_path)
    
    # Tool Call 2: Read Log
    print(f"-> Calling Tool: tool_read_telemetry_log('{log_path}')")
    log_data = tool_read_telemetry_log(log_path)

    if not doc_data:
        print("[AGENT ERROR] Target portfolio document not found.")
        sys.exit(1)
        
    if not log_data:
        print("[AGENT ERROR] Telemetry log missing.")
        if guardrail_confirm_rerun():
            import subprocess
            print("-> Executing benchmark.py...")
            subprocess.run([sys.executable, "benchmark.py"], check=True)
            log_data = tool_read_telemetry_log(log_path)
        else:
            print("[AGENT ABORT] User denied benchmark re-run. Audit halted.")
            sys.exit(1)

    # Agent Audit Reasoning
    errors = []
    passes = []

    # Check 1: Latency Drift (supports testing override)
    claimed = override_claimed_latency if override_claimed_latency is not None else doc_data["claimed_list_latency"]
    logged = log_data["list_pop_0_s"]

    if claimed is None:
        errors.append("MISSING TELEMETRY: Could not parse claimed list latency from document.")
    else:
        drift = abs(claimed - logged) / logged
        if drift > threshold:
            errors.append(f"LATENCY DRIFT: Claimed = {claimed}s vs Logged = {logged}s. Drift = {drift*100:.2f}% > Allowed {threshold*100}%.")
        else:
            passes.append(f"LATENCY ALIGNED: Claimed = {claimed}s vs Logged = {logged}s. Drift = {drift*100:.2f}%.")

    # Check 2: Categorical Boundary
    if doc_data["has_nasm_mouse_claim"]:
        errors.append("CATEGORICAL MISMATCH: Document claims NASM mouse clicks; Registry enforces BIOS keyboard polling (int 16h).")

    # Output Final Agent Report
    print("\n=== TELEMETRYGUARD AUDIT REPORT ===")
    for p in passes:
        print(f"[PASS] {p}")
    for e in errors:
        print(f"[FAIL] {e}")

    print("-----------------------------------")
    if errors:
        print("FINAL VERDICT: REJECT (Do not commit)")
    else:
        print("FINAL VERDICT: APPROVE (Safe to commit)")

if __name__ == "__main__":
    # Standard live run (reads index.html directly)
    run_telemetry_guard_agent()

    # UNCOMMENT THE LINE BELOW TO TEST THE PASS CONDITION (Simulates matching latency):
    # print("\n" + "="*40 + "\n--- TESTING PASS SANITY CHECK ---")
    # run_telemetry_guard_agent(override_claimed_latency=8.9472)