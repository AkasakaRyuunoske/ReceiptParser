from pathlib import Path


def version(request):
    changelog = Path(__file__).resolve().parent.parent.parent / "CHANGELOG.md"

    first_line = changelog.read_text(encoding="utf-8").splitlines()[0]

    return {
        "app_version": first_line.strip("*").strip(),
    }
