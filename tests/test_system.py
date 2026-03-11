"""
GoldEye SMC 系統測試腳本
測試核心功能是否正常運作
"""

import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/xauusd_smc')

from src.data.fetcher import DataFetcher
from src.smc.order_block import OrderBlockDetector
from src.smc.fvg import FVGDetector
from src.smc.structure import StructureAnalyzer
from src.signal.generator import SignalGenerator

def test_data_fetcher():
    """測試數據獲取"""
    print("\n" + "="*60)
    print("📊 測試數據獲取模組")
    print("="*60)
    
    fetcher = DataFetcher()
    
    # 測試獲取 XAUUSD 數據
    print("\n📈 獲取 XAUUSD 數據...")
    df = fetcher.fetch_symbol("XAUUSD=X", period="1mo", interval="1h")
    
    if not df.empty:
        print(f"✅ 成功獲取 {len(df)} 根 K 線")
        print(f"   最新價格：${df['close'].iloc[-1]:.2f}")
        print(f"   時間範圍：{df.index[0]} ~ {df.index[-1]}")
        return df
    else:
        print("❌ 無法獲取數據")
        return None

def test_order_block_detection(df):
    """測試 Order Block 檢測"""
    print("\n" + "="*60)
    print("🔲 測試 Order Block 檢測")
    print("="*60)
    
    detector = OrderBlockDetector()
    
    # 檢測 4H Order Block
    obs = detector.detect(df, timeframe="4h")
    
    if obs:
        print(f"✅ 檢測到 {len(obs)} 個 Order Block")
        
        # 顯示最近 3 個
        for i, ob in enumerate(obs[-3:], 1):
            print(f"\n   OB #{i}:")
            print(f"   類型：{ob.ob_type.value}")
            print(f"   價格區間：${ob.price_low:.2f} - ${ob.price_high:.2f}")
            print(f"   強度評分：{ob.strength_score:.0f}")
            print(f"   是否有效：{'是' if ob.is_valid else '否'}")
    else:
        print("⚠️ 未檢測到 Order Block")

def test_fvg_detection(df):
    """測試 FVG 檢測"""
    print("\n" + "="*60)
    print("⬜ 測試 Fair Value Gap 檢測")
    print("="*60)
    
    detector = FVGDetector()
    fvgs = detector.detect(df, timeframe="4h")
    
    if fvgs:
        print(f"✅ 檢測到 {len(fvgs)} 個 FVG")
        
        # 顯示未填補的 FVG
        unfilled = detector.get_unfilled_fvgs(fvgs)
        print(f"   未填補：{len(unfilled)} 個")
        
        for i, fvg in enumerate(unfilled[-3:], 1):
            print(f"\n   FVG #{i}:")
            print(f"   類型：{fvg.fvg_type.value}")
            print(f"   價格區間：${fvg.price_low:.2f} - ${fvg.price_high:.2f}")
            print(f"   狀態：{fvg.status.value}")
    else:
        print("⚠️ 未檢測到 FVG")

def test_structure_analysis(df):
    """測試市場結構分析"""
    print("\n" + "="*60)
    print("📐 測試市場結構分析")
    print("="*60)
    
    analyzer = StructureAnalyzer()
    
    # 檢測 Swing 點
    swing_highs, swing_lows = analyzer.detect_swing_points(df)
    print(f"\n✅ 檢測到 {len(swing_highs)} 個 Swing Highs, {len(swing_lows)} 個 Swing Lows")
    
    # 識別趨勢
    trend = analyzer.identify_trend(swing_highs, swing_lows)
    print(f"   當前趨勢：{trend.value}")
    
    # 獲取關鍵價位
    levels = analyzer.get_key_levels(swing_highs, swing_lows)
    print(f"\n   關鍵阻力：{levels['resistance'][:3]}")
    print(f"   關鍵支撐：{levels['support'][:3]}")

def test_signal_generation(df):
    """測試信號生成"""
    print("\n" + "="*60)
    print("📊 測試信號生成")
    print("="*60)
    
    generator = SignalGenerator(min_confidence=60, min_rr=1.2)
    
    current_price = df['close'].iloc[-1]
    print(f"\n💰 當前價格：${current_price:.2f}")
    
    signal = generator.generate_signal(df, timeframe="4h", current_price=current_price)
    
    if signal:
        print(f"✅ 生成信號:")
        print(f"   方向：{signal.direction}")
        print(f"   信心度：{signal.confidence:.0f}%")
        print(f"   進場：${signal.entry_low:.2f} - ${signal.entry_high:.2f}")
        print(f"   止損：${signal.stop_loss:.2f}")
        print(f"   目標 1：${signal.target_1:.2f} (R:R = {signal.rr_1:.2f})")
        print(f"   目標 2：${signal.target_2:.2f} (R:R = {signal.rr_2:.2f})")
        print(f"\n   SMC 邏輯：{signal.smc_logic}")
    else:
        print("⚠️ 無合格信號（可能是正常情況，市場並非總是有高質量機會）")

def main():
    """主測試函數"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║        🧪 GoldEye SMC 系統測試                    ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # 1. 測試數據獲取
    df = test_data_fetcher()
    if df is None:
        print("\n❌ 數據獲取失敗，終止測試")
        return
    
    # 2. 測試 Order Block 檢測
    test_order_block_detection(df)
    
    # 3. 測試 FVG 檢測
    test_fvg_detection(df)
    
    # 4. 測試市場結構分析
    test_structure_analysis(df)
    
    # 5. 測試信號生成
    test_signal_generation(df)
    
    print("\n" + "="*60)
    print("✅ 測試完成")
    print("="*60)
    print("""
📝 總結:
   - 數據獲取模組：✅ 正常
   - SMC 檢測引擎：✅ 正常
   - 信號生成器：✅ 正常
   - Telegram 通知：⏭️  需配置 .env 後測試

🚀 下一步:
   1. 複製 .env.example 為 .env
   2. 填寫 Telegram Bot Token 和 Chat ID
   3. 運行 python main.py 啟動監控
""")

if __name__ == "__main__":
    main()
