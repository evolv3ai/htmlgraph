#!/usr/bin/env python3
"""
Claude Plugin Sync Tool

Synchronizes packages/claude-plugin/ → .claude/ to ensure local development
uses the exact same hooks, skills, and configs as the distributed plugin.

This enables proper dogfooding - we use what we ship.

Usage:
    python scripts/sync_plugin_to_local.py
    python scripts/sync_plugin_to_local.py --check
    python scripts/sync_plugin_to_local.py --dry-run
"""

import argparse
import shutil
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def compare_files(source: Path, dest: Path) -> bool:
    """Compare two files for equality."""
    if not source.exists() or not dest.exists():
        return False
    return source.read_bytes() == dest.read_bytes()


def sync_directory(
    source_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
    exclude: list[str] = None,
) -> tuple[list[str], list[str], list[str]]:
    """
    Sync directory from source to destination.

    Returns:
        (created, updated, unchanged) file lists
    """
    exclude = exclude or []
    created = []
    updated = []
    unchanged = []

    if not source_dir.exists():
        return created, updated, unchanged

    # Create destination if it doesn't exist
    if not dest_dir.exists() and not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    # Sync all files recursively
    for source_file in source_dir.rglob("*"):
        if source_file.is_file():
            # Check if excluded
            rel_path = source_file.relative_to(source_dir)
            if any(excl in str(rel_path) for excl in exclude):
                continue

            dest_file = dest_dir / rel_path

            # Check if file needs syncing
            if not dest_file.exists():
                created.append(str(rel_path))
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
            elif not compare_files(source_file, dest_file):
                updated.append(str(rel_path))
                if not dry_run:
                    shutil.copy2(source_file, dest_file)
            else:
                unchanged.append(str(rel_path))

    return created, updated, unchanged


def sync_plugin_to_local(dry_run: bool = False, check_only: bool = False) -> bool:
    """
    Sync packages/claude-plugin/ → .claude/

    Returns:
        True if sync was successful or no changes needed
        False if changes are needed (in check mode) or sync failed
    """
    project_root = get_project_root()
    plugin_dir = project_root / "packages" / "claude-plugin"
    local_dir = project_root / ".claude"

    print("🔄 Claude Plugin → .claude Sync")
    print(f"   Source: {plugin_dir.relative_to(project_root)}")
    print(f"   Target: {local_dir.relative_to(project_root)}")
    print()

    if not plugin_dir.exists():
        print("❌ Plugin directory not found!")
        return False

    # Sync hooks
    print("📦 Syncing hooks...")
    hooks_created, hooks_updated, hooks_unchanged = sync_directory(
        plugin_dir / "hooks",
        local_dir / "hooks",
        dry_run=dry_run or check_only,
        exclude=[
            "__pycache__",
            ".pyc",
            "hooks.json",
        ],  # Exclude hooks.json - intentionally different
    )

    # Sync skills
    print("🎯 Syncing skills...")
    skills_created, skills_updated, skills_unchanged = sync_directory(
        plugin_dir / "skills",
        local_dir / "skills",
        dry_run=dry_run or check_only,
        exclude=["__pycache__", ".pyc"],
    )

    # Sync config
    print("⚙️  Syncing config...")
    config_created, config_updated, config_unchanged = sync_directory(
        plugin_dir / "config",
        local_dir / "config",
        dry_run=dry_run or check_only,
    )

    # Report results
    all_created = hooks_created + skills_created + config_created
    all_updated = hooks_updated + skills_updated + config_updated
    all_unchanged = hooks_unchanged + skills_unchanged + config_unchanged

    print()
    print("📊 Sync Results:")
    print(f"   ✅ Created: {len(all_created)}")
    print(f"   🔄 Updated: {len(all_updated)}")
    print(f"   ⏭️  Unchanged: {len(all_unchanged)}")

    if all_created:
        print("\n📝 Created files:")
        for file in all_created:
            print(f"   + {file}")

    if all_updated:
        print("\n🔄 Updated files:")
        for file in all_updated:
            print(f"   ~ {file}")

    # Update .claude/settings.json to use synced hooks
    settings_file = local_dir / "settings.json"
    if (
        settings_file.exists()
        and (all_created or all_updated)
        and not dry_run
        and not check_only
    ):
        print("\n⚠️  Note: .claude/settings.json may need manual review")
        print("   Ensure hook paths reference the synced files correctly")

    # Check mode
    if check_only:
        if all_created or all_updated:
            print("\n❌ Files are out of sync!")
            print("   Run without --check to sync")
            return False
        else:
            print("\n✅ All files are in sync!")
            return True

    # Dry run mode
    if dry_run:
        print("\n🔍 Dry run complete. No files were modified.")
        return True

    # Actual sync
    if all_created or all_updated:
        print("\n✅ Sync complete!")
    else:
        print("\n✅ Already in sync!")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Sync Claude plugin to local .claude directory"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if files are in sync without modifying",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without modifying files",
    )

    args = parser.parse_args()

    try:
        success = sync_plugin_to_local(
            dry_run=args.dry_run,
            check_only=args.check,
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
