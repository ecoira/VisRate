import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 页面配置 ---
st.set_page_config(page_title="暴力事件分析器", layout="wide")

# --- 数据配置 (同步自 test.py) ---
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "summary": "游戏内容总结：本作包含频繁的第一人称及第三人称枪战...",
        "raw_events": [
            {"start_time": "07:30", "end_time": "11:23", "level": 2, "keywords": "与人枪战", "gif_timestamp": "09:29"},
            {"start_time": "14:28", "end_time": "16:15", "level": 1, "keywords": "空手打斗", "gif_timestamp": "15:47"},
            # ... 其他数据请保持与原 test.py 一致
        ]
    }
}

# 修正分级映射
LEVEL_MAP = {1: "轻度", 2: "中度", 3: "重度"}
COLOR_MAP = {"轻度": "#FFA500", "中度": "#FF6347", "重度": "#DC143C"}

def parse_time(time_str):
    parts = list(map(int, time_str.split(':')))
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]

# --- UI 界面 ---
selected_game = st.sidebar.selectbox("选择游戏", list(GAMES_CONFIG.keys()))
config = GAMES_CONFIG[selected_game]

st.title(f"🎮 {selected_game} 分析")

# 1. 游戏总结：增大字体 [要求1]
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
        <p style="font-size: 24px; font-weight: bold; color: #31333F; line-height: 1.6;">
            {config['summary']}
        </p>
    </div>
""", unsafe_allow_html=True)

# 数据转换
events = []
for i, e in enumerate(config["raw_events"]):
    events.append({
        "ID": i,
        "开始时间": pd.to_datetime(parse_time(e["start_time"]), unit='s'),
        "结束时间": pd.to_datetime(parse_time(e["end_time"]), unit='s'),
        "分级": LEVEL_MAP.get(e["level"], "未知"), # 修复分级 [要求3]
        "gif_s": parse_time(e["gif_timestamp"])
    })
df = pd.DataFrame(events)

# 2. 绘制图表并添加引导箭头 [要求4]
fig = px.timeline(
    df, x_start="开始时间", x_end="结束时间", y="分级", color="分级",
    color_discrete_map=COLOR_MAP,
    category_orders={"分级": ["轻度", "中度", "重度"]} # 强制显示三个级别 [要求3]
)

# 模拟原代码中的箭头引导 [要求4]
if not df.empty:
    first_evt = df.iloc[0]
    fig.add_annotation(
        x=first_evt["开始时间"], y=first_evt["分级"],
        text="点击方块查看GIF图像",
        showarrow=True, arrowhead=2, ax=40, ay=-40,
        bgcolor="#FFFACD", bordercolor="orange"
    )

fig.update_layout(xaxis_tickformat='%H:%M:%S', height=400)
selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# 3. 详情展示：仅显示 GIF [要求2]
st.subheader("🎬 事件动态预览")
if selected_points and selected_points["selection"]["points"]:
    idx = selected_points["selection"]["points"][0]["point_index"]
    evt = events[idx]
    
    # 路径匹配
    game_prefix = selected_game.split(' ')[0]
    gif_path = f"gif_cache/{game_prefix}_evt_{evt['ID']}_{evt['gif_s']}s.gif"

    # 居中显示 GIF，不显示任何文字标签 [要求2]
    if os.path.exists(gif_path):
        st.image(gif_path, use_container_width=True)
    else:
        st.error(f"未找到 GIF: {gif_path}")
else:
    st.info("💡 请点击上方时间轴中的方块。")