from scripts.crawlers.official_major_catalog_crawler import (
    CatalogContext,
    parse_graduate_catalog_text,
    parse_vocational_catalog_rows,
)


def _context() -> CatalogContext:
    return CatalogContext(
        catalog_year="2026",
        source_name="测试来源",
        source_url="https://example.edu/source.html",
        attachment_url="https://example.edu/source.docx",
        captured_at="2026-06-12T00:00:00+08:00",
    )


def test_parse_vocational_catalog_rows_keeps_categories_and_major_rows():
    rows = [
        ["序号", "专业代码", "专业名称"],
        ["21农林牧渔大类", "21农林牧渔大类", "21农林牧渔大类"],
        ["2101农业类", "2101农业类", "2101农业类"],
        ["1", "210101", "现代种业技术"],
        ["2", "210102", "作物生产与品质改良"],
        ["3", "210103K", "国控样例专业"],
    ]

    records = parse_vocational_catalog_rows(
        rows,
        education_level="vocational_undergraduate",
        major_level="高等职业教育本科",
        display_level="高职本科",
        context=_context(),
    )

    assert len(records) == 3
    assert records[0]["major_code"] == "210101"
    assert records[0]["major_name"] == "现代种业技术"
    assert records[0]["major_category_code"] == "21"
    assert records[0]["major_category_name"] == "农林牧渔大类"
    assert records[0]["major_class_code"] == "2101"
    assert records[0]["major_class_name"] == "农业类"
    assert records[0]["major_level"] == "高等职业教育本科"
    assert records[2]["major_code"] == "210103K"


def test_parse_graduate_catalog_text_classifies_academic_and_professional_rows():
    text = """
01 哲学
0101   哲学
0151   应用伦理*
02 经济学
0258   数字经济*
"""

    records = parse_graduate_catalog_text(text, _context())

    assert [row["major_code"] for row in records] == ["0101", "0151", "0258"]
    assert records[0]["degree_type"] == "academic_first_level_discipline"
    assert records[1]["degree_type"] == "professional_degree_category"
    assert records[1]["major_name"] == "应用伦理"
    assert records[1]["master_only"] is True
    assert records[2]["major_category_code"] == "02"
    assert records[2]["major_category_name"] == "经济学"
