from __future__ import annotations

import json
import subprocess
from pathlib import Path


URLS = [
    # 北京电影学院
    "https://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm",
    "https://www.bfa.edu.cn/yanjiusheng/info/1031/4155.htm",
    "https://www.bfa.edu.cn/yanjiusheng/info/1031/3842.htm",
    "https://www.bfa.edu.cn/yanjiusheng/info/1031/3724.htm",
    # 北京服装学院
    "https://yjs.bift.edu.cn/zsgz/zsxx/9bbe264e20d94a0e8b697e3b0bb35b39.htm",
    "https://yjs.bift.edu.cn/zsgz/zsxx/e63e51f6ec9f4115936ec7d43ef087ae.htm",
    # 成都体育学院
    "https://yjsy.cdsu.edu.cn/__local/5/CF/FF/D6925699C0010E87BF1FE5E7741_F6EA84B8_15ED9.pdf?e=.pdf",
    "https://yjsy.cdsu.edu.cn/__local/2/AA/E8/AB8D1C53A49715344B6C6F6825F_6E4B3004_4EE40.pdf?e=.pdf",
    "https://yjsy.cdsu.edu.cn/info/1021/4966.htm",
    "https://yjsy.cdsu.edu.cn/info/1021/4980.htm",
    "https://yjsy.cdsu.edu.cn/info/1021/6323.htm",
    "https://yjsy.cdsu.edu.cn/info/1021/6327.htm",
    # 中国医科大学
    "https://graduate.cmu.edu.cn/zsxc/info/1014/2123.htm",
    "https://graduate.cmu.edu.cn/zsxc/info/1014/2125.htm",
    "https://graduate.cmu.edu.cn/zsxx/sszs.htm",
    "https://www.cmu.edu.cn/cmuyjs/info/1900/9630.htm",
    "https://www.cmu.edu.cn/cmuyjs/info/1900/9618.htm",
    "https://www.cmu.edu.cn/cmuyjs/info/1905/9515.htm",
    "https://www.cmu.edu.cn/cmuyjs/info/1905/9514.htm",
    "https://www.cmu.edu.cn/system/_content/download.jsp?owner=1778759152&urltype=news.DownloadAttachUrl&wbfileid=13255969",
    # 重庆邮电大学
    "https://yjs.cqupt.edu.cn/info/1180/11244.htm",
    "http://yjs.cqupt.edu.cn/info/1180/11244.htm",
    "http://yjs.cqupt.edu.cn/info/1180/7864.htm",
    "https://yjs.cqupt.edu.cn/info/1180/9944.htm",
    "https://yjs.cqupt.edu.cn/info/1180/12634.htm",
    "http://yjs.cqupt.edu.cn/info/1180/12634.htm",
]


def decode_sample(raw: bytes, content_type: str) -> str:
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def probe(index: int, url: str) -> dict[str, object]:
    out_dir = Path("tmp/probe_remaining_official_urls")
    out_dir.mkdir(parents=True, exist_ok=True)
    headers_path = out_dir / f"{index:02d}.headers.txt"
    body_path = out_dir / f"{index:02d}.body"
    completed = subprocess.run(
        [
            "curl.exe",
            "-L",
            "--max-time",
            "25",
            "-A",
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            ),
            "-D",
            str(headers_path),
            "-o",
            str(body_path),
            url,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    raw = body_path.read_bytes()[:250_000] if body_path.exists() else b""
    headers = headers_path.read_text(encoding="utf-8", errors="replace") if headers_path.exists() else ""
    status = ""
    content_type = ""
    final_url = ""
    for line in headers.splitlines():
        if line.startswith("HTTP/"):
            status = line.strip().split()[1] if len(line.strip().split()) > 1 else line.strip()
        elif line.lower().startswith("content-type:"):
            content_type = line.split(":", 1)[1].strip()
        elif line.lower().startswith("location:"):
            final_url = line.split(":", 1)[1].strip()

    text = decode_sample(raw, content_type)
    return {
        "url": url,
        "curl_returncode": completed.returncode,
        "curl_stderr": completed.stderr.decode("utf-8", errors="replace")[:260],
        "status": status,
        "final_url": final_url or url,
        "content_type": content_type,
        "bytes_sampled": len(raw),
        "magic": raw[:8].hex(),
        "is_pdf": raw.startswith(b"%PDF"),
        "has_final_keywords": any(key in text for key in ("拟录取", "录取名单", "复试结果")),
        "has_row_keywords": any(key in text for key in ("考生编号", "姓名", "考生姓名", "专业代码")),
        "has_blocker_keywords": any(
            key in text.lower()
            for key in ("captcha", "safeline", "waf", "412", "404", "人机", "验证")
        ),
        "sample": " ".join(text.split())[:260],
    }


def main() -> None:
    results = [probe(index, url) for index, url in enumerate(URLS, start=1)]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
