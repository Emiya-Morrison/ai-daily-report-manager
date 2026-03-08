---
name: ai-daily-report-manager
description: 自动识别并整理AI日报文件系统，支持重命名、归位和合并重复版本，生成标准化复盘报告；当用户需要整理日报文件、评估文件系统结构或生成复盘文档时使用
---

# AI日报文件管理与复盘助手

## 任务目标
- 本Skill用于：管理AI日报项目的文件系统，确保文件规范有序
- 能力包含：文件扫描识别、自动整理操作、结构评估、复盘报告生成、技能文档沉淀
- 触发条件：用户提出文件整理需求、需要评估文件系统或生成复盘文档

## 前置准备
- 依赖说明：本Skill仅使用Python标准库，无需额外安装依赖包
- 非标准文件/文件夹准备：无

## 操作步骤

### 标准流程

1. **扫描文件系统**
   - 调用 `scripts/scan_files.py` 扫描目标目录
   - 输入参数：
     - `--target_dir`：目标目录路径（必需）
     - `--output_file`：扫描结果输出文件路径（可选，默认输出到stdout）
   - 输出：JSON格式的扫描结果，包含：
     - `irregular_files`：命名不规范的文件列表
     - `misplaced_files`：位置错误的文件列表
     - `duplicate_files`：重复文件列表（按内容哈希分组）
     - `structure_issues`：目录结构问题清单
   - 注意事项：扫描结果将作为后续整理操作的依据

2. **整理文件**
   - 调用 `scripts/organize_files.py` 执行整理操作
   - 输入参数：
     - `--scan_result`：扫描结果JSON文件路径（必需）
     - `--dry_run`：试运行模式，不实际修改文件（可选，默认False）
     - `--backup`：是否备份原文件（可选，默认True）
   - 输出：执行日志和操作统计
   - 功能：
     - 重命名不规范文件
     - 移动错位文件到正确位置
     - 合并重复文件（保留最新版本）
   - 安全机制：支持dry_run模式预览操作结果，支持备份原文件

3. **评估效果**
   - 调用 `scripts/evaluate_structure.py` 评估整理后的文件系统
   - 输入参数：
     - `--target_dir`：目标目录路径（必需）
   - 输出：JSON格式的评估结果，包含：
     - `structure_score`：目录结构评分（0-100）
     - `compliance_rate`：命名规范符合率
     - `issue_summary`：剩余问题清单
     - `recommendations`：改进建议

4. **生成复盘报告**
   - 智能体根据扫描结果、整理日志和评估结果，生成标准化复盘报告
   - 参考模板：`assets/review-template.md`
   - 报告内容应包含：
     - 整理概览：处理的文件数量、问题类型分布
     - 问题分析：不规范文件的具体问题和原因
     - 改进方案：针对发现的问题提出的解决方案
     - 效果评估：整理前后的对比和评分变化
     - 后续计划：防止问题复发的长期维护计划

5. **应用优化建议**
   - 智能体根据复盘结果，生成或更新技能文档
   - 参考模板：`assets/skill-doc-template.md`
   - 文档内容应包含：
     - 经验总结：本次整理中发现的关键问题和解决方法
     - 最佳实践：文件管理的规范操作流程
     - 操作指南：日常维护的具体步骤和检查清单
   - 将沉淀的知识应用于后续的文件管理优化

### 可选分支
- **当仅需要扫描而不整理**：执行步骤1，根据扫描结果手动分析问题
- **当需要预览整理效果**：在步骤2中使用 `--dry_run` 参数，不实际修改文件
- **当发现严重问题需要人工介入**：生成问题报告后暂停，等待用户确认后再执行整理

## 资源索引

### 必要脚本
- [scripts/scan_files.py](scripts/scan_files.py)：扫描文件系统，识别不规范文件
  - 用途：全面扫描目标目录，识别命名不规范、位置错误、重复版本的文件
  - 输出格式：JSON（见脚本头部注释）
  
- [scripts/organize_files.py](scripts/organize_files.py)：执行文件整理操作
  - 用途：根据扫描结果执行重命名、移动、合并操作
  - 输入格式：JSON扫描结果文件
  - 安全特性：支持dry_run和备份模式
  
- [scripts/evaluate_structure.py](scripts/evaluate_structure.py)：评估目录结构效果
  - 用途：评估整理后的文件系统，生成评分和改进建议
  - 输出格式：JSON（见脚本头部注释）

### 领域参考
- [references/naming-convention.md](references/naming-convention.md)：文件命名规范定义
  - 何时读取：在步骤1扫描时，用于判断文件命名是否规范
  - 内容：完整的格式定义、正则表达式、命名示例、验证规则
  
- [references/directory-structure.md](references/directory-structure.md)：标准目录结构定义
  - 何时读取：在步骤1扫描和步骤3评估时，用于判断文件位置是否正确
  - 内容：标准目录树结构、目录用途说明、文件归类规则
  
- [references/file-criteria.md](references/file-criteria.md)：文件完整性检查标准
  - 何时读取：在步骤3评估时，用于检查文件的完整性和质量
  - 内容：必填字段清单、质量评分规则、验证方法

### 输出资产
- [assets/review-template.md](assets/review-template.md)：复盘报告模板
  - 用途：作为生成复盘报告的格式参考
  - 包含：概览、问题分析、改进方案、效果评估、后续计划
  
- [assets/skill-doc-template.md](assets/skill-doc-template.md)：技能文档模板
  - 用途：作为生成技能文档的格式参考
  - 包含：经验总结、最佳实践、操作指南

## 注意事项

### 脚本使用注意事项
- 所有脚本必须通过命令行参数接收目标目录路径，不接受交互式输入
- 脚本执行前请确认目标目录路径的正确性和访问权限
- 建议先使用 `--dry_run` 参数预览整理效果，确认无误后再执行实际操作
- 默认开启备份模式，原文件会备份到 `backup/` 目录
- 扫描结果和评估结果使用JSON格式输出，便于程序处理和智能体分析

### 智能体职责
- 脚本负责技术性操作：扫描、重命名、移动、合并、评估
- 智能体负责创造性任务：复盘报告撰写、技能文档生成、问题分析、方案设计
- 智能体应根据扫描和评估结果，提供有针对性的改进建议
- 智能体在生成报告时应结合具体问题，避免泛泛而谈

### 质量控制
- 整理前后都应运行评估脚本，确保改进效果可量化
- 发现问题应及时记录，并在复盘报告中详细分析
- 长期维护：建议定期（如每月）运行完整流程，保持文件系统规范有序
- 知识沉淀：每次复盘都应更新技能文档，积累管理经验

## 使用示例

### 示例1：首次整理文件系统
```bash
# 步骤1：扫描文件系统
python scripts/scan_files.py --target_dir ./daily-reports --output_file scan_result.json

# 步骤2：预览整理效果（dry_run模式）
python scripts/organize_files.py --scan_result scan_result.json --dry_run

# 步骤3：执行整理（确认预览结果无误后）
python scripts/organize_files.py --scan_result scan_result.json --backup

# 步骤4：评估效果
python scripts/evaluate_structure.py --target_dir ./daily-reports
```

### 示例2：仅评估不整理
```bash
# 仅扫描评估，不执行整理操作
python scripts/scan_files.py --target_dir ./daily-reports
python scripts/evaluate_structure.py --target_dir ./daily-reports
```

### 示例3：快速检查（无备份）
```bash
# 对已规范目录进行快速检查
python scripts/scan_files.py --target_dir ./daily-reports
python scripts/organize_files.py --scan_result scan_result.json --backup false
```
