import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 页面配置 ---
st.set_page_config(page_title="暴力事件分析器", layout="wide")

# --- 数据配置 (同步自 test.py) ---
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "video_path": "video/redemption.mp4", # 请修改为真实路径
        "summary": "游戏内容总结：本作包含频繁的第一人称及第三人称枪战，并通过慢动作镜头特写子弹穿透敌人、血液自伤口喷涌而出的暴力画面。此外，游戏中还存在野兽撕咬人类并导致大量出血的血腥场景，以及静态的动物尸体图像。",
        "video_duration_str": "01:01:03",
        "raw_events": [
            {"start_time": "07:30", "end_time": "11:23", "level": 2, "keywords": "与人枪战", "gif_timestamp": "09:29"},
            {"start_time": "14:28", "end_time": "16:15", "level": 1, "keywords": "空手打斗", "gif_timestamp": "15:47"},
            {"start_time": "26:34", "end_time": "27:04", "level": 1, "keywords": "马的尸体", "gif_timestamp": "26:38"},
            {"start_time": "31:05", "end_time": "36:50", "level": 2, "keywords": "与野兽枪战，野兽撕咬", "gif_timestamp": "34:02"},
            {"start_time": "51:04", "end_time": "59:36", "level": 2, "keywords": "与人枪战", "gif_timestamp": "55:02"},
        ]
    },
    "Detroit: Become Human": {
        "video_path": "video/detroit.mp4", # 请修改为真实路径
        "summary": "游戏内容总结：本作的核心剧情聚焦于仿生人与人类之间的尖锐冲突，并深入探讨了仿生人内部的分裂——例如，作为执法者的仿生人与其普通同类之间的对立。游戏中包含对犯罪现场的直接描绘，其中会涉及人类尸体与血迹。此外，剧情还包含枪击仿生人的暴力场面，其标志性的蓝色血液是本作一个独特的视觉特征。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "video_path": "video/hades.mp4",
        "summary": "游戏内容总结：快节奏的动作战斗是核心玩法，玩家在游戏中主要操控剑、矛、盾、弓等神话冷兵器与冥界怪物进行高频率的砍杀对抗。当敌人或玩家受伤时，画面会出现鲜红的血液喷溅特效和地面积血细节，但敌人死亡后通常会化为光点或烟雾迅速消散。",
        "video_duration_str": "01:00:22", # 视频总时长 HH:MM:SS
        "raw_events": [
            {"start_time": "01:10", "end_time": "06:10", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "05:14"},
            {"start_time": "08:26", "end_time": "14:42", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "08:58"},
            {"start_time": "19:20", "end_time": "19:53", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "19:27"},
            {"start_time": "22:48", "end_time": "34:30", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "28:12"},
            {"start_time": "37:48", "end_time": "42:47", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "42:40"},
            {"start_time": "49:50", "end_time": "56:46", "level": 1, "keywords": "腹部中枪", "gif_timestamp": "56:37"},
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