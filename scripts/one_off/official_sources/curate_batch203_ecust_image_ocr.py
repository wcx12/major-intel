from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


HTML_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/"
    "gschool.ecust.edu.cn/58935c62b9ab9016.htm"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages_curated"
)
IMAGE_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/ecust_images"
)
OCR_DIR = OUT_DIR / "ocr_words"
PAGE_URL = "https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm"
SCHOOL_NAME = "\u534e\u4e1c\u7406\u5de5\u5927\u5b66"
TITLE = "\u534e\u4e1c\u7406\u5de5\u5927\u5b662026\u5e74\u7855\u58eb\u7814\u7a76\u751f\u62df\u5f55\u53d6\u540d\u5355\u516c\u793a"


WINDOWS_OCR_SCRIPT = r"""
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
function Await($op, [type]$resultType) {
    $method = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.ToString().Contains('IAsyncOperation')
    })[0]
    $task = $method.MakeGenericMethod($resultType).Invoke($null, @($op))
    $task.Wait()
    $task.Result
}
$path = (Resolve-Path $env:OCR_IMAGE_PATH).Path
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage((New-Object Windows.Globalization.Language 'zh-Hans-CN'))
$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$words = New-Object System.Collections.Generic.List[object]
foreach ($line in $result.Lines) {
    foreach ($word in $line.Words) {
        $words.Add([PSCustomObject]@{
            text = $word.Text
            x = [int]$word.BoundingRect.X
            y = [int]$word.BoundingRect.Y
            w = [int]$word.BoundingRect.Width
            h = [int]$word.BoundingRect.Height
        })
    }
}
$words | ConvertTo-Json -Depth 4 -Compress
"""


def extract_ecust_image_urls(html: str, base_url: str = PAGE_URL) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"<img\b[^>]*\bsrc=[\"'](?P<src>[^\"']+\.jpg)[\"'][^>]*\boriginal-src=", html):
        url = urljoin(base_url, match.group("src"))
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def records_from_ocr_words(
    words: list[dict[str, Any]],
    *,
    source_url: str,
    title: str = TITLE,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, anchor in enumerate(_student_id_rows(words), start=1):
        row_words = _row_words(words, anchor["y"])
        student_id = _digits(_band_text(row_words, 390, 730))
        if len(student_id) < 12:
            continue
        admission_major = _admission_major(_band_text(row_words, 1260, 1745))
        remarks = _remarks(
            _remark("learning_mode", _band_text(row_words, 1760, 2030)),
            _remark("initial_score", _score(_band_text(row_words, 2040, 2245))),
            _remark("reexam_score", _score(_band_text(row_words, 2255, 2455), decimals=2)),
            _remark("total_score", _score(_band_text(row_words, 2465, 2665), decimals=3)),
            _remark("admission_category", _band_text(row_words, 2675, 2915)),
            _remark("note", _band_text(row_words, 2940, 3350)),
        )
        name = _chinese_text(_band_text(row_words, 730, 920))
        college = _chinese_text(_band_text(row_words, 900, 1245))
        needs_review = bool(
            len(student_id) != 15
            or not name
            or not college
            or not admission_major
            or not re.search(r"^[0-9A-Za-z]{6}\s+\S+", admission_major)
        )
        records.append(
            crawler._clean_record(
                {
                    "school_name": SCHOOL_NAME,
                    "year": 2026,
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": name,
                    "student_id": student_id,
                    "college": college,
                    "admission_major": admission_major,
                    "remarks": remarks,
                    "source_url": source_url,
                    "title": title,
                    "needs_review": needs_review,
                    "_input_row_index": index,
                }
            )
        )
    return records


def download_images(image_urls: list[str], image_dir: Path = IMAGE_DIR) -> list[Path]:
    image_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.trust_env = False
    paths: list[Path] = []
    for index, url in enumerate(image_urls, start=1):
        path = image_dir / f"page{index:03d}.jpg"
        if not path.exists() or path.stat().st_size == 0:
            response = session.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            path.write_bytes(response.content)
        paths.append(path)
    return paths


def ocr_image_words(image_path: Path, cache_path: Path | None = None) -> list[dict[str, Any]]:
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            WINDOWS_OCR_SCRIPT,
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "OCR_IMAGE_PATH": str(image_path)},
    )
    data = json.loads(completed.stdout or "[]")
    if isinstance(data, dict):
        data = [data]
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def curate_records(html_path: Path = HTML_PATH) -> list[dict[str, Any]]:
    html = html_path.read_text(encoding="utf-8")
    image_urls = extract_ecust_image_urls(html, PAGE_URL)
    if not image_urls:
        raise ValueError("No ECUST admission-list image URLs found.")
    image_paths = download_images(image_urls)
    rows: list[dict[str, Any]] = []
    for index, (image_url, image_path) in enumerate(zip(image_urls, image_paths, strict=True), start=1):
        cache_path = OCR_DIR / f"page{index:03d}.json"
        rows.extend(records_from_ocr_words(ocr_image_words(image_path, cache_path), source_url=image_url))
    rows.sort(
        key=lambda row: (
            str(row.get("student_id") or ""),
            str(row.get("person_name") or ""),
            str(row.get("source_url") or ""),
        )
    )
    return rows


def _student_id_rows(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        word
        for word in words
        if 390 <= _x(word) <= 730 and 430 <= _y(word) <= 2240 and re.search(r"\d", _text(word))
    ]
    groups: list[dict[str, Any]] = []
    for word in sorted(candidates, key=lambda item: (_y(item), _x(item))):
        for group in groups:
            if abs(_y(word) - group["y"]) <= 18:
                group["words"].append(word)
                group["y"] = round(sum(_y(item) for item in group["words"]) / len(group["words"]))
                break
        else:
            groups.append({"y": _y(word), "words": [word]})
    rows: list[dict[str, Any]] = []
    for group in groups:
        student_id = _digits(_join_words(group["words"]))
        if len(student_id) >= 12:
            rows.append({"y": group["y"], "student_id": student_id})
    return rows


def _row_words(words: list[dict[str, Any]], y: int) -> list[dict[str, Any]]:
    return [word for word in words if abs(_y(word) - y) <= 20]


def _band_text(words: list[dict[str, Any]], min_x: int, max_x: int) -> str:
    return _normalize_text(_join_words(word for word in words if min_x <= _x(word) <= max_x))


def _join_words(words: Any) -> str:
    return "".join(_text(word) for word in sorted(words, key=lambda item: (_x(item), _y(item))))


def _text(word: dict[str, Any]) -> str:
    return str(word.get("text") if "text" in word else word.get("Text", ""))


def _x(word: dict[str, Any]) -> int:
    return int(word.get("x") if "x" in word else word.get("X", 0))


def _y(word: dict[str, Any]) -> int:
    return int(word.get("y") if "y" in word else word.get("Y", 0))


def _normalize_text(value: str) -> str:
    return (
        value.replace(" ", "")
        .replace("\uff0e", ".")
        .replace("\u3002", ".")
        .replace("\uff0c", ",")
        .strip()
    )


def _chinese_text(value: str) -> str:
    return re.sub(r"[^\u3400-\u9fffA-Za-z0-9()（）\-]", "", value)


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value.replace("O", "0").replace("o", "0").replace("\u3007", "0"))


def _score(value: str, *, decimals: int | None = None) -> str:
    value = _normalize_text(value).replace("O", "0").replace("o", "0")
    if "." in value:
        parts = re.findall(r"\d+|\.", value)
        compact = "".join(parts)
        head, *tail = compact.split(".")
        return f"{head}.{''.join(tail)}".strip(".")
    digits = _digits(value)
    if decimals and len(digits) > decimals:
        return f"{digits[:-decimals]}.{digits[-decimals:]}"
    return digits


def _admission_major(value: str) -> str:
    value = _normalize_text(value)
    value = re.sub(r"^(\d{4})[mM](?=\D)", r"\g<1>00", value)
    match = re.match(r"(?P<code>[0-9A-Za-z]{6})(?P<name>.+)", value)
    if not match:
        return value
    return f"{match.group('code')} {_chinese_text(match.group('name'))}".strip()


def _remark(key: str, value: str) -> str:
    value = _normalize_text(value)
    return f"{key} {value}" if value else ""


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in parts if part)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    note_lines = [
        "batch203_ecust_image_ocr_curated: OCR parsed ECUST official 2026 master admission-list images.",
        f"source_page={PAGE_URL}",
        f"rows={len(rows)}",
        f"needs_review={sum(1 for row in rows if row.get('needs_review'))}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(note_lines) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
