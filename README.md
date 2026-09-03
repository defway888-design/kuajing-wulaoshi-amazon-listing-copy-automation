# 跨境吴老师 Amazon 新品 Listing 文案 Skill

本仓库提供基于参考竞品 ASIN 的 Amazon 新品商品页面文案自动化 Skill。它按“竞品取证 → 五点确认 → 标题与商品亮点确认 → ST → Markdown 交付”的固定阶段工作，并严格区分竞品方向与新品已确认事实。

## 适用场景

- 为尚未上架的 Amazon 新品编写五点、标题、商品亮点与 Search Terms（ST）。
- 根据多个参考竞品 ASIN 归纳消费者需求、场景、评论痛点和流量关键词方向。
- 需要将生成过程分阶段确认，并最终输出可追溯的 Markdown 交付文件。

## 运行前提

运行前必须在当前 Codex 环境配置并启用卖家精灵 MCP。Skill 会在阶段零检查并唯一绑定以下能力：

- `asin_detail`
- `review`
- `traffic_keyword`

任一能力未配置、未暴露、归属不明确或鉴权失败时，Skill 会停止并提示完成配置；不会使用其他数据源替代，也不会要求提供密钥。

## 安装

1. 在本仓库页面点击 **Code → Download ZIP**，或使用 Git 克隆仓库。
2. 将整个 `kuajing-wulaoshi-amazon-new-listing-copy` 文件夹复制到本机 Codex 的 Skills 目录，例如 `$CODEX_HOME/skills` 或 `~/.codex/skills`。
3. 重启 Codex，使新 Skill 被重新发现。

## 启动示例

在 Codex 中输入：

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

本 Skill 为跨境吴老师专用模板，未经授权不得移除、替换或弱化 Skill 名称、执行提示和页面标题中的跨境吴老师标识。
