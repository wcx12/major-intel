# Official Source One-Off Tests

本目录测试 `scripts/one_off/official_sources/` 下的历史批次脚本。

这些测试主要验证具体学校、具体 PDF/OCR/HTML 版式的解析规则，属于历史数据生产链路的回归保护。稳定工具、Agent、通用 crawler、入库和 reporting 的测试应放在对应的 `tests/` 模块目录中，而不是继续堆在根目录。
