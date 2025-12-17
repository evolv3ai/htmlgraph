"""
Git event logging for HtmlGraph.

Provides utilities to log Git events (commits, checkouts, merges, pushes)
to HtmlGraph's event stream for agent-agnostic continuity tracking.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_git_info() -> dict:
    """
    Get current Git repository information.

    Returns:
        Dictionary with commit hash, branch, author, etc.
        Returns empty dict if not in a Git repo.
    """
    try:
        # Get commit hash
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        commit_hash_short = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Get branch name
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Get author info
        author_name = subprocess.check_output(
            ['git', 'log', '-1', '--format=%an'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        author_email = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ae'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Get commit message
        commit_message = subprocess.check_output(
            ['git', 'log', '-1', '--format=%B'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Get changed files
        files_changed = subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip().split('\n')
        files_changed = [f for f in files_changed if f]  # Remove empty strings

        # Get stats (insertions/deletions)
        stats = subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--numstat', '-r', 'HEAD'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        insertions = 0
        deletions = 0
        for line in stats.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2 and parts[0] != '-' and parts[1] != '-':
                    insertions += int(parts[0])
                    deletions += int(parts[1])

        return {
            'commit_hash': commit_hash,
            'commit_hash_short': commit_hash_short,
            'branch': branch,
            'author_name': author_name,
            'author_email': author_email,
            'commit_message': commit_message,
            'files_changed': files_changed,
            'insertions': insertions,
            'deletions': deletions,
        }

    except subprocess.CalledProcessError:
        return {}


def get_active_features() -> list[str]:
    """
    Get list of active feature IDs.

    Returns:
        List of feature IDs with status 'in-progress'
    """
    try:
        from htmlgraph.session_manager import SessionManager

        manager = SessionManager('.htmlgraph')
        active = manager.get_active_features()
        return [f.id for f in active]

    except Exception:
        return []


def get_active_session_id() -> Optional[str]:
    """
    Get the current active session ID.

    Returns:
        Session ID if active session exists, None otherwise
    """
    try:
        from htmlgraph.session_manager import SessionManager

        manager = SessionManager('.htmlgraph')
        session = manager.get_active_session()
        return session.id if session else None

    except Exception:
        return None


def parse_feature_refs(message: str) -> list[str]:
    """
    Parse feature IDs from commit message.

    Looks for patterns like:
    - Implements: feature-xyz
    - Fixes: bug-abc
    - feature-xyz

    Args:
        message: Commit message

    Returns:
        List of feature IDs found
    """
    import re

    features = []

    # Pattern: Implements: feature-xyz
    pattern1 = r'(?:Implements|Fixes|Closes|Refs):\s*(feature-[\w-]+|bug-[\w-]+)'
    features.extend(re.findall(pattern1, message, re.IGNORECASE))

    # Pattern: feature-xyz (anywhere in message)
    pattern2 = r'\b(feature-[\w-]+|bug-[\w-]+)\b'
    features.extend(re.findall(pattern2, message, re.IGNORECASE))

    # Remove duplicates while preserving order
    seen = set()
    unique_features = []
    for f in features:
        if f not in seen:
            seen.add(f)
            unique_features.append(f)

    return unique_features


def log_git_commit(event_file: Optional[Path] = None) -> bool:
    """
    Log a Git commit event to HtmlGraph.

    Creates a GitCommit event with commit metadata, links to active features,
    and appends to the events log.

    Args:
        event_file: Path to event log file. If None, uses active session's event file.

    Returns:
        True if event was logged successfully, False otherwise
    """
    try:
        # Get Git info
        git_info = get_git_info()
        if not git_info:
            return False  # Not in a Git repo

        # Get active features
        active_features = get_active_features()

        # Parse features from commit message
        message_features = parse_feature_refs(git_info['commit_message'])

        # Combine and deduplicate features
        all_features = list(set(active_features + message_features))

        # Get session ID
        session_id = get_active_session_id()

        # Create event
        event = {
            'type': 'GitCommit',
            'timestamp': datetime.now().isoformat(),
            'commit_hash': git_info['commit_hash'],
            'commit_hash_short': git_info['commit_hash_short'],
            'branch': git_info['branch'],
            'author_name': git_info['author_name'],
            'author_email': git_info['author_email'],
            'commit_message': git_info['commit_message'],
            'files_changed': git_info['files_changed'],
            'insertions': git_info['insertions'],
            'deletions': git_info['deletions'],
            'features': all_features,
            'session_id': session_id,
        }

        # Determine event file
        if event_file is None:
            if session_id:
                event_file = Path(f'.htmlgraph/events/{session_id}.jsonl')
            else:
                # Fallback: git-events.jsonl
                event_file = Path('.htmlgraph/events/git-events.jsonl')

        # Ensure directory exists
        event_file.parent.mkdir(parents=True, exist_ok=True)

        # Append event
        with open(event_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

        return True

    except Exception as e:
        # Never fail - just log error and continue
        try:
            error_log = Path('.htmlgraph/git-hook-errors.log')
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Error logging commit: {e}\n")
        except:
            pass

        return False


def main():
    """CLI entry point for git hook."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: htmlgraph git-event <commit|checkout|merge|push>")
        sys.exit(1)

    event_type = sys.argv[1]

    if event_type == 'commit':
        success = log_git_commit()
        sys.exit(0 if success else 1)
    else:
        print(f"Event type '{event_type}' not yet implemented")
        sys.exit(1)


if __name__ == '__main__':
    main()
