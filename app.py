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

LEVEL_MAP = {1: "轻度", 2: "中度", 3: "重度"}
LEVEL_ORDER = ["轻度", "中度", "重度"]

# (GAMES_CONFIG 部分保持不变...)
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "file_prefix": "Red",
        "summary": "本作包含频繁的第一人称及第三人称枪战，并通过慢动作镜头特写子弹穿透敌人、血液自伤口喷涌而出的暴力画面。此外，游戏中还存在野兽撕咬人类并导致大量出血的血腥场景，以及静态的动物尸体图像。",
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
        "summary": "本作的核心剧情聚焦于仿生人与人类之间的尖锐冲突，并深入探讨了仿生人内部的分裂——例如，作为执法者的仿生人与其普通同类之间的对立。游戏中包含对犯罪现场的直接描绘，其中会涉及人类尸体与血迹。此外，剧情还包含枪击仿生人的暴力场面，其标志性的蓝色血液是本作一个独特的视觉特征。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "file_prefix": "Hades",
        "summary": "快节奏的动作战斗是核心玩法，玩家在游戏中主要操控剑、矛、盾、弓等神话冷兵器与冥界怪物进行高频率的砍杀对抗。当敌人或玩家受伤时，画面会出现鲜红的血液喷涌特效和地面积血细节，但敌人死亡后通常会化为光点或烟雾迅速消散。",
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

def time_str_to_seconds(t: str) -> int:
    parts = t.split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    return 0

# =============================
# 选择游戏
# =============================
selected_game = st.selectbox("选择游戏", list(GAMES_CONFIG.keys()))
game_cfg = GAMES_CONFIG[selected_game]

st.title(f"🎮 {selected_game} 暴力内容分析")

# ======================================================
# 🧱 区域一：游戏内容总结 (文字已放大)
# ======================================================
with st.container():
    st.subheader("📄 游戏内容总结")
    st.markdown(
        f"""
        <div style="
            background-color:#f5f7fa;
            padding:20px;
            border-radius:8px;
            line-height:1.8;
            font-size:20px; /* 这里从 15px 改到了 20px */
            font-weight: 400;
            color: #2c3e50;
        ">
        {game_cfg["summary"]}
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# 🧱 区域二：暴力程度时间轴 (坐标轴字体已放大)
# ======================================================
with st.container():
    st.subheader("📊 暴力程度时间轴")

    events = []
    base_time = pd.Timestamp("1970-01-01")
    total_duration_sec = time_str_to_seconds(game_cfg["video_duration_str"])
    end_video_time = base_time + pd.Timedelta(seconds=total_duration_sec)

    for idx, e in enumerate(game_cfg["raw_events"]):
        events.append({
            "ID": idx,
            "start": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["start_time"])),
            "end": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["end_time"])),
            "level": LEVEL_MAP[e["level"]],
            "keywords": e["keywords"],
            "gif_timestamp_str": e["gif_timestamp"]
        })

    df = pd.DataFrame(events)

    # 补充空数据确保 y 轴完整
    for lvl in LEVEL_ORDER:
        if df.empty or lvl not in df["level"].values:
            df = pd.concat([df, pd.DataFrame([{"ID": -1, "start": base_time, "end": base_time + pd.Timedelta(seconds=0.1), "level": lvl, "keywords": "无事件", "gif_timestamp_str": ""}])])

    df = df.reset_index(drop=True)

    fig = px.timeline(
        df, x_start="start", x_end="end", y="level", color="level",
        category_orders={"level": LEVEL_ORDER},
        custom_data=["ID"],
        hover_data={"ID": False, "level": True, "start": True, "end": True}, 
        color_discrete_map={"轻度": "#FDB462", "中度": "#FB6A4A", "重度": "#CB181D"},
        range_x=[base_time, end_video_time]
    )

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=10, b=20),
        showlegend=True,
        xaxis=dict(tickformat="%H:%M:%S", title="视频时间", tickfont=dict(size=14)),
        # 放大 y 轴（轻度、中度、重度）的字体
        yaxis=dict(title=None, tickfont=dict(size=18, color="black")),
        legend=dict(font=dict(size=14))
    )

    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# ======================================================
# 🧱 区域三：事件动态预览 (强制 GIF 动态 + 调整大小)
# ======================================================
# ======================================================
# 🧱 区域三：事件动态预览 (路径修正版)
# ======================================================
with st.container():
    st.subheader("🎬 事件动态预览")

    selected_row = None
    # 保持 selection 获取逻辑不变
    points = selected.get("selection", {}).get("points", [])
    if points:
        point_data = points[0]
        custom_data = point_data.get("customdata", [])
        if custom_data:
            clicked_id = int(custom_data[0])
            if clicked_id != -1:
                match = df[df["ID"] == clicked_id]
                if not match.empty:
                    selected_row = match.iloc[0]

    if selected_row is not None:
        evt_id = int(selected_row["ID"])
        prefix = game_cfg["file_prefix"]
        gif_seconds = time_str_to_seconds(selected_row["gif_timestamp_str"])
        
        gif_filename = f"{prefix}_evt_{evt_id}_{gif_seconds}s.gif"
        
        # 1. Python 后端检查路径（用于确认文件是否存在）
        local_gif_path = os.path.join("static", "gif_cache", gif_filename)
        
        # 2. 浏览器前端访问路径 (关键：必须以 / 开头)
        web_gif_url = f"/app/static/gif_cache/{gif_filename}"

        if os.path.exists(local_gif_path):
            # 渲染图片
            st.markdown(
                f'''
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <img src="{web_gif_url}" width="500" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <p style="margin-top: 10px; font-size: 16px;">
                        <b>事件详情</b>：{selected_row['keywords']} | <b>等级</b>：{selected_row['level']}
                    </p>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            # --- 临时调试代码：如果图片还是不显示，请取消下面这行的注释查看 URL ---
            st.code(f"生成的图片URL: {web_gif_url}")
            
        else:
            # 如果 Python 找不到文件，说明文件名拼接逻辑或目录结构还是有问题
            st.error(f"❌ 找不到文件：{local_gif_path}")
            st.write("请检查该文件是否确实存在于 static/gif_cache/ 目录下。")
    else:
        st.info("💡 请点击上方时间轴中的彩色方块查看视频片段")