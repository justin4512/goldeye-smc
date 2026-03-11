"""
Telegram 通知模組
發送交易信號、警告、報告到 Telegram
"""

import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram 通知器
    
    功能：
    - 發送交易信號
    - 發送警告通知
    - 發送每日/週度報告
    - 緊急通知
    """
    
    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled
        self.bot = Bot(token=bot_token) if enabled else None
    
    async def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        發送消息
        
        Parameters
        ----------
        message : str
            消息內容
        parse_mode : str
            解析模式 (Markdown, HTML)
        
        Returns
        -------
        bool
            發送成功與否
        """
        if not self.enabled:
            logger.info("Telegram 通知已禁用")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("✅ Telegram 消息發送成功")
            return True
        except TelegramError as e:
            logger.error(f"❌ Telegram 發送失敗：{e}")
            return False
        except Exception as e:
            logger.error(f"❌ 未知錯誤：{e}")
            return False
    
    def send_sync(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """同步發送消息"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_message(message, parse_mode))
    
    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """
        發送交易信號
        
        Parameters
        ----------
        signal : dict
            信號數據，包含：
            - direction: 做多/做空
            - confidence: 信心度
            - entry_low, entry_high: 進場區間
            - stop_loss: 止損價
            - target_1, target_2: 目標價
            - smc_logic: SMC 邏輯說明
            - institutional_factors: 機構因子
            - risk_factors: 風險因子
            - position_size: 建議頭寸
        """
        message = f"""
🏦 *GoldEye SMC 信號*

📊 *方向*：{signal.get('direction', 'N/A')}
💯 *信心度*：{signal.get('confidence', 0)}%
⏰ *時間框架*：{signal.get('timeframe', 'N/A')}

📍 *進場區間*：${signal.get('entry_low', 0):.2f} ~ ${signal.get('entry_high', 0):.2f}
🛑 *止損*：${signal.get('stop_loss', 0):.2f} ({signal.get('risk_pct', 0):.2f}%)
🎯 *目標 1*：${signal.get('target_1', 0):.2f} (R:R = {signal.get('rr_1', 0):.1f})
🎯 *目標 2*：${signal.get('target_2', 0):.2f} (R:R = {signal.get('rr_2', 0):.1f})

🔍 *SMC 邏輯*：
{signal.get('smc_logic', 'N/A')}

📈 *機構因子*：
{signal.get('institutional_summary', 'N/A')}

⚠️ *風險*：
{signal.get('risk_warning', 'N/A')}

📋 *頭寸建議*：
- 資本：${signal.get('capital', 100000):,.0f}
- 風險%：{signal.get('risk_per_trade', 1)}%
- 建議頭寸：{signal.get('position_size', 0):.1f} 盎司

_免責聲明：本信號僅供參考，不構成投資建議。交易有風險，請自行判斷。_
"""
        return await self.send_message(message)
    
    async def send_alert(self, alert_type: str, message: str) -> bool:
        """
        發送警告通知
        
        Parameters
        ----------
        alert_type : str
            警告類型 (stop_loss, target_reached, ob_invalid, emergency)
        message : str
            警告內容
        """
        emoji = {
            'stop_loss': '🛑',
            'target_reached': '🎯',
            'ob_invalid': '⚠️',
            'emergency': '🚨',
            'system': '🔧'
        }
        
        formatted = f"""
{emoji.get(alert_type, '⚠️')} *GoldEye {alert_type.replace('_', ' ').title()}*

{message}

_時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}_
"""
        return await self.send_message(formatted)
    
    async def send_daily_report(self, report: Dict[str, Any]) -> bool:
        """
        發送每日盤面報告
        
        Parameters
        ----------
        report : dict
            報告數據，包含：
            - date: 日期
            - open, high, low, close: 當日走勢
            - active_positions: 活躍頭寸
            - key_levels: 關鍵價位
            - events: 明日風險事件
        """
        message = f"""
📊 *GoldEye 每日盤面報告*
📅 {report.get('date', datetime.now().strftime('%Y-%m-%d'))}

📈 *XAUUSD 走勢*
開：${report.get('open', 0):.2f} | 高：${report.get('high', 0):.2f}
低：${report.get('low', 0):.2f} | 收：${report.get('close', 0):.2f}
漲跌：{report.get('change_pct', 0):+.2f}%

🔑 *關鍵價位*
阻力：{', '.join([f'${l:.2f}' for l in report.get('resistance', [])])}
支撐：{', '.join([f'${l:.2f}' for l in report.get('support', [])])}

📋 *活躍頭寸*
{report.get('positions_summary', '無活躍頭寸')}

📅 *明日風險事件*
{report.get('events', '無重大事件')}

_祝交易順利！_
"""
        return await self.send_message(message)
    
    async def test_connection(self) -> bool:
        """測試 Telegram 連接"""
        try:
            await self.bot.get_me()
            logger.info("✅ Telegram Bot 連接成功")
            
            # 發送測試消息
            await self.send_message("✅ GoldEye 系統測試 - Telegram 連接正常")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram Bot 連接失敗：{e}")
            return False


# 測試用
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        # 測試連接
        print("🔌 測試 Telegram 連接...")
        success = notifier.send_sync("👋 GoldEye 系統測試")
        
        if success:
            print("✅ Telegram 通知測試成功")
        else:
            print("❌ Telegram 通知測試失敗")
    else:
        print("⚠️ 請設置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 環境變量")
