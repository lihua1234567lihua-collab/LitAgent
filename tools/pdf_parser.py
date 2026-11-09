from pathlib import Path
import shutil
import subprocess


def extract_pdf_text(pdf_path: str | Path) -> str | None:
    """从本地 PDF 提取文本。"""

    path = Path(pdf_path)

    if not path.is_file():
        return None

    executable = shutil.which("pdftotext")

    if not executable:
        return None

    try:
        result = subprocess.run(
            [executable, "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    return result.stdout.strip() or None