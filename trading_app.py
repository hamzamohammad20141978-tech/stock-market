import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. إعداد الصفحة الفاخرة المخصصة للموبايل والتابلت والكمبيوتر لمنع التهنيج
st.set_page_config(
    page_title="GoTrading Mobile Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# تصميم استايل صايع ومظلم يليق بحيتان البورصة
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; background-color: #0c1015; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 48px; }
    div[data-testid="stMetricValue"] { font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# الأسعار الأساسية للشركات والعملات
STATIC_BASE_PRICES = {
    "⚡ Bitcoin (BTC/USD)": 68250.0,
    "🌐 Alphabet Inc. (GOOGLE)": 178.50,
    "💻 Microsoft Corp. (MSFT)": 425.20,
    "📱 Meta Platforms (META)": 485.10,
    "🚗 Tesla Motors (TESLA)": 185.40,
}

# 2. إدارة الذاكرة المستقرة لحفظ الحساب والمحفظة
if "market_data" not in st.session_state: st.session_state.market_data = {}
if "trend_state" not in st.session_state: st.session_state.trend_state = {}
if "last_asset" not in st.session_state: st.session_state.last_asset = "⚡ Bitcoin (BTC/USD)"
if "balance" not in st.session_state: st.session_state.balance = 10000.0
if "holdings" not in st.session_state: st.session_state.holdings = {}
if "history" not in st.session_state: st.session_state.history = []

# دالة لتهيئة حالة الاتجاه الزمني لكل أصل مالي
def initialize_trend_state(asset_name):
    """تهيئة نظام الاتجاه الزمني لكل أصل"""
    if asset_name not in st.session_state.trend_state:
        st.session_state.trend_state[asset_name] = {
            "phase": "bullish",  # bullish -> consolidation -> bearish
            "cycle_count": 0,
            "phase_duration": 3  # عدد التحديثات في كل مرحلة
        }

# دالة حساب السعر الجديد بناءً على الاتجاه الزمني
def calculate_temporal_trend_price(asset_name, last_price, base_price, is_bitcoin=False):
    """
    حساب السعر الجديد بناءً على نمط الاتجاه الزمني
    - Bullish: صعود مستمر لمدة 3 تحديثات
    - Consolidation: استقرار جانبي مع تذبذب بسيط
    - Bearish: هبوط مستمر لمدة 3 تحديثات
    """
    trend_info = st.session_state.trend_state[asset_name]
    phase = trend_info["phase"]
    cycle_count = trend_info["cycle_count"]
    
    # تحديد نطاق الحركة السعرية بناءً على المرحلة
    if is_bitcoin:
        if phase == "bullish":
            price_change = random.uniform(10.0, 80.0)  # صعود قوي
        elif phase == "consolidation":
            price_change = random.uniform(-15.0, 15.0)  # تذبذب طفيف
        else:  # bearish
            price_change = random.uniform(-80.0, -10.0)  # هبوط قوي
        rounding_factor = 1.0
    else:
        if phase == "bullish":
            price_change = random.uniform(0.5, 7.5)  # صعود قوي
        elif phase == "consolidation":
            price_change = random.uniform(-1.5, 1.5)  # تذبذب طفيف
        else:  # bearish
            price_change = random.uniform(-7.5, -0.5)  # هبوط قوي
        rounding_factor = 0.01
    
    # حساب السعر الجديد
    next_price = last_price + price_change
    
    # حدود أمان لحماية السعر من الطيران اللانهائي أو الهبوط الكامل
    next_price = max(base_price * 0.75, min(base_price * 1.25, next_price))
    next_price = round(next_price / rounding_factor) * rounding_factor
    
    # تحديث عداد المرحلة
    trend_info["cycle_count"] += 1
    
    # الانتقال إلى المرحلة التالية عند اكتمال المدة
    if trend_info["cycle_count"] >= trend_info["phase_duration"]:
        trend_info["cycle_count"] = 0
        # دوران المراحل: bullish -> consolidation -> bearish -> bullish
        if phase == "bullish":
            trend_info["phase"] = "consolidation"
        elif phase == "consolidation":
            trend_info["phase"] = "bearish"
        else:
            trend_info["phase"] = "bullish"
    
    return next_price

# قائمة اختيار الأسهم الفخمة
selected_asset = st.selectbox(
    "📊 SELECT MARKET", 
    list(STATIC_BASE_PRICES.keys()), 
    index=list(STATIC_BASE_PRICES.keys()).index(st.session_state.last_asset)
)

# تصفير ذكي عند تنقل المستخدم بين الأسهم عشان الشموع متدخلش في بعضها
if selected_asset != st.session_state.last_asset:
    st.session_state.last_asset = selected_asset

# توليد الشموع الـ 25 الأولى لأول مرة مع تطبيق نمط الاتجاهات الزمنية
if selected_asset not in st.session_state.market_data:
    initialize_trend_state(selected_asset)
    base_p = STATIC_BASE_PRICES[selected_asset]
    is_btc = "Bitcoin" in selected_asset
    
    candles_init = []
    p = base_p
    for _ in range(25):
        op = p
        # استخدام نظام الاتجاه الزمني بدلاً من الحركة العشوائية البسيطة
        cl = calculate_temporal_trend_price(selected_asset, p, base_p, is_bitcoin=is_btc)
        
        hi = max(op, cl) * random.uniform(1.001, 1.004)
        lo = min(op, cl) * random.uniform(0.996, 0.999)
        candles_init.append({"open": op, "high": hi, "low": lo, "close": cl})
        p = cl
    st.session_state.market_data[selected_asset] = candles_init
else:
    # تهيئة حالة الاتجاه إذا لم تكن موجودة (للأصول الموجودة مسبقاً)
    initialize_trend_state(selected_asset)

# 🔥 محرك التحديث التلقائي الذكي (تحديث كل 1 ثانية أوتوماتيك بدون وميض للشاشة)
st_autorefresh(interval=1000, key="datarefresh")

# تشغيل الحسابات الحية لحركة السهم الحالية مع نظام الاتجاهات الزمنية
current_candles = st.session_state.market_data[selected_asset]
last_candle = current_candles[-1]
last_p = last_candle["close"]

base_ref = STATIC_BASE_PRICES[selected_asset]
is_btc = "Bitcoin" in selected_asset

# 💎 نظام الاتجاهات الزمنية المحسّن (Temporal Trends) 💎
# الحركة السعرية الآن تتبع نمطاً واقعياً بدلاً من التذبذب العشوائي البسيط
next_open = last_p
next_close = calculate_temporal_trend_price(selected_asset, last_p, base_ref, is_bitcoin=is_btc)

# حساب أعلى وأقل سعر للشمعة الجديدة بناءً على الاختلاف الفعلي
price_move = abs(next_close - next_open)
next_high = max(next_open, next_close) + (price_move * random.uniform(0.1, 0.25))
next_low = min(next_open, next_close) - (price_move * random.uniform(0.1, 0.25))

# ترحيل الشموع (نشيل أقدم واحدة ونحط الجديدة في الآخر عشان السهم يندفع للأمام)
current_candles.pop(0)
current_candles.append({"open": next_open, "high": next_high, "low": next_low, "close": next_close})
st.session_state.market_data[selected_asset] = current_candles

# 3. شاشة العدادات الرقمية المضيئة
col_metric1, col_metric2 = st.columns(2)
with col_metric1:
    st.metric(
        label=f"📈 LIVE PRICE: {selected_asset.split()[-1]}", 
        value=f"${next_close:,.2f}", 
        delta=f"{(next_close - last_p):+,.2f}$"
    )
with col_metric2:
    st.metric(
        label="💰 Margin Balance", 
        value=f"${st.session_state.balance:,.2f}"
    )

# 4. بناء ورسم شارت الشموع اليابانية الاحترافي (Candlestick Chart)
df = pd.DataFrame(current_candles)
string_axis = [f"C_{x}" for x in range(len(df))]

fig = go.Figure(data=[go.Candlestick(
    x=string_axis, 
    open=df['open'], 
    high=df['high'], 
    low=df['low'], 
    close=df['close'],
    increasing_line_color='#02c076', 
    decreasing_line_color='#f6465d',
    increasing_fillcolor='#02c076', 
    decreasing_fillcolor='#f6465d',
    whiskerwidth=0.4, 
    line_width=1.5
)])

fig.update_layout(
    margin=dict(l=2, r=2, t=2, b=2), 
    xaxis_rangeslider_visible=False,
    template="plotly_dark", 
    paper_bgcolor="#0c1015", 
    plot_bgcolor="#0c1015", 
    height=320, 
    dragmode="pan"
)
fig.update_xaxes(type='category', showticklabels=False)

# رسم خط سعر الدخول الأصفر لو شاري في السهم ده
if selected_asset in st.session_state.holdings:
    entry = st.session_state.holdings[selected_asset]["entry_price"]
    fig.add_hline(y=entry, line_dash="dash", line_color="#ffb703")

st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

# 5. لوحة تنفيذ الصفقات الجديدة بالاسم البورصجي الفخم والمظبوط 💼
st.markdown("### 💼 TRADING DESK & ORDER EXECUTION")
trade_size = st.number_input(
    "INVESTMENT SIZE ($)", 
    min_value=10.0, 
    max_value=max(10.0, st.session_state.balance), 
    value=1000.0, 
    step=100.0
)

col_b1, col_b2 = st.columns(2)
has_pos = selected_asset in st.session_state.holdings

with col_b1:
    if not has_pos:
        if st.button("🟢 BUY / INVEST IN ASSET", key="buy_b"):
            if st.session_state.balance >= trade_size:
                st.session_state.balance -= trade_size
                st.session_state.holdings[selected_asset] = {"entry_price": next_close, "amount": trade_size}
                st.rerun()
    else:
        st.info(f"📈 Invested at: ${st.session_state.holdings[selected_asset]['entry_price']:,.2f}")

with col_b2:
    if has_pos:
        entry_price = st.session_state.holdings[selected_asset]["entry_price"]
        pct_change = (next_close - entry_price) / entry_price
        current_value = st.session_state.holdings[selected_asset]["amount"] * (1 + pct_change)
        pnl = current_value - st.session_state.holdings[selected_asset]["amount"]
        pnl_status = "🎯 Profit" if pnl >= 0 else "❌ Loss"
        
        if st.button(f"🔴 SELL & LIQUIDATE ({pnl:+.2f}$)", key="sell_b"):
            st.session_state.balance += current_value
            st.session_state.history.insert(0, f"⚡ Sold {selected_asset.split()[-1]}: {pnl:+.2f}$ ({pnl_status})")
            del st.session_state.holdings[selected_asset]
            st.rerun()
    else:
        st.write("No active position. Click BUY to open a spot trade.")

# 6. أرشيف العمليات السابقة
st.markdown("### 📜 LIVE ORDER HISTORY")
if st.session_state.history:
    for item in st.session_state.history[:5]: 
        st.markdown(f"- {item}")
else:
    st.write("No history recorded yet.")
