"""
數據獲取模組
使用 yfinance 獲取多資產、多時間框架數據
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio


class DataFetcher:
    """
    多資產數據獲取器
    
    支持：
    - XAUUSD (黃金現貨)
    - GC=F (黃金期貨)
    - GLD (黃金 ETF)
    - ^DXY (美元指數)
    - US10Y (10 年美債)
    - VIX (恐慌指數)
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    def fetch_symbol(self, symbol: str, period: str = "1y", 
                     interval: str = "1d") -> pd.DataFrame:
        """
        獲取單一標的數據
        
        Parameters
        ----------
        symbol : str
            Yahoo Finance 代碼
        period : str
            時間範圍 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval : str
            時間間隔 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns
        -------
        pd.DataFrame
            K 線數據，columns: ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"⚠️ 警告：{symbol} 無數據返回")
                return pd.DataFrame()
            
            # 標準化 column 名稱
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return df
        
        except Exception as e:
            print(f"❌ 獲取 {symbol} 數據失敗：{e}")
            return pd.DataFrame()
    
    def fetch_multi_timeframe(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        獲取多時間框架數據
        
        Returns
        -------
        Dict[str, pd.DataFrame]
            {timeframe: DataFrame}
        """
        timeframes = {
            '1d': {'period': '1y', 'interval': '1d'},
            '4h': {'period': '3mo', 'interval': '1h'},  # yfinance 無 4h，用 1h 替代
            '1h': {'period': '1mo', 'interval': '1h'},
            '15m': {'period': '5d', 'interval': '15m'},
            '5m': {'period': '1d', 'interval': '5m'}
        }
        
        result = {}
        
        for tf, params in timeframes.items():
            df = self.fetch_symbol(symbol, **params)
            if not df.empty:
                result[tf] = df
        
        return result
    
    def fetch_related_assets(self) -> Dict[str, float]:
        """
        獲取相關資產當前價格
        
        Returns
        -------
        Dict[str, float]
            {symbol: current_price}
        """
        symbols = {
            'XAUUSD': 'XAUUSD=X',
            'GOLD_FUTURES': 'GC=F',
            'GLD': 'GLD',
            'DXY': '^DXY',
            'VIX': 'VIX'
        }
        
        prices = {}
        
        for name, symbol in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d', interval='1m')
                if not data.empty:
                    prices[name] = data['Close'].iloc[-1]
            except Exception as e:
                prices[name] = None
        
        return prices
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """獲取最新價格"""
        df = self.fetch_symbol(symbol, period='5d', interval='1m')
        if not df.empty:
            return df['close'].iloc[-1]
        return None
    
    async def fetch_async(self, symbol: str, period: str = "1y", 
                          interval: str = "1d") -> pd.DataFrame:
        """異步獲取數據"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.fetch_symbol, symbol, period, interval
        )
    
    async def fetch_all_async(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """異步獲取多個標的數據"""
        tasks = [self.fetch_async(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame):
                data[symbol] = result
            else:
                print(f"❌ {symbol} 獲取失敗：{result}")
        
        return data


# 測試用
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # 測試獲取 XAUUSD 數據
    print("📊 獲取 XAUUSD 數據...")
    df = fetcher.fetch_symbol("XAUUSD=X", period="1mo", interval="1h")
    print(f"數據形狀：{df.shape}")
    print(f"最新價格：${df['close'].iloc[-1]:.2f}")
    
    # 測試獲取相關資產
    print("\n📈 獲取相關資產價格...")
    prices = fetcher.fetch_related_assets()
    for name, price in prices.items():
        if price:
            print(f"{name}: ${price:.2f}")
