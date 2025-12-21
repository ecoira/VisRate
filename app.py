import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# =============================
# 页面配置
# =============================
st.set_page_config(
    page_title="暴力内容分析系统",
    layout="wide"
)

LEVEL_MAP = {
    1: "轻度",
    2: "中度",
    3: "重度"
}

LEVEL_COLOR = {
    "轻度": "#7BC8A4",
    "中度": "#F9C74F",
    "重度": "#F94144"
}

LEVEL_ORDER = ["轻度", "中度", "重度"]

# =============================
# 游戏配置
# =============================
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "file_prefix": "Red",
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
        "file_prefix": "Detroit",
        "summary": "游戏内容总结：本作的核心剧情聚焦于仿生人与人类之间的尖锐冲突，并深入探讨了仿生人内部的分化与觉醒。游戏中存在案发现场的直接描绘，其中会涉及人类尸体与血迹。此外，剧情还包含枪击仿生人的暴力场面，其标志性的蓝色血液是本作一个独特的视觉特征。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "file_prefix": "Hades",
        "summary": "游戏内容总结：快节奏的动作战斗是核心玩法，玩家在游戏中主要操控剑、矛、盾、弓等神话冷兵器进行高频率的砍杀对抗。当敌人或玩家受伤时，画面会出现鲜红的血液喷溅特效和地面积血细节，但敌人死亡后通常会化为光点或烟雾迅速消散。",
        "video_duration_str": "01:00:22",
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

# =============================
# 工具函数
# =============================
def time_str_to_seconds(t):
    parts = list(map(int, t.split(":")))
    if len(parts) == 2:
        m, s = parts
        return m * 60 + s
    h, m, s = parts
    return h * 3600 + m * 60 + s

def gif_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =============================
# 页面主体
# =============================
st.title("🎮 游戏暴力内容分析")

game_name = st.selectbox("请选择游戏", list(GAMES_CONFIG.keys()))
game_cfg = GAMES_CONFIG[game_name]
prefix = game_cfg["file_prefix"]

st.markdown(
    f"""
    <div style="
        background-color:#f5f7fa;
        padding:16px;
        border-radius:8px;
        line-height:1.7;
        font-size:15px;
    ">
    {game_cfg["summary"]}
    </div>
    """,
    unsafe_allow_html=True
)

# ======================================================
# 🧱 区域二：暴力程度时间轴（Hover 播放 GIF）
# ======================================================
st.subheader("📊 暴力程度时间轴")

events = []
base_time = pd.Timestamp("1970-01-01")

for idx, e in enumerate(game_cfg["raw_events"]):
    gif_path = os.path.join("gifs", f"{prefix}_{e['gif_timestamp'].replace(':','')}.gif")
    gif_b64 = gif_to_base64(gif_path) if os.path.exists(gif_path) else ""

    events.append({
        "ID": idx,
        "start": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["start_time"])),
        "end": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["end_time"])),
        "level": LEVEL_MAP[e["level"]],
        "keywords": e["keywords"],
        "gif": gif_b64
    })

df = pd.DataFrame(events)

fig = px.timeline(
    df,
    x_start="start",
    x_end="end",
    y="level",
    color="level",
    color_discrete_map=LEVEL_COLOR,
    custom_data=["ID", "keywords", "gif"]
)

fig.update_traces(
    hovertemplate="""
    <b>%{customdata[1]}</b><br><br>
    <img src="data:image/gif;base64,%{customdata[2]}" width="240">
    <extra></extra>
    """
)

fig.update_layout(
    height=260,
    margin=dict(l=20, r=20, t=10, b=20),
    showlegend=True,
    xaxis=dict(tickformat="%H:%M:%S", title="视频时间")
)

selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# ======================================================
# 🧱 区域三：点击后事件详情（稳定版）
# ======================================================
st.subheader("🎬 事件详情")

if selected and selected.get("selection", {}).get("points"):
    evt_id = selected["selection"]["points"][0]["customdata"][0]
    row = df.iloc[evt_id]

    gif_path = os.path.join(
        "gifs",
        f"{prefix}_{game_cfg['raw_events'][evt_id]['gif_timestamp'].replace(':','')}.gif"
    )

    col1, col2 = st.columns([1.5, 1])
    with col1:
        if os.path.exists(gif_path):
            with open(gif_path, "rb") as f:
                st.image(
                    f.read(),
                    format="gif",
                    use_container_width=True,
                    key=f"gif_{prefix}_{evt_id}_{os.path.getmtime(gif_path)}"
                )
        else:
            st.warning("GIF 文件丢失")

    with col2:
        st.markdown("### 事件信息")
        st.markdown(f"**关键词**：{row['keywords']}")
        st.markdown(f"**暴力等级**：{row['level']}")
        st.markdown(
            f"**发生时间**：{game_cfg['raw_events'][evt_id]['start_time']} - {game_cfg['raw_events'][evt_id]['end_time']}"
        )
else:
    st.info("点击时间轴中的事件查看详情，或直接悬停播放 GIF")
