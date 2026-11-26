#!/usr/bin/env python3
"""Copy the shared files into both skills, or check that nothing drifted.

  python tools/sync_shared.py          copy shared/<path> into every skill at the same <path>
  python tools/sync_shared.py --check  fail if a copy differs from shared/, then run each skill's check_skill.py

An installed skill can only rely on files inside its own folder, so each skill keeps a copy of
the shared files. Edit only the original under shared/. Each copy gets a one-line header saying
so (Python/C#/Markdown); the check compares copies with that header in place.
"""
import subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHARED = REPO / "shared"
SKILLS = [REPO / ".claude/skills/str-to-revit", REPO / ".claude/skills/ars-to-revit"]
NOTE = "SHARED COPY - do not edit here. Edit shared/{p} in the repo, then run tools/sync_shared.py"


def files():
    return sorted(p.relative_to(SHARED).as_posix() for p in SHARED.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def with_header(rel, text):
    note = NOTE.format(p=rel)
    if rel.endswith(".py"):
        lines = text.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            return lines[0] + "# " + note + "\n" + "".join(lines[1:])
        return "# " + note + "\n" + text
    if rel.endswith(".cs"):
        return "// " + note + "\n" + text
    if rel.endswith(".md"):
        return "<!-- " + note + " -->\n" + text
    return text  # csv and others: no comment syntax, listed in the README instead


def main():
    check = "--check" in sys.argv
    bad = []
    for rel in files():
        # compare with LF line endings: git on Windows may check files out with CRLF
        want = with_header(rel, (SHARED / rel).read_text(encoding="utf-8").replace("\r\n", "\n"))
        for skill in SKILLS:
            dst = skill / rel
            have = dst.read_text(encoding="utf-8").replace("\r\n", "\n") if dst.exists() else None
            if have == want:
                continue
            if check:
                bad.append(f"{dst.relative_to(REPO).as_posix()} " + ("missing" if have is None else "differs from shared/" + rel))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(want, encoding="utf-8", newline="")
                print("updated", dst.relative_to(REPO).as_posix())
    if not check:
        print(f"synced {len(files())} shared files into {len(SKILLS)} skills")
        return
    if bad:
        print("FAIL: shared copies out of date (edit shared/, then run tools/sync_shared.py):")
        for b in bad:
            print(" -", b)
        sys.exit(1)
    print(f"OK: {len(files())} shared files identical in {len(SKILLS)} skills")
    rc = 0
    for skill in SKILLS:
        r = subprocess.run([sys.executable, str(skill / "scripts/check_skill.py")], capture_output=True, text=True)
        print(f"{skill.name}: {r.stdout.strip()}")
        rc |= r.returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()
