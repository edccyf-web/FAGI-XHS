#!/usr/bin/env python3
"""
yuwen-publish-precheck — 词面预检扫描脚本

用法:
    python3 scripts/scan.py --file <稿件路径> [--commercial] [--industry medical,finance]

输出:
    风险候选列表（命中词、位置、对应规则、优先级）
    辟谣提示（用户自我审查的冤枉词）
    我的规则命中（个人词库命中）

说明:
    本脚本为框架占位文件。完整扫描逻辑依赖 data/my-rules.md 和 references/*.md 中的规则定义。
    实际使用时需实现：
    1. 读取稿件内容
    2. 读取 data/my-rules.md 黑名单表
    3. 对每个黑名单词进行关键词/正则匹配
    4. 输出匹配结果
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='词面预检扫描')
    parser.add_argument('--file', required=True, help='稿件文件路径')
    parser.add_argument('--commercial', action='store_true', help='有商业属性')
    parser.add_argument('--industry', help='涉监管行业，逗号分隔（medical,finance）')
    args = parser.parse_args()

    # 占位：实际使用时加载稿件和规则库
    print(f"[占位] 扫描文件: {args.file}")
    print(f"[占位] 商业属性: {args.commercial}")
    print(f"[占位] 涉监管行业: {args.industry}")
    print("[占位] 风险候选: 无（扫描逻辑待实现）")
    print("[占位] 辟谣提示: 无")
    print("[占位] 我的规则命中: 无")

    return 0


if __name__ == '__main__':
    sys.exit(main())
