import csv
import json
import zipfile
from io import BytesIO
from pathlib import Path

from scripts.ingestion.build_major_risk_source_archive import (
    FetchResult,
    build_major_risk_source_archive,
    extract_text,
)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_build_major_risk_source_archive_fetches_missing_url(tmp_path):
    source_index = tmp_path / "source_index.csv"
    output_dir = tmp_path / "processed"
    report_dir = tmp_path / "reports"
    raw_root = tmp_path / "raw"
    fields = [
        "source_kind",
        "source_url",
        "source_title",
        "source_publisher",
        "source_path_status",
        "evidence_families",
        "source_tables",
        "evidence_record_count",
        "major_count",
    ]
    write_csv(
        source_index,
        [
            {
                "source_kind": "url",
                "source_url": "https://example.test/page.html",
                "source_title": "撤销专业公示",
                "source_publisher": "example",
                "source_path_status": "no_local_path",
                "evidence_families": "official_policy_warning",
                "source_tables": "policy.csv",
                "evidence_record_count": "3",
                "major_count": "2",
            },
            {
                "source_kind": "url",
                "source_url": "https://example.test/already.html",
                "source_title": "已有归档",
                "source_path_status": "all_paths_available",
                "evidence_record_count": "1",
                "major_count": "1",
            },
        ],
        fields,
    )

    def fake_fetcher(url: str, timeout_seconds: float) -> FetchResult:
        assert url == "https://example.test/page.html"
        assert timeout_seconds == 5
        return FetchResult(
            body="<html><head><title>测试页</title></head><body>专业撤销 证据</body></html>".encode(
                "utf-8"
            ),
            status_code=200,
            final_url=url,
            content_type="text/html; charset=utf-8",
        )

    manifest = build_major_risk_source_archive(
        source_index_csv=source_index,
        output_dir=output_dir,
        report_dir=report_dir,
        raw_root=raw_root,
        generated_at="2026-06-14",
        run_id="test",
        fetcher=fake_fetcher,
        timeout_seconds=5,
        sleep_seconds=0,
    )

    rows = read_rows(output_dir / "major_risk_review_source_archive_2026.csv")
    manifest_data = json.loads(
        (output_dir / "major_risk_source_archive_manifest_2026.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["row_counts"]["archive_rows"] == 1
    assert manifest_data["row_counts"]["successful_or_cached"] == 1
    assert rows[0]["crawl_status"] == "ok"
    assert rows[0]["source_url"] == "https://example.test/page.html"
    assert rows[0]["raw_path"]
    assert rows[0]["text_path"]
    assert "专业撤销" in Path(rows[0]["text_path"]).read_text(encoding="utf-8")
    assert (report_dir / "major_risk_source_archive_2026.md").exists()


def test_extract_text_handles_zip_download_payload():
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("材料/说明.txt", "拟撤销专业：信息管理与信息系统")

    text = extract_text(payload.getvalue(), content_type="", url="https://example.test/download.ashx")

    assert "ZIP archive contents" in text
    assert "拟撤销专业" in text


def test_extract_text_handles_ole_binary_fallback():
    raw = b"\xd0\xcf\x11\xe0" + "上海市本科预警专业名单 动画 法学 英语".encode("utf-16le")

    text = extract_text(raw, content_type="application/msword", url="https://example.test/source.doc")

    assert "本科预警专业名单" in text


def test_extract_text_detects_pdf_without_url_suffix():
    text = extract_text(
        b"%PDF-1.7\nnot a full pdf",
        content_type="",
        url="https://example.test/api/file/download/abc",
    )

    assert "PDF source metadata" in text
