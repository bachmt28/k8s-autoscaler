from autoscaler.apply_engine import run_apply_engine

if __name__ == "__main__":
    print("🔍 Test apply_engine.py với dry-run:")
    run_apply_engine("conf/example.ctf", dry_run=True)
