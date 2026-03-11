"""
Order Block 檢測模組
Smart Money Concept 核心組件
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class OBType(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass
class OrderBlock:
    """Order Block 數據結構"""
    ob_type: OBType
    price_low: float
    price_high: float
    midpoint: float
    timeframe: str
    formation_time: pd.Timestamp
    test_count: int = 0
    strength_score: float = 0.0
    is_valid: bool = True
    volume_at_formation: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'type': self.ob_type.value,
            'low': self.price_low,
            'high': self.price_high,
            'midpoint': self.midpoint,
            'timeframe': self.timeframe,
            'formation_time': str(self.formation_time),
            'test_count': self.test_count,
            'strength_score': self.strength_score,
            'is_valid': self.is_valid
        }


class OrderBlockDetector:
    """
    Order Block 檢測器
    
    Order Block 定義：
    - Bullish OB: 大陽線前的最後一根陰線
    - Bearish OB: 大陰線前的最後一根陽線
    """
    
    def __init__(self, atr_multiplier: float = 1.5, max_test_count: int = 3):
        self.atr_multiplier = atr_multiplier
        self.max_test_count = max_test_count
    
    def detect(self, df: pd.DataFrame, timeframe: str = "4h") -> List[OrderBlock]:
        """
        檢測 Order Block
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據，需包含 columns: ['open', 'high', 'low', 'close', 'volume']
        timeframe : str
            時間框架
        
        Returns
        -------
        List[OrderBlock]
            檢測到的 Order Block 列表
        """
        if len(df) < 10:
            return []
        
        # 計算 ATR
        df = self._calculate_atr(df, period=14)
        atr = df['ATR'].iloc[-1]
        
        order_blocks = []
        
        # 遍歷 K 線（從倒數第 3 根開始，避免最後一根不完整）
        for i in range(2, len(df) - 1):
            current = df.iloc[i]
            prev = df.iloc[i - 1]
            prev_prev = df.iloc[i - 2] if i >= 2 else None
            
            # 檢測大 K 線
            body_size = abs(current['close'] - current['open'])
            is_large_candle = body_size > (atr * self.atr_multiplier)
            
            if not is_large_candle:
                continue
            
            # 檢測 Bullish OB (大陽線前的陰線)
            if current['close'] > current['open']:  # 陽線
                if prev['close'] < prev['open']:  # 前一根是陰線
                    ob = OrderBlock(
                        ob_type=OBType.BULLISH,
                        price_low=prev['low'],
                        price_high=prev['high'],
                        midpoint=(prev['low'] + prev['high']) / 2,
                        timeframe=timeframe,
                        formation_time=prev.name,
                        volume_at_formation=prev.get('volume', 0)
                    )
                    order_blocks.append(ob)
            
            # 檢測 Bearish OB (大陰線前的陽線)
            elif current['close'] < current['open']:  # 陰線
                if prev['close'] > prev['open']:  # 前一根是陽線
                    ob = OrderBlock(
                        ob_type=OBType.BEARISH,
                        price_low=prev['low'],
                        price_high=prev['high'],
                        midpoint=(prev['low'] + prev['high']) / 2,
                        timeframe=timeframe,
                        formation_time=prev.name,
                        volume_at_formation=prev.get('volume', 0)
                    )
                    order_blocks.append(ob)
        
        # 計算每個 OB 的強度評分
        for ob in order_blocks:
            ob.strength_score = self._calculate_strength(ob, df)
        
        return order_blocks
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """計算 ATR"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=period).mean()
        
        return df
    
    def _calculate_strength(self, ob: OrderBlock, df: pd.DataFrame) -> float:
        """
        計算 OB 強度評分
        
        評分因子：
        - 未測試次數 (30%): 0 次=100 分，每測試 1 次 -25 分
        - 形成時成交量 (25%): 相對均量倍率
        - 時間框架 (25%): HTF 權重更高
        - 後續 BOS (20%): 有 BOS 確認=有效
        """
        score = 0.0
        
        # 1. 未測試次數評分 (30%)
        test_score = max(0, 100 - (ob.test_count * 25))
        score += test_score * 0.30
        
        # 2. 成交量評分 (25%)
        if 'volume' in df.columns and ob.volume_at_formation > 0:
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            if avg_volume > 0:
                volume_ratio = ob.volume_at_formation / avg_volume
                volume_score = min(100, volume_ratio * 50)  # 2 倍均量=100 分
                score += volume_score * 0.25
        
        # 3. 時間框架評分 (25%)
        tf_scores = {
            '1mo': 100, '1wk': 95, '1d': 90,
            '4h': 80, '1h': 70, '15m': 60, '5m': 50
        }
        tf_score = tf_scores.get(ob.timeframe, 50)
        score += tf_score * 0.25
        
        # 4. BOS 確認評分 (20%) - 簡化版本，假設有 BOS=100 分
        # 實際實現需要檢查後續價格是否突破結構
        bos_score = 80  # 預設值
        score += bos_score * 0.20
        
        return score
    
    def check_price_reaction(self, ob: OrderBlock, current_price: float) -> str:
        """
        檢查價格與 OB 的互動
        
        Returns
        -------
        str: 'inside' (在 OB 內), 'above' (上方), 'below' (下方), 'testing' (測試中)
        """
        tolerance = (ob.price_high - ob.price_low) * 0.01  # 1% 容差
        
        if ob.price_low - tolerance <= current_price <= ob.price_high + tolerance:
            return 'testing'
        elif ob.ob_type == OBType.BULLISH:
            if current_price > ob.price_high:
                return 'above'
            else:
                return 'below'
        else:  # BEARISH
            if current_price < ob.price_low:
                return 'below'
            else:
                return 'above'
    
    def invalidate_ob(self, ob: OrderBlock, current_price: float) -> bool:
        """
        檢查 OB 是否失效
        
        Bullish OB: 收盤跌破低點 → 失效
        Bearish OB: 收盤突破高點 → 失效
        """
        if ob.ob_type == OBType.BULLISH:
            if current_price < ob.price_low:
                ob.is_valid = False
                return True
        else:  # BEARISH
            if current_price > ob.price_high:
                ob.is_valid = False
                return True
        
        return False
