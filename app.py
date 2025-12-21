import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

LEVEL_ORDER = ["轻度", "中度", "重度"]

# =============================
# 游戏配置
# =============================
# ✅ 根据截图修正了 file_prefix
GAMES_CONFIG = {
    "Red Dead Redemption 2": {
        "file_prefix": "Red", # 截图显示为 Red_evt_...
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
        "file_prefix": "Detroit:", # 截图显示为 Detroit:_evt_... (注意冒号)
        "summary": "本作的核心剧情聚焦于仿生人与人类之间的尖锐冲突，并深入探讨了仿生人内部的分裂——例如，作为执法者的仿生人与其普通同类之间的对立。游戏中包含对犯罪现场的直接描绘，其中会涉及人类尸体与血迹。此外，剧情还包含枪击仿生人的暴力场面，其标志性的蓝色血液是本作一个独特的视觉特征。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "file_prefix": "Hades", # 截图显示为 Hades_evt_...
        "summary": "快节奏的动作战斗是核心玩法，玩家在游戏中主要操控剑、矛、盾、弓等神话冷兵器与冥界怪物进行高频率的砍杀对抗。当敌人或玩家受伤时，画面会出现鲜红的血液喷溅特效和地面积血细节，但敌人死亡后通常会化为光点或烟雾迅速消散。",
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
# 工具函数：时间字符串转秒
# =============================
def time_str_to_seconds(t: str) -> int:
    parts = t.split(":")
    if len(parts) == 2:      # MM:SS
        m, s = parts
        return int(m) * 60 + int(s)
    elif len(parts) == 3:    # HH:MM:SS
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    return 0


# =============================
# 选择游戏
# =============================
selected_game = st.selectbox(
    "选择游戏",
    list(GAMES_CONFIG.keys())
)

game_cfg = GAMES_CONFIG[selected_game]

# =============================
# 🔥 动态标题
# =============================
st.title(f"🎮 {selected_game} 暴力内容分析")

# ======================================================
# 🧱 区域一：游戏内容总结
# ======================================================
with st.container():
    st.subheader("📄 游戏内容总结")

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
# 🧱 区域二：暴力程度时间轴
# ======================================================
with st.container():
    st.subheader("📊 暴力程度时间轴")

    events = []
    
    # 基准日期，用于 Plotly 时间轴计算
    base_time = pd.Timestamp("1970-01-01")
    
    total_duration_sec = time_str_to_seconds(game_cfg["video_duration_str"])
    end_video_time = base_time + pd.Timedelta(seconds=total_duration_sec)

    for idx, e in enumerate(game_cfg["raw_events"]):
        start_s = time_str_to_seconds(e["start_time"])
        end_s = time_str_to_seconds(e["end_time"])

        events.append({
            "ID": idx,
            "start": base_time + pd.Timedelta(seconds=start_s),
            "end": base_time + pd.Timedelta(seconds=end_s),
            "level": LEVEL_MAP[e["level"]],
            "keywords": e["keywords"],
            "gif_timestamp_str": e["gif_timestamp"]
        })

    df = pd.DataFrame(events)

    # ✅ 强制补齐三个等级（即使没有事件）
    for lvl in LEVEL_ORDER:
        if df.empty or lvl not in df["level"].values:
            df = pd.concat([
                df,
                pd.DataFrame([{
                    "ID": -1,
                    "start": base_time,
                    "end": base_time + pd.Timedelta(seconds=0.1), # 极短时间
                    "level": lvl,
                    "keywords": "无事件",
                    "gif_timestamp_str": ""
                }])
            ])
    
    df = df.reset_index(drop=True)

    fig = px.timeline(
        df,
        x_start="start",
        x_end="end",
        y="level",
        color="level",
        category_orders={"level": LEVEL_ORDER},
        custom_data=["ID"], # ✅ 将 ID 注入 custom_data 供点击捕获
        color_discrete_map={
            "轻度": "#FDB462",
            "中度": "#FB6A4A",
            "重度": "#CB181D"
        },
        range_x=[base_time, end_video_time]
    )

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=10, b=20),
        showlegend=True,
        xaxis=dict(
            tickformat="%H:%M:%S",
            title="视频时间"
        )
    )

    selected = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun" # 必须开启 rerun 才能捕获点击
    )

# ======================================================
# 🧱 区域三：事件动态预览
# ======================================================
with st.container():
    st.subheader("🎬 事件动态预览")

    selected_row = None
    
    try:
        if selected and selected.get("selection") and selected["selection"].get("points"):
            # ✅ 修复核心：通过 customdata[0] 获取 ID
            point_data = selected["selection"]["points"][0]
            if "customdata" in point_data:
                clicked_id = point_data["customdata"][0]
                # 根据 ID 在数据框中过滤出行
                matching_rows = df[df["ID"] == clicked_id]
                if not matching_rows.empty:
                    selected_row = matching_rows.iloc[0]
    except Exception as e:
        st.error(f"处理点击事件时发生错误: {e}")

    # 显示逻辑
    if selected_row is not None:
        evt_id = selected_row["ID"]
        
        if evt_id == -1:
            st.info("该暴力等级下未检测到具体事件，但已完成检测与分类。")
        else:
            # 准备文件路径
            prefix = game_cfg["file_prefix"]
            gif_time_str = selected_row["gif_timestamp_str"]
            gif_seconds = time_str_to_seconds(gif_time_str)
            
            # 拼接文件名：{前缀}_evt_{ID}_{秒数}s.gif
            gif_filename = f"{prefix}_evt_{evt_id}_{gif_seconds}s.gif"
            gif_path = os.path.join("gif_cache", gif_filename)

            if os.path.exists(gif_path):
                col1, col2 = st.columns([1.5, 1])
                with col1:
                    st.image(
                        gif_path,
                        use_container_width=True,
                        key=f"img_{prefix}_{evt_id}" 
                    )
                with col2:
                    st.markdown("### 事件详情")
                    st.markdown(f"**关键词**：{selected_row['keywords']}")
                    st.markdown(f"**暴力等级**：{selected_row['level']}")
                    st.markdown(f"**发生时间**：{game_cfg['raw_events'][evt_id]['start_time']} - {game_cfg['raw_events'][evt_id]['end_time']}")
            else:
                st.warning(f"GIF 文件丢失")
                st.caption(f"系统尝试读取路径: `{gif_path}`，但文件不存在。请检查 `gif_cache` 文件夹。")
    else:
        st.info("💡 请点击上方时间轴中的【彩色方块】以查看对应动态预览")