from pathlib import Path

ROOT = Path.cwd()

REQUIRED_DIRS = [
    "src/components/cinematic",
    "src/components/home",
    "src/components/evidence",
    "src/components/cost",
    "src/components/sources",
    "src/components/methodology",

    "src/components/hershey3d/home",
    "src/components/hershey3d/supply-chain",
    "src/components/hershey3d/factory",
    "src/components/hershey3d/distribution",
    "src/components/hershey3d/evidence",
    "src/components/hershey3d/cost",
    "src/components/hershey3d/sources",
    "src/components/hershey3d/methodology",

    "src/lib/hershey",
    "scripts",
    "artifacts/10_run_reports",
]

def ensure_dir(relative_path: str) -> dict:
    path = ROOT / relative_path
    existed_before = path.exists()
    path.mkdir(parents=True, exist_ok=True)

    gitkeep = path / ".gitkeep"
    created_gitkeep = False

    # Only create .gitkeep when the directory has no files.
    existing_items = [item for item in path.iterdir() if item.name != ".gitkeep"]
    if not existing_items and not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
        created_gitkeep = True

    return {
        "path": relative_path,
        "existed_before": existed_before,
        "exists_now": path.exists(),
        "created_gitkeep": created_gitkeep,
    }

def main() -> None:
    created = [ensure_dir(path) for path in REQUIRED_DIRS]

    print("Step 17E-B6B-1 directory scaffold completed.")
    print(f"Root: {ROOT}")
    print(f"Directories checked/created: {len(created)}")
    print("Next: run the validation script.")

if __name__ == "__main__":
    main()
