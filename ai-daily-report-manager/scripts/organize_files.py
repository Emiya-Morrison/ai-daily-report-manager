#!/usr/bin/env python3
"""
文件整理脚本：执行重命名、移动、合并操作

功能：
1. 根据扫描结果重命名不规范文件
2. 移动错位文件到正确位置
3. 合并重复文件（保留最新版本）
4. 支持dry_run模式预览操作
5. 支持备份原文件

输入格式：JSON扫描结果文件（由scan_files.py生成）
输出格式：执行日志（JSON）
{
    "execution_time": "2026-03-06T10:00:00",
    "dry_run": true,
    "backup_enabled": true,
    "operations": [
        {
            "type": "rename",
            "from": "./daily-reports/20240306.txt",
            "to": "./daily-reports/daily/ai-daily-2024-03-06.md",
            "status": "success",
            "backup": "./daily-reports/backup/20240306.txt.bak"
        }
    ],
    "statistics": {
        "total_operations": 5,
        "successful": 4,
        "failed": 1,
        "renamed": 2,
        "moved": 2,
        "removed": 1
    }
}
"""

import os
import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def create_backup_dir(base_dir):
    """创建备份目录"""
    backup_dir = os.path.join(base_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_file(file_path, backup_dir):
    """
    备份文件
    
    返回：备份文件路径
    """
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.basename(file_path)
    backup_filename = f"{filename}.bak_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def rename_file(file_path, suggested_name, base_dir, backup_enabled=True, dry_run=False):
    """
    重命名文件
    
    返回：(success, new_path, backup_path, message)
    """
    if not suggested_name:
        return (False, None, None, "未指定新文件名")
    
    if not os.path.exists(file_path):
        return (False, None, None, f"文件不存在：{file_path}")
    
    parent_dir = os.path.dirname(file_path)
    new_path = os.path.join(parent_dir, suggested_name)
    
    # 检查目标文件是否已存在
    if os.path.exists(new_path) and os.path.abspath(file_path) != os.path.abspath(new_path):
        return (False, None, None, f"目标文件已存在：{new_path}")
    
    backup_path = None
    if backup_enabled and not dry_run:
        backup_dir = create_backup_dir(base_dir)
        backup_path = backup_file(file_path, backup_dir)
    
    if dry_run:
        return (True, new_path, backup_path, f"[DRY RUN] 将重命名：{file_path} -> {new_path}")
    
    try:
        os.rename(file_path, new_path)
        return (True, new_path, backup_path, f"重命名成功：{file_path} -> {new_path}")
    except Exception as e:
        return (False, None, backup_path, f"重命名失败：{e}")


def move_file(file_path, target_dir, base_dir, backup_enabled=True, dry_run=False):
    """
    移动文件到目标目录
    
    返回：(success, new_path, backup_path, message)
    """
    if not os.path.exists(file_path):
        return (False, None, None, f"文件不存在：{file_path}")
    
    # 构建目标路径
    filename = os.path.basename(file_path)
    target_path = os.path.join(base_dir, target_dir, filename)
    
    # 确保目标目录存在
    target_full_dir = os.path.join(base_dir, target_dir)
    if not dry_run:
        os.makedirs(target_full_dir, exist_ok=True)
    
    # 检查目标文件是否已存在
    if os.path.exists(target_path):
        return (False, None, None, f"目标文件已存在：{target_path}")
    
    backup_path = None
    if backup_enabled and not dry_run:
        backup_dir = create_backup_dir(base_dir)
        backup_path = backup_file(file_path, backup_dir)
    
    if dry_run:
        return (True, target_path, backup_path, f"[DRY RUN] 将移动：{file_path} -> {target_path}")
    
    try:
        shutil.move(file_path, target_path)
        return (True, target_path, backup_path, f"移动成功：{file_path} -> {target_path}")
    except Exception as e:
        return (False, None, backup_path, f"移动失败：{e}")


def remove_duplicate_file(file_path, backup_enabled=True, dry_run=False):
    """
    删除重复文件
    
    返回：(success, message)
    """
    if not os.path.exists(file_path):
        return (True, f"文件已不存在：{file_path}")
    
    if dry_run:
        return (True, f"[DRY RUN] 将删除重复文件：{file_path}")
    
    try:
        os.remove(file_path)
        return (True, f"已删除重复文件：{file_path}")
    except Exception as e:
        return (False, f"删除失败：{e}")


def organize_files(scan_result, dry_run=False, backup_enabled=True):
    """
    执行文件整理操作
    
    返回：执行结果字典
    """
    result = {
        "execution_time": datetime.now().isoformat(),
        "dry_run": dry_run,
        "backup_enabled": backup_enabled,
        "operations": [],
        "statistics": {
            "total_operations": 0,
            "successful": 0,
            "failed": 0,
            "renamed": 0,
            "moved": 0,
            "removed": 0
        }
    }
    
    base_dir = scan_result.get("target_dir", ".")
    
    # 处理命名不规范的文件
    for file_info in scan_result.get("irregular_files", []):
        result["statistics"]["total_operations"] += 1
        
        file_path = file_info["path"]
        suggested_name = file_info.get("suggested_name")
        
        success, new_path, backup_path, message = rename_file(
            file_path, suggested_name, base_dir, backup_enabled, dry_run
        )
        
        result["operations"].append({
            "type": "rename",
            "from": file_path,
            "to": new_path,
            "status": "success" if success else "failed",
            "backup": backup_path,
            "message": message
        })
        
        if success:
            result["statistics"]["successful"] += 1
            result["statistics"]["renamed"] += 1
        else:
            result["statistics"]["failed"] += 1
    
    # 处理位置错误的文件
    for file_info in scan_result.get("misplaced_files", []):
        result["statistics"]["total_operations"] += 1
        
        file_path = file_info["path"]
        target_dir = file_info["target_dir"]
        
        success, new_path, backup_path, message = move_file(
            file_path, target_dir, base_dir, backup_enabled, dry_run
        )
        
        result["operations"].append({
            "type": "move",
            "from": file_path,
            "to": new_path,
            "status": "success" if success else "failed",
            "backup": backup_path,
            "message": message
        })
        
        if success:
            result["statistics"]["successful"] += 1
            result["statistics"]["moved"] += 1
        else:
            result["statistics"]["failed"] += 1
    
    # 处理重复文件
    for duplicate_info in scan_result.get("duplicate_files", []):
        keep_file = duplicate_info["keep"]
        remove_files = duplicate_info["remove"]
        
        for file_path in remove_files:
            result["statistics"]["total_operations"] += 1
            
            success, message = remove_duplicate_file(
                file_path, backup_enabled, dry_run
            )
            
            result["operations"].append({
                "type": "remove",
                "file": file_path,
                "keep": keep_file,
                "status": "success" if success else "failed",
                "message": message
            })
            
            if success:
                result["statistics"]["successful"] += 1
                result["statistics"]["removed"] += 1
            else:
                result["statistics"]["failed"] += 1
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='执行文件整理操作（重命名、移动、合并）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python organize_files.py --scan_result scan_result.json
  python organize_files.py --scan_result scan_result.json --dry_run
  python organize_files.py --scan_result scan_result.json --backup false
        """
    )
    parser.add_argument(
        '--scan_result',
        type=str,
        required=True,
        help='扫描结果JSON文件路径（由scan_files.py生成）'
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='试运行模式，不实际修改文件'
    )
    parser.add_argument(
        '--backup',
        type=str,
        default='true',
        choices=['true', 'false'],
        help='是否备份原文件（默认true）'
    )
    parser.add_argument(
        '--output_file',
        type=str,
        default=None,
        help='执行日志输出文件路径（可选，默认输出到stdout）'
    )
    
    args = parser.parse_args()
    
    # 读取扫描结果
    try:
        with open(args.scan_result, 'r', encoding='utf-8') as f:
            scan_result = json.load(f)
    except Exception as e:
        print(f"错误：无法读取扫描结果文件：{e}")
        return 1
    
    # 解析backup参数
    backup_enabled = args.backup.lower() == 'true'
    
    # 执行整理
    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"{mode}开始执行文件整理操作...")
    
    result = organize_files(scan_result, args.dry_run, backup_enabled)
    
    # 输出结果
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"执行完成，结果已保存到：{args.output_file}")
    else:
        print(json_output)
    
    # 打印统计信息
    print(f"\n操作统计：")
    print(f"  总操作数：{result['statistics']['total_operations']}")
    print(f"  成功：{result['statistics']['successful']}")
    print(f"  失败：{result['statistics']['failed']}")
    print(f"  重命名：{result['statistics']['renamed']}")
    print(f"  移动：{result['statistics']['moved']}")
    print(f"  删除：{result['statistics']['removed']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
