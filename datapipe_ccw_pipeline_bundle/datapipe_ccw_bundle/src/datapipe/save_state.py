from __future__ import annotations

from pathlib import Path
import subprocess


class SaveStateError(RuntimeError):
    pass


def _run(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(args, cwd=repo_root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SaveStateError(f"Command failed: {' '.join(args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc.stdout.strip()


def commit_and_push(repo_root: Path, message: str, retries: int = 2) -> None:
    _run(repo_root, 'git', 'config', 'user.name', 'github-actions[bot]')
    _run(repo_root, 'git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    _run(repo_root, 'git', 'add', '-A')
    diff_proc = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_root)
    if diff_proc.returncode == 0:
        return
    _run(repo_root, 'git', 'commit', '-m', message)
    for attempt in range(retries + 1):
        try:
            _run(repo_root, 'git', 'fetch', 'origin', 'main')
            _run(repo_root, 'git', 'pull', '--rebase', '--autostash', 'origin', 'main')
            _run(repo_root, 'git', 'push', 'origin', 'HEAD:main')
            return
        except SaveStateError:
            if attempt >= retries:
                raise
