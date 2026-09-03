# 跨境吴老师 Amazon 新品 Listing 文案 Skill

本仓库提供基于参考竞品 ASIN 的 Amazon 新品商品页面文案自动化 Skill。它按“竞品取证 → 五点确认 → 标题与商品亮点确认 → ST → Markdown 交付”的固定阶段工作，并严格区分竞品方向与新品已确认事实。

## 适用场景

- 为尚未上架的 Amazon 新品编写五点、标题、商品亮点与 Search Terms（ST）。
- 根据多个参考竞品 ASIN 归纳消费者需求、场景、评论痛点和流量关键词方向。
- 需要将生成过程分阶段确认，并最终输出可追溯的 Markdown 交付文件。

## 运行前提

运行前必须在实际执行本 Skill 的 Agent 环境中配置并启用卖家精灵 MCP。Skill 会在阶段零检查并唯一绑定以下能力：

- `asin_detail`
- `review`
- `traffic_keyword`

任一能力未配置、未暴露、归属不明确或鉴权失败时，Skill 会停止并提示完成配置；不会使用其他数据源替代，也不会要求提供密钥。

## 安装（适用于各类 Agent）

### 一键复制安装口令

在所使用的 Agent 对话中复制并发送以下口令：

```text
请从以下 GitHub 仓库安装跨境吴老师亚马逊商品页面文字内容自动化编写Skill
https://github.com/defway888-design/kuajing-wulaoshi-amazon-listing-copy-automation
```

支持 GitHub Skill 安装或导入的 Agent 会按自身机制完成拉取、安装或提示所需授权。不要在对话中提供卖家精灵密钥。

### 其他接入方式

本仓库是可移植的目录式 Skill 包；不依赖固定的本机路径。请始终保留完整的 `kuajing-wulaoshi-amazon-new-listing-copy` 文件夹及其内部目录结构。

| Agent 能力 | 安装或接入方式 |
| --- | --- |
| 支持本地 Skill、Rules 或 Agent Skills | 下载或克隆本仓库后，在 Agent 的设置、工作区或项目中，将整个 Skill 文件夹添加为本地 Skill／规则目录；具体目录和导入按钮以该 Agent 的官方说明为准。 |
| 不支持原生 Skill 安装 | 将 `SKILL.md` 与 `references/` 文件夹作为项目上下文或附件提供给 Agent，并让 Agent 按 `SKILL.md` 执行；运行环境仍须能连接卖家精灵 MCP。 |

完成导入后，按所用 Agent 的机制重新加载项目、工作区或 Skill 清单。若该 Agent 需要显式授权 MCP 连接，请在运行前完成授权。

## 启动示例

在已加载本 Skill 的 Agent 对话中输入：

```text
使用 $kuajing-wulaoshi-amazon-new-listing-copy，根据参考竞品 ASIN 生成并分阶段确认 Amazon 新品 Listing 文案。
```

随后提供 Amazon 站点和一个或多个参考竞品 ASIN。建议同时提供新品品牌词、主品类词、已确认的产品事实和变体信息。

## 执行结果

Skill 会先核验卖家精灵 MCP 配置；通过后按四阶段执行。所有阶段完成并获得必要确认后，会在当前可写位置生成一个 UTF-8 Markdown 文件，包含：

- 5 条本地语言卖点、标题、商品亮点和 ST；
- 参考竞品/数据状态账本与候选卖点明细；
- 关键词密度、Top10 词频、可读性和 A+ 建议；
- 标题字符数、商品亮点字符数与 ST UTF-8 bytes 校验。

## 关键文件

- `SKILL.md`：入口、阶段门槛与执行规则。
- `references/sellersprite-mcp-configuration-gate.md`：卖家精灵 MCP 配置核验。
- `references/listing-workflow-contract.md`：完整业务与数据契约。
- `references/final-delivery-template.md`：最终 Markdown 版式。
- `scripts/check_listing_limits.py`：标题、商品亮点和 ST 限制校验。

## 版本更新说明

### v1.0.3 · 2026-09-03

- 新增可直接发送给 Agent 的 GitHub 安装口令，使用完整的 Skill 名称与公开仓库地址。

### v1.0.2 · 2026-09-03

- 将安装说明改为面向各类 Agent 的通用导入方式，不再绑定单一 Agent 的路径或操作。

### v1.0.1 · 2026-09-03

- 新增 README 版本更新记录，便于追踪公共 Skill 的发布与文档变更。

### v1.0.0 · 2026-09-03

- 首次发布 Amazon 新品 Listing 文案自动化 Skill。
- 内置卖家精灵 MCP 阶段零配置核验、分阶段确认流程与 Listing 字符限制校验。

本 Skill 为跨境吴老师专用模板，未经授权不得移除、替换或弱化 Skill 名称、执行提示和页面标题中的跨境吴老师标识。
