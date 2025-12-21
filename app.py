import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 页面基本设置 ---
st.set_page_config(page_title="暴力事件分析器", layout="wide")

# --- 静态数据配置 (保持与原逻辑一致) ---
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "summary": "游戏内容总结：本作包含频繁的第一人称及第三人称枪战，并通过慢动作镜头特写子弹穿透敌人、血液自伤口喷涌而出的暴力画面。",
        "raw_events": [
            {"start_time": "07:30", "end_time": "11:23", "level": "重度", "keywords": "与人枪战", "gif_timestamp": "09:29"},
            {"start_time": "14:28", "end_time": "16:15", "level": "轻度", "keywords": "空手打斗", "gif_timestamp": "15:47"},
            {"start_time": "26:34", "end_time": "27:04", "level": "轻度", "keywords": "马的尸体", "gif_timestamp": "26:38"},
            {"start_time": "31:05", "end_time": "36:50", "level": "重度", "keywords": "与野兽枪战", "gif_timestamp": "34:02"},
            {"start_time": "51:04", "end_time": "59:36", "level": "重度", "keywords": "与人枪战", "gif_timestamp": "55:02"},
        ]
    },
    "Detroit: Become Human": {
        "summary": "游戏内容总结：剧情聚焦于仿生人与人类之间的尖锐冲突。包含犯罪现场描绘、人类尸体与血迹，以及枪击仿生人的暴力场面。",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": "轻度", "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": "轻度", "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "summary": "游戏内容总结：快节奏动作战斗，使用冷兵器砍杀对抗。画面会出现鲜红的血液喷溅特效，但敌人死亡后通常会迅速消散。",
        "raw_events": [
            {"start_time": "01:10", "end_time": "06:10", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "05:14"},
            {"start_time": "08:26", "end_time": "14:42", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "08:58"},
            {"start_time": "19:20", "end_time": "19:53", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "19:27"},
            {"start_time": "22:48", "end_time": "34:30", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "28:12"},
            {"start_time": "37:48", "end_time": "42:47", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "42:40"},
            {"start_time": "49:50", "end_time": "56:46", "level": "轻度", "keywords": "腹部中枪", "gif_timestamp": "56:37"},
        ]
    }
}

def parse_time(time_str):
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 2: return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]

# --- 侧边栏：选择游戏 ---
st.sidebar.title("控制面板")
selected_game = st.sidebar.selectbox("选择要分析的游戏", list(GAMES_CONFIG.keys()))
config = GAMES_CONFIG[selected_game]

# --- 主界面 ---
st.title(f"📊 {selected_game} 暴力事件分析")
st.markdown(f"**游戏总结：** {config['summary']}")

# 数据转换
events = []
for i, e in enumerate(config["raw_events"]):
    start_s = parse_time(e["start_time"])
    end_s = parse_time(e["end_time"])
    gif_s = parse_time(e["gif_timestamp"])
    events.append({
        "事件编号": i,
        "开始时间": pd.to_datetime(start_s, unit='s'),
        "结束时间": pd.to_datetime(end_s, unit='s'),
        "等级": e["level"],
        "关键词": e["keywords"],
        "gif_s": gif_s
    })

df = pd.DataFrame(events)

# --- 绘制交互式时间轴 (Plotly) ---
fig = px.timeline(
    df, 
    x_start="开始时间", 
    x_end="结束时间", 
    y="等级", 
    color="等级",
    hover_data=["关键词", "事件编号"],
    color_discrete_map={"轻度": "#FFA500", "重度": "#FF6347"}, # 映射颜色
    category_orders={"等级": ["轻度", "重度"]}
)

fig.update_layout(
    xaxis_title="时间轴 (HH:MM:SS)",
    yaxis_title="暴力分级",
    xaxis_tickformat='%H:%M:%S',
    height=400,
    clickmode='event+select'
)

# 在网页上展示图表，并捕获点击动作
selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# --- 详情展示区 ---
st.divider()
st.subheader("🎬 事件动态预览")

# 检查用户是否点击了图表中的某个方块
if selected_points and "selection" in selected_points and selected_points["selection"]["points"]:
    # 获取点击点的原始数据索引
    idx = selected_points["selection"]["points"][0]["point_index"]
    event_data = events[idx]
    
    # 构建文件名 (逻辑与原代码一致)
    game_prefix = selected_game.split(' ')[0]
    gif_filename = f"{game_prefix}_evt_{event_data['事件编号']}_{event_data['gif_s']}s.gif"
    gif_path = os.path.join("gif_cache", gif_filename)

    # 左右分栏显示
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**当前选中:** 事件 #{event_data['事件编号']}")
        st.write(f"**暴力关键词:** {event_data['关键词']}")
        st.write(f"**分级:** {event_data['等级']}")
        st.write(f"**对应文件名:** `{gif_filename}`")
    
    with col2:
        if os.path.exists(gif_path):
            st.image(gif_path, caption=f"事件 #{event_data['事件编号']} 预览")
        else:
            st.error(f"未找到对应的 GIF 文件: {gif_path}")
else:
    st.info("💡 提示：请点击上方时间轴中的【彩色方块】查看该事件的 GIF 预览。")