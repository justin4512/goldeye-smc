"""
市場結構分析模組 (BOS / CHoCH)
Smart Money Concept 核心組件
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TrendDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    RANGING = "ranging"


class StructureType(Enum):
    HH = "HH"  # Higher High
    HL = "HL"  # Higher Low
    LH = "LH"  # Lower High
    LL = "LL"  # Lower Low


@dataclass
class MarketStructure:
    """市場結構數據"""
    structure_type: StructureType
    price: float
    time: pd.Timestamp
    confirmed: bool = True


@dataclass
class BOS:
    """Break of Structure"""
    direction: TrendDirection
    breakout_price: float
    breakout_time: pd.Timestamp
    previous_structure: MarketStructure
    confirmed: bool = True


@dataclass
class CHoCH:
    """Change of Character"""
    from_trend: TrendDirection
    to_trend: TrendDirection
    break_price: float
    break_time: pd.Timestamp
    confirmed: bool = True


class StructureAnalyzer:
    """
    市場結構分析器
    
    功能：
    - 識別 HH, HL, LH, LL
    - 檢測 BOS (Break of Structure)
    - 檢測 CHoCH (Change of Character)
    """
    
    def __init__(self, swing_lookback: int = 5):
        self.swing_lookback = swing_lookback
    
    def detect_swing_points(self, df: pd.DataFrame) -> Tuple[List[MarketStructure], List[MarketStructure]]:
        """
        檢測 Swing Highs 和 Swing Lows
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據，需包含 columns: ['high', 'low']
        
        Returns
        -------
        Tuple[List[MarketStructure], List[MarketStructure]]
            (Swing Highs, Swing Lows)
        """
        swing_highs = []
        swing_lows = []
        
        for i in range(self.swing_lookback, len(df) - self.swing_lookback):
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            
            # 檢測 Swing High
            left_highs = df['high'].iloc[i-self.swing_lookback:i]
            right_highs = df['high'].iloc[i+1:i+self.swing_lookback+1]
            
            if current_high > left_highs.max() and current_high > right_highs.max():
                swing_highs.append(MarketStructure(
                    structure_type=StructureType.HH,  # 暫時標記，後續會更新
                    price=current_high,
                    time=df.index[i]
                ))
            
            # 檢測 Swing Low
            left_lows = df['low'].iloc[i-self.swing_lookback:i]
            right_lows = df['low'].iloc[i+1:i+self.swing_lookback+1]
            
            if current_low < left_lows.min() and current_low < right_lows.min():
                swing_lows.append(MarketStructure(
                    structure_type=StructureType.LL,  # 暫時標記，後續會更新
                    price=current_low,
                    time=df.index[i]
                ))
        
        return swing_highs, swing_lows
    
    def identify_trend(self, swing_highs: List[MarketStructure], 
                       swing_lows: List[MarketStructure]) -> TrendDirection:
        """
        識別趨勢方向
        
        Returns
        -------
        TrendDirection: BULLISH / BEARISH / RANGING
        """
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return TrendDirection.RANGING
        
        # 檢查高點和低點是否墊高
        recent_hh = swing_highs[-1].price > swing_highs[-2].price
        recent_hl = swing_lows[-1].price > swing_lows[-2].price
        
        # 檢查高點和低點是否降低
        recent_lh = swing_highs[-1].price < swing_highs[-2].price
        recent_ll = swing_lows[-1].price < swing_lows[-2].price
        
        if recent_hh and recent_hl:
            return TrendDirection.BULLISH
        elif recent_lh and recent_ll:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.RANGING
    
    def detect_bos(self, df: pd.DataFrame, swing_highs: List[MarketStructure],
                   swing_lows: List[MarketStructure], 
                   current_trend: TrendDirection) -> Optional[BOS]:
        """
        檢測 Break of Structure
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據
        swing_highs : List[MarketStructure]
            Swing Highs
        swing_lows : List[MarketStructure]
            Swing Lows
        current_trend : TrendDirection
            當前趨勢
        
        Returns
        -------
        Optional[BOS]
            檢測到的 BOS，如果沒有則返回 None
        """
        if len(df) < 2:
            return None
        
        current_price = df['close'].iloc[-1]
        current_time = df.index[-1]
        
        if current_trend == TrendDirection.BULLISH and len(swing_highs) > 0:
            # 檢查是否突破前高
            previous_high = swing_highs[-1].price
            
            if current_price > previous_high:
                return BOS(
                    direction=TrendDirection.BULLISH,
                    breakout_price=current_price,
                    breakout_time=current_time,
                    previous_structure=swing_highs[-1],
                    confirmed=True
                )
        
        elif current_trend == TrendDirection.BEARISH and len(swing_lows) > 0:
            # 檢查是否跌破前低
            previous_low = swing_lows[-1].price
            
            if current_price < previous_low:
                return BOS(
                    direction=TrendDirection.BEARISH,
                    breakout_price=current_price,
                    breakout_time=current_time,
                    previous_structure=swing_lows[-1],
                    confirmed=True
                )
        
        return None
    
    def detect_choch(self, df: pd.DataFrame, swing_highs: List[MarketStructure],
                     swing_lows: List[MarketStructure],
                     current_trend: TrendDirection) -> Optional[CHoCH]:
        """
        檢測 Change of Character
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據
        swing_highs : List[MarketStructure]
            Swing Highs
        swing_lows : List[MarketStructure]
            Swing Lows
        current_trend : TrendDirection
            當前趨勢
        
        Returns
        -------
        Optional[CHoCH]
            檢測到的 CHoCH，如果沒有則返回 None
        """
        if len(df) < 2:
            return None
        
        current_price = df['close'].iloc[-1]
        current_time = df.index[-1]
        
        if current_trend == TrendDirection.BULLISH:
            # 上升趨勢中，檢查是否跌破最後一個 HL
            if len(swing_lows) >= 1:
                last_hl = swing_lows[-1].price
                
                if current_price < last_hl:
                    return CHoCH(
                        from_trend=TrendDirection.BULLISH,
                        to_trend=TrendDirection.BEARISH,
                        break_price=current_price,
                        break_time=current_time,
                        confirmed=True
                    )
        
        elif current_trend == TrendDirection.BEARISH:
            # 下降趨勢中，檢查是否突破最後一個 LH
            if len(swing_highs) >= 1:
                last_lh = swing_highs[-1].price
                
                if current_price > last_lh:
                    return CHoCH(
                        from_trend=TrendDirection.BEARISH,
                        to_trend=TrendDirection.BULLISH,
                        break_price=current_price,
                        break_time=current_time,
                        confirmed=True
                    )
        
        return None
    
    def get_key_levels(self, swing_highs: List[MarketStructure],
                       swing_lows: List[MarketStructure]) -> Dict[str, List[float]]:
        """
        獲取關鍵價位
        
        Returns
        -------
        Dict[str, List[float]]
            {'resistance': [阻力位], 'support': [支撐位]}
        """
        # 取最近 3 個高點和低點
        recent_highs = [sh.price for sh in swing_highs[-3:]] if len(swing_highs) >= 3 else swing_highs
        recent_lows = [sl.price for sl in swing_lows[-3:]] if len(swing_lows) >= 3 else swing_lows
        
        return {
            'resistance': sorted(recent_highs, reverse=True),
            'support': sorted(recent_lows)
        }
