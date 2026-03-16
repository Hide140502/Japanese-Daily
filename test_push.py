#!/usr/bin/env python3
"""
配置测试脚本 - 验证配置是否正确
"""

import sys
from pathlib import Path


def test_config():
    """测试配置文件"""
    print("🔍 测试配置文件...")

    config_file = Path(__file__).parent / "config.py"
    if not config_file.exists():
        print("❌ 配置文件不存在！")
        print("   请执行: cp config.example.py config.py")
        print("   然后编辑 config.py 填入你的配置")
        return False

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_file)
        if spec is None or spec.loader is None:
            print("❌ 配置文件加载失败")
            return False

        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        # 检查必要配置
        checks = [
            ("LLM_API_BASE", getattr(config, 'LLM_API_BASE', None)),
            ("LLM_API_KEY", getattr(config, 'LLM_API_KEY', None)),
            ("FEISHU_WEBHOOK_URL", getattr(config, 'FEISHU_WEBHOOK_URL', None)),
        ]

        all_ok = True
        for name, value in checks:
            if not value or value.startswith("your-"):
                print(f"❌ {name} 未配置或使用默认值")
                all_ok = False
            else:
                # 隐藏敏感信息
                display = value[:20] + "..." if len(value) > 20 else value
                if "KEY" in name or "WEBHOOK" in name:
                    display = value[:8] + "****" + value[-4:] if len(value) > 12 else "****"
                print(f"✓ {name}: {display}")

        if all_ok:
            print("\n✅ 配置检查通过！")
            return True
        else:
            print("\n❌ 请完善配置后重试")
            return False

    except Exception as e:
        print(f"❌ 配置文件解析失败: {e}")
        return False


def test_syllabus():
    """测试课程大纲"""
    print("\n🔍 测试课程大纲...")

    syllabus_file = Path(__file__).parent / "syllabus.json"
    if not syllabus_file.exists():
        print("❌ syllabus.json 不存在")
        return False

    try:
        import json
        with open(syllabus_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # 处理可能的代码块
        if content.startswith('```'):
            content = content.strip().strip('```').strip()
            if content.lower().startswith('json'):
                content = content[4:].strip()
            syllabus = json.loads(content)
        else:
            syllabus = json.loads(content)

        print(f"✓ 课程大纲加载成功")
        print(f"✓ 共 {len(syllabus)} 天课程")

        # 检查第一天内容
        if syllabus:
            first_day = syllabus[0]
            print(f"✓ 第一天: {first_day.get('grammar', 'N/A')}")
            print(f"  词汇: {', '.join(first_day.get('words', []))}")

        return True

    except Exception as e:
        print(f"❌ 课程大纲加载失败: {e}")
        return False


def test_dependencies():
    """测试依赖"""
    print("\n🔍 测试依赖...")

    try:
        import requests
        print(f"✓ requests {requests.__version__}")
        return True
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        print("   请执行: pip install -r requirements.txt")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 日语学习推送系统 - 配置测试")
    print("=" * 50)

    results = [
        test_dependencies(),
        test_config(),
        test_syllabus(),
    ]

    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有测试通过！可以开始使用了")
        print("   运行推送: python daily_push.py")
        return 0
    else:
        print("❌ 部分测试失败，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
