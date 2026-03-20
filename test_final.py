#!/usr/bin/env python3
"""完整的推送流程测试"""

import json
from pathlib import Path
from daily_push import JapaneseDailyPush

# 初始化
pusher = JapaneseDailyPush()

print("=" * 60)
print("📚 日语学习推送系统测试")
print("=" * 60)
print(f"✓ 当前天数: {pusher.current_day}")
print(f"✓ 课程总数: {len(pusher.syllabus)}")
print()

# 显示即将推送的内容
day_content = pusher.get_day_content(pusher.current_day)
if day_content:
    print("📖 即将推送的内容:")
    print(f"  - 天数: 第 {day_content['day']} 天")
    print(f"  - 课程: {day_content['lesson']}")
    print(f"  - 词汇: {', '.join(day_content['words'])}")
    print(f"  - 语法: {day_content['grammar']}")
    print()

    # 执行推送
    print("=" * 60)
    print("🚀 开始推送...")
    print("=" * 60)
    success = pusher.run()

    if success:
        print()
        print("=" * 60)
        print("✅ 推送成功！")
        print("=" * 60)

        # 读取更新后的状态
        with open(pusher.state_file, 'r') as f:
            new_day = int(f.read().strip())
        print(f"✓ 状态已更新: 第 {pusher.current_day - 1} 天 → 第 {new_day} 天")
        print()
        print("下次运行将推送第 {} 天的内容".format(new_day))
else:
    print("❌ 无法获取内容，可能已完成所有课程")
