#!/usr/bin/env python3
"""
目录结构评估脚本：评估文件系统管理效果

功能：
1. 评估目录结构是否符合标准
2. 计算命名规范符合率
3. 识别剩余问题
4. 生成评分和改进建议

输出格式：JSON
{
    "evaluation_time": "2026-03-06T10:00:00",
    "target_dir": "./daily-reports",
    "structure_score": 85,
    "compliance_rate": 0.9,
    "issue_summary": {
        "total_files": 10,
        "irregular_files": 1,
        "misplaced_files": 0,
        "duplicate_files": 0,
        "structure_issues": 1
    },
    "recommendations": [
        "修复剩余的不规范文件：./daily-reports/20240306.txt",
        "创建缺失的 review/ 目录"
    ]
}
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path


# 导入scan_files.py中的函数（避免重复代码）
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_files import scan_directory, check_naming_convention, check_file_location


def calculate_structure_score(issue_summary, total_files):
    """
    计算目录结构评分（0-100）
    
    评分标准：
    - 命名规范符合率：40分
    - 文件位置正确率：30分
    - 无重复文件：15分
    - 目录结构完整性：15分
    """
    if total_files == 0:
        return 0
    
    score = 100
    
    # 命名规范扣分（每个不规范文件扣4分，最多40分）
    naming_penalty = min(issue_summary["irregular_files"] * 4, 40)
    score -= naming_penalty
    
    # 文件位置扣分（每个错位文件扣3分，最多30分）
    location_penalty = min(issue_summary["misplaced_files"] * 3, 30)
    score -= location_penalty
    
    # 重复文件扣分（每组扣5分，最多15分）
    duplicate_penalty = min(issue_summary["duplicate_files"] * 5, 15)
    score -= duplicate_penalty
    
    # 目录结构扣分（每个问题扣3分，最多15分）
    structure_penalty = min(issue_summary["structure_issues"] * 3, 15)
    score -= structure_penalty
    
    return max(0, score)


def calculate_compliance_rate(irregular_files, total_files):
    """
    计算命名规范符合率
    
    返回：0.0-1.0之间的浮点数
    """
    if total_files == 0:
        return 0.0
    
    compliant_files = total_files - irregular_files
    return compliant_files / total_files


def generate_recommendations(issue_summary, target_dir):
    """
    生成改进建议
    
    返回：建议列表
    """
    recommendations = []
    
    # 命名不规范
    if issue_summary["irregular_files"] > 0:
        recommendations.append(
            f"修复剩余的 {issue_summary['irregular_files']} 个命名不规范的文件"
        )
    
    # 位置错误
    if issue_summary["misplaced_files"] > 0:
        recommendations.append(
            f"移动 {issue_summary['misplaced_files']} 个错位文件到正确目录"
        )
    
    # 重复文件
    if issue_summary["duplicate_files"] > 0:
        recommendations.append(
            f"清理 {issue_summary['duplicate_files']} 组重复文件"
        )
    
    # 目录结构问题
    if issue_summary["structure_issues"] > 0:
        recommendations.append(
            f"修复 {issue_summary['structure_issues']} 个目录结构问题"
        )
    
    # 如果没有问题，建议定期维护
    if not any(issue_summary.values()):
        recommendations.append(
            "文件系统状态良好，建议定期（如每月）运行评估以保持规范"
        )
    
    return recommendations


def evaluate_structure(target_dir):
    """
    评估目录结构
    
    返回：评估结果字典
    """
    # 执行扫描
    scan_result = scan_directory(target_dir)
    
    # 计算指标
    total_files = scan_result["total_files"]
    irregular_files = len(scan_result["irregular_files"])
    misplaced_files = len(scan_result["misplaced_files"])
    duplicate_files = len(scan_result["duplicate_files"])
    structure_issues = len(scan_result["structure_issues"])
    
    issue_summary = {
        "total_files": total_files,
        "irregular_files": irregular_files,
        "misplaced_files": misplaced_files,
        "duplicate_files": duplicate_files,
        "structure_issues": structure_issues
    }
    
    # 计算评分和符合率
    structure_score = calculate_structure_score(issue_summary, total_files)
    compliance_rate = calculate_compliance_rate(irregular_files, total_files)
    
    # 生成建议
    recommendations = generate_recommendations(issue_summary, target_dir)
    
    # 构建结果
    result = {
        "evaluation_time": datetime.now().isoformat(),
        "target_dir": target_dir,
        "structure_score": structure_score,
        "compliance_rate": compliance_rate,
        "issue_summary": issue_summary,
        "recommendations": recommendations
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='评估文件系统目录结构和命名规范符合度',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python evaluate_structure.py --target_dir ./daily-reports
  python evaluate_structure.py --target_dir ./daily-reports --output_file eval_result.json
        """
    )
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help='目标目录路径'
    )
    parser.add_argument(
        '--output_file',
        type=str,
        default=None,
        help='评估结果输出文件路径（可选，默认输出到stdout）'
    )
    
    args = parser.parse_args()
    
    # 检查目标目录是否存在
    if not os.path.isdir(args.target_dir):
        print(f"错误：目标目录不存在：{args.target_dir}")
        return 1
    
    # 执行评估
    print(f"开始评估目录结构：{args.target_dir}")
    result = evaluate_structure(args.target_dir)
    
    # 输出结果
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"评估完成，结果已保存到：{args.output_file}")
    else:
        print(json_output)
    
    # 打印评分信息
    print(f"\n评估结果：")
    print(f"  结构评分：{result['structure_score']}/100")
    print(f"  命名规范符合率：{result['compliance_rate']*100:.1f}%")
    print(f"  总文件数：{result['issue_summary']['total_files']}")
    print(f"  发现问题数：{sum(result['issue_summary'].values()) - result['issue_summary']['total_files']}")
    
    # 打印改进建议
    if result['recommendations']:
        print(f"\n改进建议：")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    return 0


if __name__ == '__main__':
    exit(main())
