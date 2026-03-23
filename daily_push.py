#!/usr/bin/env python3
"""
日语学习每日推送脚本

功能：
1. 读取 syllabus.json 获取当天学习内容
2. 调用 LLM API 生成教学内容
3. 推送到飞书群组
4. 更新学习天数
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import requests

# ==================== 配置日志 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('daily_push.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class JapaneseDailyPush:
    """日语学习每日推送核心类"""

    def __init__(self, base_dir: Optional[Path] = None):
        """初始化配置

        Args:
            base_dir: 项目根目录，默认为脚本所在目录
        """
        if base_dir is None:
            self.base_dir = Path(__file__).parent
        else:
            self.base_dir = Path(base_dir)

        # 文件路径
        self.syllabus_file = self.base_dir / "syllabus.json"
        self.state_file = self.base_dir / "current_day.txt"
        self.config_file = self.base_dir / "config.py"
        self.kana_file = self.base_dir / "kana_data.json"

        # 加载配置
        self._load_config()

        # 状态管理
        self.current_day = self._load_current_day()
        self.syllabus = self._load_syllabus()
        self.kana_data = self._load_kana_data()

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            # 动态导入配置
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", self.config_file)
            if spec is None or spec.loader is None:
                raise FileNotFoundError(f"配置文件不存在: {self.config_file}")

            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)

            self.llm_api_base = getattr(config, 'LLM_API_BASE', '')
            self.llm_api_key = getattr(config, 'LLM_API_KEY', '')
            self.llm_model = getattr(config, 'LLM_MODEL', 'gpt-4o-mini')
            self.feishu_webhook = getattr(config, 'FEISHU_WEBHOOK_URL', '')
            self.system_prompt_template = getattr(config, 'SYSTEM_PROMPT', '')

            # 验证必要配置
            if not self.llm_api_key:
                raise ValueError("LLM_API_KEY 未配置")
            if not self.feishu_webhook:
                raise ValueError("FEISHU_WEBHOOK_URL 未配置")

            logger.info("✓ 配置加载成功")

        except Exception as e:
            logger.error(f"✗ 配置加载失败: {e}")
            raise

    def _load_current_day(self) -> int:
        """加载当前学习天数

        Returns:
            当前学习天数，如果文件不存在则返回 1
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    day = int(f.read().strip())
                    logger.info(f"✓ 当前学习进度: 第 {day} 天")
                    return day
            else:
                # 首次运行，创建初始文件
                self._save_current_day(1)
                return 1
        except Exception as e:
            logger.error(f"✗ 读取状态文件失败: {e}")
            return 1

    def _save_current_day(self, day: int) -> None:
        """保存当前学习天数

        Args:
            day: 学习天数
        """
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                f.write(str(day))
            logger.debug(f"状态已更新: 第 {day} 天")
        except Exception as e:
            logger.error(f"✗ 保存状态文件失败: {e}")
            raise

    def _load_syllabus(self) -> List[Dict]:
        """加载课程大纲

        Returns:
            课程列表
        """
        try:
            with open(self.syllabus_file, 'r', encoding='utf-8') as f:
                syllabus = json.load(f)

            # 处理可能的代码块包裹
            if isinstance(syllabus, str) and syllabus.startswith('```'):
                # 去掉 markdown 代码块标记
                syllabus = syllabus.strip().strip('```').strip()
                if syllabus.lower().startswith('json'):
                    syllabus = syllabus[4:].strip()
                syllabus = json.loads(syllabus)

            logger.info(f"✓ 加载课程大纲: 共 {len(syllabus)} 天")
            return syllabus
        except Exception as e:
            logger.error(f"✗ 加载课程大纲失败: {e}")
            raise

    def _load_kana_data(self) -> List[Dict]:
        """加载五十音数据

        Returns:
            五十音列表
        """
        try:
            with open(self.kana_file, 'r', encoding='utf-8') as f:
                kana_data = json.load(f)

            logger.info(f"✓ 加载五十音数据: 共 {len(kana_data)} 个")
            return kana_data
        except Exception as e:
            logger.error(f"✗ 加载五十音数据失败: {e}")
            # 如果加载失败，返回空列表
            return []

    def get_day_content(self, day: int) -> Optional[Dict]:
        """获取指定天的学习内容

        Args:
            day: 学习天数

        Returns:
            当天的学习内容，如果超出范围返回 None
        """
        # syllabus 是 0-indexed，day 是 1-indexed
        index = day - 1
        if 0 <= index < len(self.syllabus):
            content = self.syllabus[index]
            logger.info(f"✓ 获取第 {day} 天内容: {content['grammar']}")
            return content
        else:
            logger.warning(f"第 {day} 天超出课程范围")
            return None

    def get_kana_of_day(self, day: int) -> Optional[Dict]:
        """获取指定天的五十音复习内容

        Args:
            day: 学习天数

        Returns:
            当天的五十音数据，如果超出范围返回 None
        """
        if not self.kana_data:
            return None

        # kana_data 是 1-indexed（day 字段从 1 开始）
        for kana in self.kana_data:
            if kana['day'] == day:
                logger.info(f"✓ 五十音复习: {kana['hiragana']} ({kana['romaji']})")
                return kana

        # 如果没有匹配的 day，使用循环取模
        index = (day - 1) % len(self.kana_data)
        return self.kana_data[index]

    def generate_content(self, day_content: Dict) -> str:
        """调用 LLM API 生成教学内容

        Args:
            day_content: 当天的学习内容

        Returns:
            生成的 Markdown 格式教学内容
        """
        try:
            # 获取当天的五十音复习内容
            kana_data = self.get_kana_of_day(day_content['day'])
            kana_str = ""
            if kana_data:
                kana_str = f"{kana_data['hiragana']} / {kana_data['katakana']} ({kana_data['romaji']}) - {kana_data['type']}"

            # 构建提示词
            words_str = "、".join(day_content['words'])
            prompt = self.system_prompt_template.format(
                day=day_content['day'],
                lesson=day_content['lesson'],
                words=words_str,
                grammar=day_content['grammar'],
                kana=kana_str
            )

            logger.info("正在调用 LLM API 生成内容...")

            # 调用 API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.llm_api_key}"
            }

            payload = {
                "model": self.llm_model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请生成第{day_content['day']}天的日语学习内容"}
                ],
                "temperature": 0.8,
                "max_tokens": 4000
            }

            response = requests.post(
                f"{self.llm_api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            logger.info("✓ 内容生成成功")
            return content

        except requests.exceptions.Timeout:
            logger.error("✗ LLM API 请求超时")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ LLM API 请求失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"✗ LLM API 响应格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ 生成内容失败: {e}")
            raise

    def send_to_feishu(self, content: str) -> None:
        """推送内容到飞书群组

        Args:
            content: Markdown 格式的教学内容
        """
        try:
            logger.info("正在推送到飞书...")

            # 飞书 Webhook 格式
            payload = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"📚 日语学习打卡 - 第 {self.current_day} 天"
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": content
                            }
                        },
                        {
                            "tag": "hr"
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "plain_text",
                                "content": f"📅 推送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        }
                    ]
                }
            }

            response = requests.post(
                self.feishu_webhook,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info("✓ 飞书推送成功")

        except requests.exceptions.Timeout:
            logger.error("✗ 飞书推送超时")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ 飞书推送失败: {e}")
            # 如果是 JSON 格式的错误响应，打印详细信息
            try:
                error_detail = response.json()
                logger.error(f"错误详情: {error_detail}")
            except:
                logger.error(f"响应内容: {response.text}")
            raise

    def run(self) -> bool:
        """执行每日推送任务

        Returns:
            是否成功完成
        """
        try:
            logger.info("=" * 50)
            logger.info(f"开始执行第 {self.current_day} 天推送任务")
            logger.info("=" * 50)

            # 1. 获取当天内容
            day_content = self.get_day_content(self.current_day)
            if day_content is None:
                # 已完成所有课程
                completion_msg = (
                    "🎉 恭喜！你已经完成了所有90天的日语学习课程！\n\n"
                    "这真是一段了不起的旅程！🌟\n\n"
                    "接下来可以：\n"
                    "1. 复习薄弱知识点\n"
                    "2. 开始学习 N4 级别内容\n"
                    "3. 多看动漫、日剧巩固所学\n\n"
                    "持续学习，终将精通！がんばって！💪"
                )
                self._send_completion_message(completion_msg)
                return True

            # 2. 生成内容
            generated_content = self.generate_content(day_content)

            # 3. 推送到飞书
            self.send_to_feishu(generated_content)

            # 4. 更新状态（只有成功后才更新）
            next_day = self.current_day + 1
            if next_day <= len(self.syllabus):
                self._save_current_day(next_day)
                logger.info(f"✓ 状态已更新: 下次将是第 {next_day} 天")
            else:
                logger.info("✓ 已完成所有课程")

            logger.info("=" * 50)
            logger.info("✓ 推送任务完成")
            logger.info("=" * 50)

            return True

        except Exception as e:
            logger.error("=" * 50)
            logger.error(f"✗ 推送任务失败: {e}")
            logger.error("=" * 50)
            return False

    def _send_completion_message(self, message: str) -> None:
        """发送完成消息

        Args:
            message: 完成消息内容
        """
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }

            response = requests.post(
                self.feishu_webhook,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info("✓ 完成消息已发送")

        except Exception as e:
            logger.error(f"✗ 发送完成消息失败: {e}")


def main():
    """主函数"""
    try:
        pusher = JapaneseDailyPush()
        success = pusher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
