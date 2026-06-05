# 仓库 README 与数据发布审视记录（2026-06-05）

本文回答三个问题：

1. 当前 README 是否足够完善。
2. 如何从 GitHub 仓库查看 Release 数据包。
3. 本地文件架构与远程仓库、Release 数据包之间如何对齐。

## 1. README 审视结论

结论：README 已经能说明项目目标、系统分层、function call、常用命令、测试状态和数据边界，但原版仍不够完整，主要缺以下内容：

- 更新时间停留在 2026-05-21，和当前仓库结构迁移、数据 Release 状态不一致。
- 只说明了“不提交数据”，没有说明“数据通过 GitHub Release 发布”的方式。
- 没有告诉使用者如何在 GitHub 页面找到 Release。
- 没有说明本地被 `.gitignore` 排除的目录如何与远端保持一致。
- 没有列清楚“Git 仓库内容”和“Release 数据资产”的区别。
- 30 个 function call 的总数是正确的，但 README 中“专项覆盖 27 个底层检索工具”的措辞容易误解，需要理解为：30 个 schema 中有一部分是联网证据补全/缺口处理入口，不全是纯本地 SQL 检索工具。

本轮已补充 README：

- 更新当前快照日期。
- 增加 GitHub Release 数据资产说明。
- 增加从仓库查看 Release 的操作路径。
- 增加本地/远程文件结构对齐口径。
- 增加详细数据发布文档链接。

## 2. GitHub 仓库里如何查看 Release

有三种方式。

第一种：直接打开 Release 页面：

- 完整本地资产 Release：https://github.com/wcx12/major-intel/releases/tag/full-local-assets-2026-06-05
- 早先的精简爬取数据 Release：https://github.com/wcx12/major-intel/releases/tag/crawled-data-2026-06-05

第二种：从仓库主页进入：

1. 打开仓库：https://github.com/wcx12/major-intel
2. 在仓库右侧找到 `Releases`。
3. 点击 `Releases`。
4. 找到 `Full local assets snapshot 2026-06-05` 或 `Crawled data snapshot 2026-06-05`。
5. 展开 `Assets`，下载需要的 zip。

第三种：用 GitHub CLI 查看：

```powershell
gh release list --repo wcx12/major-intel
gh release view full-local-assets-2026-06-05 --repo wcx12/major-intel
gh release view crawled-data-2026-06-05 --repo wcx12/major-intel
```

下载完整本地资产 Release：

```powershell
gh release download full-local-assets-2026-06-05 --repo wcx12/major-intel --dir .\release-downloads\full-local-assets-2026-06-05
```

下载后，如果要恢复成本地目录结构，把 zip 解压到仓库根目录。所有 zip 内部都保留仓库相对路径，例如 `data/raw/...`、`reports/...`、`outputs/graduate_outcomes/...`。

## 3. 完整本地资产 Release

完整本地资产 Release 的目标是：除核心 MySQL dump 和本地密钥外，把当前本地数据资产、爬取产物、报告输出和参考资料打包上传。

Release URL：https://github.com/wcx12/major-intel/releases/tag/full-local-assets-2026-06-05

| 附件 | 原始体积 | 压缩体积 | 文件数 | 说明 |
|---|---:|---:|---:|---|
| `major-intel-data-raw-2026-06-05.zip` | 1411.23 MB | 908.66 MB | 9676 | `data/raw/` 原始爬取数据、网页、PDF、HTML、JSON、图片等 |
| `major-intel-data-processed-cleaned-seeds-logs-2026-06-05.zip` | 1497.72 MB | 120.36 MB | 5320 | `data/processed/`、`data/cleaned/`、`data/seeds/`、`data/logs/`、`logs/` |
| `major-intel-reports-outputs-clean-datasets-2026-06-05.zip` | 86.36 MB | 35.97 MB | 1810 | `reports/`、`outputs/graduate_outcomes/`、`clean/`、`datasets/`、`clean_gaokao_dialogue_candidates.py` |
| `major-intel-tmp-evidence-files-2026-06-05.zip` | 230.41 MB | 201.22 MB | 906 | `tmp/` 中的临时 PDF、OCR 图片、HTML、文本等证据文件 |
| `major-intel-local-reference-workspaces-2026-06-05.zip` | 63.64 MB | 45.67 MB | 531 | `gaokao-zhiyuan-projects/` 本地参考项目和资料 |
| `FULL_LOCAL_ASSETS_MANIFEST.md` | 很小 | 很小 | 1 | 人类可读 Release 清单 |
| `full_local_assets_manifest.json` | 很小 | 很小 | 1 | 机器可读 Release 清单 |

明确没有上传：

- `gaokao_test_20260519_155032.sql`
- `gaokao_test_20260519_155216.sql`
- `.env`
- `__pycache__`
- `.pytest_cache`
- `node_modules`
- `tmp/rapidocr_pkg`
- `tmp/xlrd_pkg`
- 本地参考项目里的嵌套 `.git` 目录

其中 MySQL dump 是核心数据库备份，不能进入公开 GitHub Release；`.env` 是本地密钥配置，也不能上传。依赖包和缓存目录不是业务数据，后续可通过命令重新安装或生成。

## 4. 精简爬取数据 Release

早先已经发布过一个精简版本：

Release URL：https://github.com/wcx12/major-intel/releases/tag/crawled-data-2026-06-05

它只包含：

- 结构化爬取数据。
- 爬取 seed 和失败记录。
- 升学结果 Excel、manifest、dashboard、校验图。

这个精简 Release 适合只想审查核心爬取结果的人；完整 Release 适合恢复本地数据资产。

## 5. 本地与远程文件架构如何一致

当前有两层“远程”：

- GitHub 仓库：保存代码、文档、测试、少量样例数据。
- GitHub Release：保存大体积数据资产和生成产物。

因此，本地与远程的一致性规则是：

1. Git 仓库层面保持一致：代码、脚本、测试、文档、样例数据都应通过 Git commit/push 同步。
2. 数据资产层面通过 Release 对齐：被 `.gitignore` 排除的大文件和批量数据不进 Git 历史，而是打包进 Release。
3. Release zip 内部保留仓库相对路径：下载后在仓库根目录解压，可以恢复本地目录结构。
4. 本地数据库 dump 单独保留：它不属于公开远程资产，需要用本地备份盘、私有网盘或私有对象存储保存。
5. 本地密钥永远不进入远程：`.env`、真实密码、API Key 不进 Git，也不进 Release。

## 6. README 是否还需要继续增强

后续如果要进一步工程化，建议继续补：

- `docs/data/` 或 `docs/status/` 下的数据库表结构总览。
- 每个 Release 数据包的恢复命令和校验命令。
- 从 Release 恢复数据后如何导入 MySQL 的步骤。
- CI 配置，至少跑 `compileall` 和核心单测。
- 依赖锁定文件，例如 `requirements.txt` 或更完整的 `pyproject.toml` dependency 列表。

当前 README 对“项目是什么、怎么跑、数据在哪里、哪些没完成”已经够用；对“完整数据恢复”和“数据库导入”仍然只是第一版说明。
