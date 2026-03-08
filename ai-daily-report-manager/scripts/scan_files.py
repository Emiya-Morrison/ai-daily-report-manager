#!/usr/bin/env python3
"""
文件扫描脚本：识别AI日报项目中的不规范文件

功能：
1. 扫描目标目录下的所有文件
2. 识别命名不规范的文件
3. 识别位置错误的文件
4. 检测重复文件（基于内容哈希）
5. 识别目录结构问题

输出格式：JSON
{
    "scan_time": "2026-03-06T10:00:00",
    "target_dir": "./daily-reports",
    "total_files": 10,
    "irregular_files": [
        {
            "path": "./daily-reports/20240306.txt",
            "issue": "naming",
            "details": "文件名不符合命名规范，应为 ai-daily-YYYY-MM-DD.md 格式",
            "suggested_name": "ai-daily-2024-03-06.md"
        }
    ],
    "misplaced_files": [
        {
            "path": "./daily-reports/temp/ai-daily-2024-03-05.md",
            "current_dir": "./daily-reports/temp",
            "target_dir": "./daily-reports/daily",
            "issue": "location",
            "details": "日报文件应放在 daily/ 目录下"
        }
    ],
    "duplicate_files": [
        {
            "hash": "abc123...",
            "files": [
                "./daily-reports/ai-daily-2024-03-05.md",
                "./daily-reports/backup/ai-daily-2024-03-05.md"
            ],
            "keep": "./daily-reports/ai-daily-2024-03-05.md",
            "remove": ["./daily-reports/backup/ai-daily-2024-03-05.md"]
        }
    ],
    "structure_issues": [
        {
            "type": "missing_dir",
            "path": "./daily-reports/review",
            "details": "缺少 review/ 目录用于存放复盘报告"
        }
    ]
}
"""

import os
import re
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime


def calculate_file_hash(file_path, chunk_size=8192):
    """计算文件的MD5哈希值"""
    hash_obj = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"警告：无法计算文件哈希 {file_path}: {e}")
        return None


def check_naming_convention(file_path):
    """
    检查文件命名是否符合规范
    
    规范定义（见 references/naming-convention.md）：
    - 日报文件：ai-daily-YYYY-MM-DD.md
    - 复盘文件：review-YYYY-MM-DD.md
    - 模板文件：template-*.md
    - 其他文件：*.md（需要根据上下文判断）
    
    返回：(is_valid, suggested_name, issue_details)
    """
    filename = os.path.basename(file_path)
    
    # 日报文件命名模式：ai-daily-YYYY-MM-DD.md
    daily_pattern = r'^ai-daily-(\d{4}-\d{2}-\d{2})\.md$'
    match = re.match(daily_pattern, filename)
    if match:
        date_str = match.group(1)
        # 验证日期有效性
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return (True, None, None)
        except ValueError:
            return (False, None, f"日期无效: {date_str}")
    
    # 复盘文件命名模式：review-YYYY-MM-DD.md
    review_pattern = r'^review-(\d{4}-\d{2}-\d{2})\.md$'
    match = re.match(review_pattern, filename)
    if match:
        date_str = match.group(1)
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return (True, None, None)
        except ValueError:
            return (False, None, f"日期无效: {date_str}")
    
    # 模板文件命名模式：template-*.md
    template_pattern = r'^template-.+\.md$'
    if re.match(template_pattern, filename):
        return (True, None, None)
    
    # 尝试从文件名中提取日期，建议重命名
    # 常见格式：20240306.txt, 2024-03-06.md, daily-20240306.md
    date_patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # 20240306
        r'(\d{4})-(\d{2})-(\d{2})', # 2024-03-06
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            year, month, day = match.groups()
            date_str = f"{year}-{month}-{day}"
            # 尝试判断文件类型
            if 'daily' in filename.lower() or '日报' in filename:
                suggested_name = f"ai-daily-{date_str}.md"
            elif 'review' in filename.lower() or '复盘' in filename:
                suggested_name = f"review-{date_str}.md"
            else:
                suggested_name = f"ai-daily-{date_str}.md"
            
            return (False, suggested_name, f"文件名不符合命名规范，建议重命名为 {suggested_name}")
    
    # 无法识别的文件
    return (False, None, f"文件名不符合任何命名规范：{filename}")


def check_file_location(file_path, base_dir):
    """
    检查文件位置是否正确
    
    标准目录结构（见 references/directory-structure.md）：
    daily-reports/
    ├── daily/          # 日报文件
    ├── review/         # 复盘报告
    ├── template/       # 模板文件
    ├── archive/        # 归档文件
    └── temp/           # 临时文件
    
    返回：(is_correct, target_dir, issue_details)
    """
    filename = os.path.basename(file_path)
    relative_path = os.path.relpath(file_path, base_dir)
    parent_dir = os.path.dirname(relative_path)
    
    # 判断文件类型
    if filename.startswith('ai-daily-'):
        target_dir = 'daily'
    elif filename.startswith('review-'):
        target_dir = 'review'
    elif filename.startswith('template-'):
        target_dir = 'template'
    else:
        # 无法识别的文件，假设当前目录就是正确位置
        return (True, None, None)
    
    # 检查是否在正确的目录下
    if parent_dir == target_dir or parent_dir == os.path.join(target_dir, ''):
        return (True, None, None)
    
    # 特殊情况：temp 目录下的文件需要移动到正确目录
    if parent_dir == 'temp':
        return (False, target_dir, f"临时文件应移动到 {target_dir}/ 目录")
    
    return (False, target_dir, f"文件应放在 {target_dir}/ 目录下")


def scan_directory(target_dir):
    """
    扫描目标目录，识别所有问题
    
    返回：扫描结果字典
    """
    result = {
        "scan_time": datetime.now().isoformat(),
        "target_dir": target_dir,
        "total_files": 0,
        "irregular_files": [],
        "misplaced_files": [],
        "duplicate_files": [],
        "structure_issues": []
    }
    
    # 标准目录列表
    standard_dirs = ['daily', 'review', 'template', 'archive', 'temp']
    
    # 检查目录结构
    existing_dirs = set()
    file_hashes = {}  # hash -> list of file paths
    
    # 遍历所有文件
    for root, dirs, files in os.walk(target_dir):
        # 记录存在的目录
        for dir_name in dirs:
            if dir_name in standard_dirs:
                existing_dirs.add(dir_name)
            elif dir_name != '__pycache__' and not dir_name.startswith('.'):
                result["structure_issues"].append({
                    "type": "unexpected_dir",
                    "path": os.path.join(root, dir_name),
                    "details": f"存在非标准目录：{dir_name}"
                })
        
        # 检查文件
        for file in files:
            if file.startswith('.') or file == '__pycache__':
                continue
            
            file_path = os.path.join(root, file)
            result["total_files"] += 1
            
            # 检查命名规范
            is_valid, suggested_name, naming_details = check_naming_convention(file_path)
            if not is_valid:
                result["irregular_files"].append({
                    "path": file_path,
                    "issue": "naming",
                    "details": naming_details,
                    "suggested_name": suggested_name
                })
            
            # 检查文件位置
            is_correct, target_dir_path, location_details = check_file_location(
                file_path, target_dir
            )
            if not is_correct and target_dir_path:
                result["misplaced_files"].append({
                    "path": file_path,
                    "current_dir": os.path.dirname(os.path.relpath(file_path, target_dir)),
                    "target_dir": target_dir_path,
                    "issue": "location",
                    "details": location_details
                })
            
            # 计算文件哈希（用于检测重复）
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
    
    # 检测重复文件
    for file_hash, file_list in file_hashes.items():
        if len(file_list) > 1:
            # 找出最新的文件（按修改时间）
            sorted_files = sorted(file_list, key=lambda f: os.path.getmtime(f), reverse=True)
            keep_file = sorted_files[0]
            remove_files = sorted_files[1:]
            
            result["duplicate_files"].append({
                "hash": file_hash,
                "files": file_list,
                "keep": keep_file,
                "remove": remove_files
            })
    
    # 检查缺失的标准目录
    missing_dirs = set(standard_dirs) - existing_dirs
    for missing_dir in missing_dirs:
        result["structure_issues"].append({
            "type": "missing_dir",
            "path": os.path.join(target_dir, missing_dir),
            "details": f"缺少标准目录：{missing_dir}"
        })
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='扫描AI日报项目文件系统，识别不规范文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python scan_files.py --target_dir ./daily-reports
  python scan_files.py --target_dir ./daily-reports --output_file scan_result.json
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
        help='扫描结果输出文件路径（可选，默认输出到stdout）'
    )
    
    args = parser.parse_args()
    
    # 检查目标目录是否存在
    if not os.path.isdir(args.target_dir):
        print(f"错误：目标目录不存在：{args.target_dir}")
        return 1
    
    # 执行扫描
    print(f"开始扫描目录：{args.target_dir}")
    result = scan_directory(args.target_dir)
    
    # 输出结果
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"扫描完成，结果已保存到：{args.output_file}")
    else:
        print(json_output)
    
    # 打印统计信息
    print(f"\n扫描统计：")
    print(f"  总文件数：{result['total_files']}")
    print(f"  命名不规范：{len(result['irregular_files'])}")
    print(f"  位置错误：{len(result['misplaced_files'])}")
    print(f"  重复文件组：{len(result['duplicate_files'])}")
    print(f"  结构问题：{len(result['structure_issues'])}")
    
    return 0


if __name__ == '__main__':
    exit(main())
