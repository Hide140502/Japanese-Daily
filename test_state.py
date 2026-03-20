#!/usr/bin/env python3
"""测试状态管理是否正常工作"""

from pathlib import Path

# 模拟多次运行
state_file = Path("/home/siesta/japanese_daily/current_day.txt")

print("=" * 60)
print("测试状态管理逻辑")
print("=" * 60)

for run in range(1, 6):
    print(f"\n🔄 模拟第 {run} 次运行:")

    # 读取当前状态
    if state_file.exists():
        with open(state_file, 'r') as f:
            current_day = int(f.read().strip())
    else:
        current_day = 1

    print(f"  📖 读取状态: 第 {current_day} 天")

    # 模拟推送内容
    print(f"  📤 推送内容: 第 {current_day} 天")

    # 更新状态
    next_day = current_day + 1
    with open(state_file, 'w') as f:
        f.write(str(next_day))

    print(f"  ✅ 更新状态: 第 {next_day} 天")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print(f"\n最终状态: 第 {state_file.read_text().strip()} 天")
