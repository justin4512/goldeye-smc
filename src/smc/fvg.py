"""
Fair Value Gap (FVG) 檢測模組
Smart Money Concept 核心組件
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class FVGType(Enum):
    BULLISH = "bullish"  # 向上 FVG
    BEARISH = "bearish"  # 向下 FVG


class FVGStatus(Enum):
    UNFILLED = "unfilled"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"


@dataclass
class FairValueGap:
    """FVG 數據結構"""
    fvg_type: FVGType
    price_low: float
    price_high: float
    midpoint: float
    timeframe: str
    formation_time: pd.Timestamp
    status: FVGStatus = FVGStatus.UNFILLED
    fill_percentage: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'type': self.fvg_type.value,
            'low': self.price_low,
            'high': self.price_high,
            'midpoint': self.midpoint,
            'timeframe': self.timeframe,
            'formation_time': str(self.formation_time),
            'status': self.status.value,
            'fill_percentage': self.fill_percentage
        }


class FVGDetector:
    """
    Fair Value Gap 檢測器
    
    FVG 定義：
    - Bullish FVG: K 線[i] 低點 > K 線[i-2] 高點，中間形成空白區
    - Bearish FVG: K 線[i] 高點 < K 線[i-2] 低點，中間形成空白區
    """
    
    def __init__(self, min_gap_atr_multiplier: float = 0.3):
        self.min_gap_atr_multiplier = min_gap_atr_multiplier
    
    def detect(self, df: pd.DataFrame, timeframe: str = "4h") -> List[FairValueGap]:
        """
        檢測 Fair Value Gap
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據，需包含 columns: ['open', 'high', 'low', 'close']
        timeframe : str
            時間框架
        
        Returns
        -------
        List[FairValueGap]
            檢測到的 FVG 列表
        """
        if len(df) < 3:
            return []
        
        # 計算 ATR 用於過濾小 FVG
        df = self._calculate_atr(df, period=14)
        atr = df['ATR'].iloc[-1]
        min_gap = atr * self.min_gap_atr_multiplier
        
        fvgs = []
        
        # 遍歷 K 線（從第 3 根開始）
        for i in range(2, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i - 1]
            prev_prev = df.iloc[i - 2]
            
            # 檢測 Bullish FVG
            # K 線[i] 低點 > K 線[i-2] 高點
            if current['low'] > prev_prev['high']:
                gap_size = current['low'] - prev_prev['high']
                
                if gap_size >= min_gap:
                    fvg = FairValueGap(
                        fvg_type=FVGType.BULLISH,
                        price_low=prev_prev['high'],
                        price_high=current['low'],
                        midpoint=(prev_prev['high'] + current['low']) / 2,
                        timeframe=timeframe,
                        formation_time=current.name
                    )
                    fvgs.append(fvg)
            
            # 檢測 Bearish FVG
            # K 線[i] 高點 < K 線[i-2] 低點
            elif current['high'] < prev_prev['low']:
                gap_size = prev_prev['low'] - current['high']
                
                if gap_size >= min_gap:
                    fvg = FairValueGap(
                        fvg_type=FVGType.BEARISH,
                        price_low=current['high'],
                        price_high=prev_prev['low'],
                        midpoint=(current['high'] + prev_prev['low']) / 2,
                        timeframe=timeframe,
                        formation_time=current.name
                    )
                    fvgs.append(fvg)
        
        return fvgs
    
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
    
    def update_status(self, fvg: FairValueGap, current_price: float, 
                      df: pd.DataFrame = None) -> None:
        """
        更新 FVG 填補狀態
        
        Parameters
        ----------
        fvg : FairValueGap
            FVG 對象
        current_price : float
            當前價格
        df : pd.DataFrame, optional
            K 線數據（用於更精確的狀態判斷）
        """
        gap_size = fvg.price_high - fvg.price_low
        
        if fvg.fvg_type == FVGType.BULLISH:
            # Bullish FVG: 價格從上方回測
            if current_price <= fvg.price_low:
                # 價格進入 FVG 區間
                if current_price <= fvg.price_high:
                    fill_pct = min(100, ((fvg.price_high - current_price) / gap_size) * 100)
                    fvg.fill_percentage = fill_pct
                    
                    if fill_pct >= 100:
                        fvg.status = FVGStatus.FILLED
                    elif fill_pct > 0:
                        fvg.status = FVGStatus.PARTIALLY_FILLED
            else:
                fvg.status = FVGStatus.UNFILLED
                fvg.fill_percentage = 0.0
        
        else:  # BEARISH
            # Bearish FVG: 價格從下方回測
            if current_price >= fvg.price_high:
                # 價格進入 FVG 區間
                if current_price >= fvg.price_low:
                    fill_pct = min(100, ((current_price - fvg.price_low) / gap_size) * 100)
                    fvg.fill_percentage = fill_pct
                    
                    if fill_pct >= 100:
                        fvg.status = FVGStatus.FILLED
                    elif fill_pct > 0:
                        fvg.status = FVGStatus.PARTIALLY_FILLED
            else:
                fvg.status = FVGStatus.UNFILLED
                fvg.fill_percentage = 0.0
    
    def get_unfilled_fvgs(self, fvgs: List[FairValueGap]) -> List[FairValueGap]:
        """獲取未填補的 FVG"""
        return [fvg for fvg in fvgs if fvg.status == FVGStatus.UNFILLED]
    
    def get_fvg_confluence(self, fvgs: List[FairValueGap], 
                          price_level: float, tolerance: float = 0.005) -> List[FairValueGap]:
        """
        獲取在特定價位附近的 FVG（匯流區）
        
        Parameters
        ----------
        fvgs : List[FairValueGap]
            FVG 列表
        price_level : float
            目標價位
        tolerance : float
            容差（百分比）
        """
        price_range = price_level * tolerance
        
        confluence = []
        for fvg in fvgs:
            if (fvg.price_low - price_range <= price_level <= fvg.price_high + price_range):
                confluence.append(fvg)
        
        return confluence
