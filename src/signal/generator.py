"""
SMC 信號生成器
整合 Order Block、FVG、市場結構生成交易信號
"""

import pandas as pd
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.smc.order_block import OrderBlockDetector, OrderBlock, OBType
from src.smc.fvg import FVGDetector, FairValueGap, FVGType
from src.smc.structure import StructureAnalyzer, TrendDirection


@dataclass
class TradingSignal:
    """交易信號數據結構"""
    direction: str  # LONG / SHORT
    confidence: float
    timeframe: str
    entry_low: float
    entry_high: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_pct: float
    rr_1: float
    rr_2: float
    smc_logic: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'direction': self.direction,
            'confidence': self.confidence,
            'timeframe': self.timeframe,
            'entry_low': self.entry_low,
            'entry_high': self.entry_high,
            'stop_loss': self.stop_loss,
            'target_1': self.target_1,
            'target_2': self.target_2,
            'risk_pct': self.risk_pct,
            'rr_1': self.rr_1,
            'rr_2': self.rr_2,
            'smc_logic': self.smc_logic,
            'timestamp': str(self.timestamp)
        }


class SignalGenerator:
    """
    SMC 信號生成器
    
    整合以下因子生成信號：
    - Order Block 回測
    - FVG 目標
    - 市場結構 (BOS/CHoCH)
    - 流動性掃描
    """
    
    def __init__(self, min_confidence: float = 70.0, min_rr: float = 1.5):
        self.min_confidence = min_confidence
        self.min_rr = min_rr
        self.ob_detector = OrderBlockDetector()
        self.fvg_detector = FVGDetector()
        self.structure_analyzer = StructureAnalyzer()
    
    def generate_signal(self, df: pd.DataFrame, timeframe: str = "4h",
                        current_price: float = None) -> Optional[TradingSignal]:
        """
        生成交易信號
        
        Parameters
        ----------
        df : pd.DataFrame
            K 線數據
        timeframe : str
            時間框架
        current_price : float
            當前價格
        
        Returns
        -------
        Optional[TradingSignal]
            交易信號，如果無合格信號則返回 None
        """
        if df.empty or len(df) < 50:
            return None
        
        if current_price is None:
            current_price = df['close'].iloc[-1]
        
        # 1. 檢測 Order Block
        order_blocks = self.ob_detector.detect(df, timeframe)
        valid_obs = [ob for ob in order_blocks if ob.is_valid and ob.strength_score >= 60]
        
        # 2. 檢測 FVG
        fvgs = self.fvg_detector.detect(df, timeframe)
        unfilled_fvgs = self.fvg_detector.get_unfilled_fvgs(fvgs)
        
        # 3. 檢測市場結構
        swing_highs, swing_lows = self.structure_analyzer.detect_swing_points(df)
        trend = self.structure_analyzer.identify_trend(swing_highs, swing_lows)
        
        # 4. 尋找交易機會
        signal = None
        
        # 做多信號：回測 Bullish OB + 上升趨勢
        if trend == TrendDirection.BULLISH:
            signal = self._find_long_opportunity(
                valid_obs, unfilled_fvgs, current_price, df, timeframe
            )
        
        # 做空信號：回測 Bearish OB + 下降趨勢
        elif trend == TrendDirection.BEARISH:
            signal = self._find_short_opportunity(
                valid_obs, unfilled_fvgs, current_price, df, timeframe
            )
        
        # 5. 驗證信號質量
        if signal and signal.confidence >= self.min_confidence:
            if signal.rr_1 >= self.min_rr:
                return signal
        
        return None
    
    def _find_long_opportunity(self, obs: List[OrderBlock], fvgs: List[FairValueGap],
                               current_price: float, df: pd.DataFrame,
                               timeframe: str) -> Optional[TradingSignal]:
        """尋找做多機會"""
        # 尋找未被測試的 Bullish OB
        for ob in obs:
            if ob.ob_type != OBType.BULLISH:
                continue
            
            # 檢查價格是否接近 OB
            if not (ob.price_low * 0.995 <= current_price <= ob.price_high * 1.005):
                continue
            
            # 計算止損 (OB 低點下方)
            stop_loss = ob.price_low * 0.998  # 0.2% 緩衝
            
            # 計算目標 (上方 FVG 或流動性)
            target_1, target_2 = self._calculate_long_targets(ob, fvgs, df)
            
            if target_1 <= current_price:
                continue
            
            # 計算 R:R
            risk = current_price - stop_loss
            reward_1 = target_1 - current_price
            reward_2 = target_2 - current_price
            
            if risk <= 0:
                continue
            
            rr_1 = reward_1 / risk
            rr_2 = reward_2 / risk
            
            # 計算信心度
            confidence = self._calculate_confidence(ob, fvgs, trend='bullish')
            
            # 生成信號
            return TradingSignal(
                direction='LONG',
                confidence=confidence,
                timeframe=timeframe,
                entry_low=ob.price_low,
                entry_high=ob.price_high,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                risk_pct=(risk / current_price) * 100,
                rr_1=rr_1,
                rr_2=rr_2,
                smc_logic=f"回測 Bullish OB @ ${ob.price_low:.2f}-{ob.price_high:.2f}, "
                         f"強度評分：{ob.strength_score:.0f}, 上方 FVG 目標 @ ${target_1:.2f}"
            )
        
        return None
    
    def _find_short_opportunity(self, obs: List[OrderBlock], fvgs: List[FairValueGap],
                                current_price: float, df: pd.DataFrame,
                                timeframe: str) -> Optional[TradingSignal]:
        """尋找做空機會"""
        # 尋找未被測試的 Bearish OB
        for ob in obs:
            if ob.ob_type != OBType.BEARISH:
                continue
            
            # 檢查價格是否接近 OB
            if not (ob.price_low * 0.995 <= current_price <= ob.price_high * 1.005):
                continue
            
            # 計算止損 (OB 高點上方)
            stop_loss = ob.price_high * 1.002  # 0.2% 緩衝
            
            # 計算目標 (下方 FVG 或流動性)
            target_1, target_2 = self._calculate_short_targets(ob, fvgs, df)
            
            if target_1 >= current_price:
                continue
            
            # 計算 R:R
            risk = stop_loss - current_price
            reward_1 = current_price - target_1
            reward_2 = current_price - target_2
            
            if risk <= 0:
                continue
            
            rr_1 = reward_1 / risk
            rr_2 = reward_2 / risk
            
            # 計算信心度
            confidence = self._calculate_confidence(ob, fvgs, trend='bearish')
            
            # 生成信號
            return TradingSignal(
                direction='SHORT',
                confidence=confidence,
                timeframe=timeframe,
                entry_low=ob.price_low,
                entry_high=ob.price_high,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                risk_pct=(risk / current_price) * 100,
                rr_1=rr_1,
                rr_2=rr_2,
                smc_logic=f"回測 Bearish OB @ ${ob.price_low:.2f}-{ob.price_high:.2f}, "
                         f"強度評分：{ob.strength_score:.0f}, 下方 FVG 目標 @ ${target_1:.2f}"
            )
        
        return None
    
    def _calculate_long_targets(self, ob: OrderBlock, fvgs: List[FairValueGap],
                                df: pd.DataFrame) -> tuple:
        """計算做多目標價"""
        current_price = df['close'].iloc[-1]
        
        # 目標 1: 最近的上方 FVG
        target_1 = current_price * 1.01  # 預設 1%
        for fvg in fvgs:
            if fvg.fvg_type == FVGType.BEARISH and fvg.price_low > current_price:
                target_1 = fvg.price_low
                break
        
        # 目標 2: 前高或更遠的 FVG
        target_2 = df['high'].rolling(20).max().iloc[-1] * 1.005
        
        return target_1, target_2
    
    def _calculate_short_targets(self, ob: OrderBlock, fvgs: List[FairValueGap],
                                 df: pd.DataFrame) -> tuple:
        """計算做空目標價"""
        current_price = df['close'].iloc[-1]
        
        # 目標 1: 最近的下方 FVG
        target_1 = current_price * 0.99  # 預設 -1%
        for fvg in fvgs:
            if fvg.fvg_type == FVGType.BULLISH and fvg.price_high < current_price:
                target_1 = fvg.price_high
                break
        
        # 目標 2: 前低或更遠的 FVG
        target_2 = df['low'].rolling(20).min().iloc[-1] * 0.995
        
        return target_1, target_2
    
    def _calculate_confidence(self, ob: OrderBlock, fvgs: List[FairValueGap],
                              trend: str) -> float:
        """
        計算信號信心度
        
        因子：
        - OB 強度 (40%)
        - FVG 匯流 (30%)
        - 趨勢一致性 (30%)
        """
        score = 0.0
        
        # OB 強度 (40%)
        ob_score = ob.strength_score
        score += ob_score * 0.40
        
        # FVG 匯流 (30%)
        fvg_confluence = len([fvg for fvg in fvgs 
                              if (trend == 'bullish' and fvg.fvg_type == FVGType.BEARISH) or
                                 (trend == 'bearish' and fvg.fvg_type == FVGType.BULLISH)])
        fvg_score = min(100, fvg_confluence * 30)
        score += fvg_score * 0.30
        
        # 趨勢一致性 (30%) - 假設已經在正確的趨勢中
        trend_score = 80
        score += trend_score * 0.30
        
        return min(100, score)
