"""
UAV配置管理工具

此模块提供了一组函数和命令行接口，用于管理UAV模块的配置文件。
它允许用户创建、重置、更新和查看配置。
"""

import os
import json
import argparse
from typing import Dict, Any, Optional
from .settings import get_current_config, save_config, CONFIG_FILE, DEFAULT_CONFIG_FILE

def create_default_config() -> bool:
    """创建默认配置文件
    
    将当前配置保存为默认配置文件，以便在需要时重置配置。
    
    Returns:
        bool: 是否成功创建默认配置文件
    """
    config = get_current_config()
    if save_config(config, DEFAULT_CONFIG_FILE):
        print(f"默认配置已保存到 {DEFAULT_CONFIG_FILE}")
        return True
    else:
        print("保存默认配置失败")
        return False

def reset_config() -> bool:
    """重置配置为默认值
    
    从默认配置文件加载配置并保存到主配置文件。
    
    Returns:
        bool: 是否成功重置配置
    """
    if os.path.exists(DEFAULT_CONFIG_FILE):
        with open(DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            default_config = json.load(f)
        
        if save_config(default_config, CONFIG_FILE):
            print(f"配置已重置为默认值")
            return True
        else:
            print("重置配置失败")
            return False
    else:
        print(f"默认配置文件 {DEFAULT_CONFIG_FILE} 不存在")
        return False

def update_config(key_path: str, value: Any) -> bool:
    """更新配置中的特定值
    
    Args:
        key_path: 键路径，如 "paths.base_dir"
        value: 新值
    
    Returns:
        bool: 是否成功更新配置
    
    Examples:
        >>> update_config("data_params.patch_size", "128")
        配置已更新: data_params.patch_size = 128
        True
    """
    # 加载当前配置
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 解析键路径
    keys = key_path.split('.')
    
    # 递归更新配置
    current = config
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            # 最后一个键，更新值
            current[key] = value
        else:
            # 确保中间键存在
            if key not in current:
                current[key] = {}
            current = current[key]
    
    # 保存更新后的配置
    if save_config(config, CONFIG_FILE):
        print(f"配置已更新: {key_path} = {value}")
        return True
    else:
        print("更新配置失败")
        return False

def show_config() -> Optional[Dict[str, Any]]:
    """显示当前配置
    
    打印当前配置内容，并返回配置字典。
    
    Returns:
        Optional[Dict[str, Any]]: 当前配置字典，如果配置文件不存在则返回None
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("当前配置:")
        print(json.dumps(config, indent=4, ensure_ascii=False))
        return config
    else:
        print(f"配置文件 {CONFIG_FILE} 不存在")
        return None

def main() -> None:
    """命令行入口点
    
    提供命令行接口，用于管理配置文件。
    """
    parser = argparse.ArgumentParser(description='UAV配置管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 创建默认配置命令
    create_parser = subparsers.add_parser('create-default', help='创建默认配置文件')
    
    # 重置配置命令
    reset_parser = subparsers.add_parser('reset', help='重置配置为默认值')
    
    # 更新配置命令
    update_parser = subparsers.add_parser('update', help='更新配置')
    update_parser.add_argument('key_path', help='键路径，如 "paths.base_dir"')
    update_parser.add_argument('value', help='新值')
    
    # 显示配置命令
    show_parser = subparsers.add_parser('show', help='显示当前配置')
    
    args = parser.parse_args()
    
    if args.command == 'create-default':
        create_default_config()
    elif args.command == 'reset':
        reset_config()
    elif args.command == 'update':
        update_config(args.key_path, args.value)
    elif args.command == 'show':
        show_config()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()