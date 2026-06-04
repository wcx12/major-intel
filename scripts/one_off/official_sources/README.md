# Official Source One-Off Scripts

这里存放历史批次的官网证据采集、PDF/OCR 解析、人工补数和结果修补脚本。

这些脚本的定位是“可追溯的一次性数据生产记录”，不是稳定的业务 API：

- 文件名通常带有批次号、学校缩写或具体来源，例如 `curate_batch176_shzu_pdfs.py`。
- 脚本可以依赖当时的本地文件、网页结构、PDF 版式或临时输出目录。
- 后续如果某段逻辑需要长期复用，应抽取到 `src/major_intel/crawlers/`、`src/major_intel/ingestion/` 或 `src/major_intel/reporting/`。
- 新增一次性脚本也应放在本目录，不再放到 `scripts/` 根目录。

对应测试位于 `tests/one_off/official_sources/`。这些测试用于保留历史解析逻辑的可回归性，但不代表相关脚本已经是稳定命令入口。
