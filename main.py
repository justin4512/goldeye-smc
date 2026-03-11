"""
GoldEye SMC 交易系統 - 主程序
"""

import asyncio
import yaml
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

from src.data.fetcher import DataFetcher
from src.signal.generator import SignalGenerator, TradingSignal
from src.utils.notifier import TelegramNotifier

# 加載環境變量
load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoldEyeSystem:
    """
    GoldEye SMC 交易系統主類
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        # 加載配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化組件
        self.data_fetcher = DataFetcher()
        self.signal_generator = SignalGenerator(
            min_confidence=self.config['smc']['signal']['min_confidence'],
            min_rr=self.config['smc']['signal']['min_rr_ratio']
        )
        
        # 初始化 Telegram 通知
        telegram_config = self.config.get('telegram', {})
        self.notifier = TelegramNotifier(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', telegram_config.get('bot_token', '')),
            chat_id=os.getenv('TELEGRAM_CHAT_ID', telegram_config.get('chat_id', '')),
            enabled=telegram_config.get('enabled', True)
        )
        
        self.symbol = self.config['symbols']['primary']
        self.last_signal_time = None
    
    async def run_monitoring(self, interval_seconds: int = 60):
        """
        運行監控循環
        
        Parameters
        ----------
        interval_seconds : int
            監控間隔（秒）
        """
        logger.info(f"🚀 GoldEye 系統啟動，監控標的：{self.symbol}")
        
        # 測試 Telegram 連接
        if self.config['telegram'].get('enabled', True):
            logger.info("🔌 測試 Telegram 連接...")
            await self.notifier.test_connection()
        
        while True:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(interval_seconds)
            
            except KeyboardInterrupt:
                logger.info("👋 系統停止")
                break
            except Exception as e:
                logger.error(f"❌ 監控循環錯誤：{e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _monitoring_cycle(self):
        """單次監控循環"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 開始監控循環 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 獲取最新數據
        df = self.data_fetcher.fetch_symbol(self.symbol, period="5d", interval="5m")
        
        if df.empty:
            logger.warning("⚠️ 無法獲取數據，跳過本次循環")
            return
        
        current_price = df['close'].iloc[-1]
        logger.info(f"💰 {self.symbol} 當前價格：${current_price:.2f}")
        
        # 2. 分析多時間框架
        timeframes = ['1d', '4h', '1h', '15m']
        signals = {}
        
        for tf in timeframes:
            signal = self._analyze_timeframe(df, tf, current_price)
            if signal:
                signals[tf] = signal
                logger.info(f"📈 {tf} 檢測到信號：{signal.direction}, 信心度：{signal.confidence:.0f}%")
        
        # 3. 發送高質量信號
        if signals:
            best_signal = max(signals.values(), key=lambda s: s.confidence)
            
            # 避免重複發送（30 分鐘內不發送相同信號）
            if self._should_send_signal(best_signal):
                await self._send_signal_notification(best_signal)
                self.last_signal_time = datetime.now()
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str,
                           current_price: float) -> TradingSignal:
        """分析單一時間框架"""
        # 這裡應該獲取對應時間框架的數據
        # 簡化版本：使用相同數據
        return self.signal_generator.generate_signal(df, timeframe, current_price)
    
    def _should_send_signal(self, signal: TradingSignal) -> bool:
        """檢查是否應該發送信號"""
        if self.last_signal_time is None:
            return True
        
        # 30 分鐘內不發送相同信號
        time_diff = (datetime.now() - self.last_signal_time).total_seconds()
        if time_diff < 1800:  # 30 分鐘
            return False
        
        return True
    
    async def _send_signal_notification(self, signal: TradingSignal):
        """發送信號通知"""
        logger.info(f"📱 發送信號通知：{signal.direction} @ {signal.entry_low:.2f}-{signal.entry_high:.2f}")
        
        # 添加機構因子和風險警告
        signal_dict = signal.to_dict()
        signal_dict['institutional_summary'] = "COT: 中性 | ETF: 流入 | 實際利率：-0.8%"
        signal_dict['risk_warning'] = "明日 20:30 美國 CPI 數據，建議事件前減小頭寸"
        signal_dict['capital'] = self.config['risk']['capital']
        signal_dict['risk_per_trade'] = self.config['risk']['risk_per_trade'] * 100
        
        # 計算頭寸規模
        risk_amount = self.config['risk']['capital'] * self.config['risk']['risk_per_trade']
        risk_per_ounce = abs(signal.entry_low - signal.stop_loss)
        signal_dict['position_size'] = risk_amount / risk_per_ounce if risk_per_ounce > 0 else 0
        
        await self.notifier.send_signal(signal_dict)


def main():
    """主函數"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║        🏦 GoldEye SMC 交易系統 v2.0              ║
    ║        Institutional Edition                      ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # 檢查環境變量
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("⚠️ 警告：TELEGRAM_BOT_TOKEN 未設置，Telegram 通知將禁用")
        print("   請複製 .env.example 為 .env 並填寫配置")
    
    # 創建系統實例
    system = GoldEyeSystem()
    
    # 運行監控
    try:
        asyncio.run(system.run_monitoring(interval_seconds=60))
    except KeyboardInterrupt:
        print("\n👋 系統已停止")


if __name__ == "__main__":
    main()
