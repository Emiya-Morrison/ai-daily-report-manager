# AI日报文件管理技能文档

**文档版本**：{{VERSION}}
**创建日期**：{{CREATION_DATE}}
**最后更新**：{{LAST_UPDATED}}

---

## 一、技能概述

### 1.1 技能定位
本技能用于管理AI日报项目的文件系统，确保文件规范有序，便于资料提取和项目维护。

### 1.2 核心能力
- **文件扫描识别**：自动识别命名不规范、位置错误、重复版本的文件
- **文件整理操作**：执行重命名、移动、合并等整理操作
- **结构评估**：评估目录结构的规范性和有效性
- **复盘报告生成**：生成标准化的复盘报告，沉淀管理经验

### 1.3 适用场景
- 当需要整理日报文件时
- 当需要评估文件系统结构时
- 当需要生成复盘文档时
- 当需要建立自动化整理机制时

---

## 二、文件管理规范

### 2.1 文件命名规范

#### 日报文件
- **格式**：`ai-daily-YYYY-MM-DD.md`
- **示例**：`ai-daily-2024-01-01.md`
- **规则**：
  - 必须以 `ai-daily-` 开头
  - 日期格式为 `YYYY-MM-DD`
  - 文件扩展名为 `.md`

#### 复盘文件
- **格式**：`review-YYYY-MM-DD.md`
- **示例**：`review-2024-01-07.md`
- **规则**：
  - 必须以 `review-` 开头
  - 日期格式为 `YYYY-MM-DD`
  - 文件扩展名为 `.md`

#### 模板文件
- **格式**：`template-*.md`
- **示例**：`template-daily.md`
- **规则**：
  - 必须以 `template-` 开头
  - 文件扩展名为 `.md`

### 2.2 目录结构规范

```
daily-reports/
├── daily/              # 日报文件目录
├── review/             # 复盘报告目录
├── template/           # 模板文件目录
├── archive/            # 归档文件目录
├── temp/               # 临时文件目录
└── backup/             # 备份文件目录
```

### 2.3 文件归类规则
- 日报文件 → `daily/`
- 复盘文件 → `review/`
- 模板文件 → `template/`
- 归档文件 → `archive/`

---

## 三、操作流程

### 3.1 标准整理流程

#### 步骤1：扫描文件系统
```bash
python scripts/scan_files.py --target_dir ./daily-reports --output_file scan_result.json
```

**输出**：
- 命名不规范的文件列表
- 位置错误的文件列表
- 重复文件列表
- 目录结构问题清单

#### 步骤2：预览整理效果（可选）
```bash
python scripts/organize_files.py --scan_result scan_result.json --dry_run
```

**说明**：
- `--dry_run` 参数用于预览，不实际修改文件
- 建议先预览，确认无误后再执行实际操作

#### 步骤3：执行整理操作
```bash
python scripts/organize_files.py --scan_result scan_result.json --backup true
```

**安全机制**：
- 默认开启备份模式
- 原文件备份到 `backup/` 目录
- 备份文件命名：`<原文件名>.bak_<timestamp>`

#### 步骤4：评估整理效果
```bash
python scripts/evaluate_structure.py --target_dir ./daily-reports --output_file eval_result.json
```

**输出**：
- 目录结构评分（0-100）
- 命名规范符合率
- 剩余问题清单
- 改进建议

#### 步骤5：生成复盘报告
由智能体根据扫描结果、整理日志和评估结果，生成标准化复盘报告。

### 3.2 快速检查流程

当只需要快速检查文件系统状态时：

```bash
# 仅扫描评估，不执行整理
python scripts/scan_files.py --target_dir ./daily-reports
python scripts/evaluate_structure.py --target_dir ./daily-reports
```

### 3.3 紧急修复流程

当发现严重问题需要紧急修复时：

```bash
# 快速扫描并整理（无备份）
python scripts/scan_files.py --target_dir ./daily-reports --output_file scan_result.json
python scripts/organize_files.py --scan_result scan_result.json --backup false
```

**注意**：`--backup false` 会关闭备份模式，谨慎使用。

---

## 四、常见问题处理

### 4.1 命名不规范问题

#### 问题示例
- `20240101.txt`
- `daily-20240106.md`
- `AI日报_20240306.md`

#### 解决方法
脚本会自动识别并建议重命名为 `ai-daily-YYYY-MM-DD.md` 格式。

### 4.2 文件位置错误问题

#### 问题示例
- 日报文件散落在根目录
- 日报文件存放在 `temp/` 目录

#### 解决方法
脚本会自动识别并移动到正确的目录（`daily/`）。

### 4.3 重复文件问题

#### 问题示例
- 同一文件在多个位置重复存放

#### 解决方法
脚本会根据内容哈希检测重复文件，保留最新版本，删除其他版本。

### 4.4 目录结构问题

#### 问题示例
- 缺少标准目录
- 存在非标准目录

#### 解决方法
脚本会自动创建缺失的标准目录，报告非标准目录。

---

## 五、经验总结

### 5.1 关键经验
{{KEY_EXPERIENCES}}

### 5.2 最佳实践
{{BEST_PRACTICES}}

### 5.3 避坑指南
{{PITFALLS_TO_AVOID}}

### 5.4 性能优化建议
{{PERFORMANCE_TIPS}}

---

## 六、维护与优化

### 6.1 定期复盘
- **频率**：建议每月进行一次全面复盘
- **内容**：
  - 扫描文件系统，识别新出现的问题
  - 评估管理效果，生成复盘报告
  - 更新技能文档，沉淀管理经验

### 6.2 自动化建议
- **定时任务**：设置定时任务，定期扫描和整理文件
- **监控告警**：当文件规范率低于阈值时，发送告警通知
- **自动归档**：自动将超过保留期限的文件移动到归档目录

### 6.3 规范更新
- 当项目需求变化时，及时更新文件管理规范
- 更新规范后，同步更新脚本和文档
- 通过复盘报告跟踪规范执行情况

---

## 七、工具使用说明

### 7.1 脚本工具

#### scan_files.py
**用途**：扫描文件系统，识别不规范文件

**参数**：
- `--target_dir`：目标目录路径（必需）
- `--output_file`：扫描结果输出文件路径（可选）

**输出**：
- JSON格式的扫描结果

#### organize_files.py
**用途**：执行文件整理操作

**参数**：
- `--scan_result`：扫描结果JSON文件路径（必需）
- `--dry_run`：试运行模式（可选）
- `--backup`：是否备份原文件（可选，默认true）

**输出**：
- 执行日志和操作统计

#### evaluate_structure.py
**用途**：评估目录结构效果

**参数**：
- `--target_dir`：目标目录路径（必需）
- `--output_file`：评估结果输出文件路径（可选）

**输出**：
- JSON格式的评估结果

### 7.2 参考文档

#### naming-convention.md
- 文件命名规范定义
- 正则表达式和验证规则
- 常见错误与修正方法

#### directory-structure.md
- 标准目录结构定义
- 目录用途说明
- 文件归类规则

#### file-criteria.md
- 文件完整性检查标准
- 质量评分规则
- 验证方法

### 7.3 资产文件

#### review-template.md
- 复盘报告模板
- 标准化报告结构

#### skill-doc-template.md
- 技能文档模板
- 经验沉淀格式

---

## 八、检查清单

### 8.1 文件整理检查清单
- [ ] 已扫描文件系统，识别所有问题
- [ ] 已预览整理效果，确认操作正确
- [ ] 已执行整理操作，备份原文件
- [ ] 已评估整理效果，验证改进结果
- [ ] 已生成复盘报告，沉淀管理经验

### 8.2 文件质量检查清单
- [ ] 文件命名符合规范
- [ ] 文件位置正确
- [ ] 无重复文件
- [ ] 目录结构完整
- [ ] 文件内容完整

### 8.3 定期维护检查清单
- [ ] 已执行定期扫描
- [ ] 已评估管理效果
- [ ] 已生成复盘报告
- [ ] 已更新技能文档
- [ ] 已优化管理流程

---

## 九、附录

### A. 相关文档
- [文件命名规范](references/naming-convention.md)
- [目录结构定义](references/directory-structure.md)
- [文件完整性标准](references/file-criteria.md)

### B. 变更历史
| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0 | {{CREATION_DATE}} | 初始版本 |

### C. 联系方式
如有问题或建议，请联系：{{CONTACT_INFO}}
