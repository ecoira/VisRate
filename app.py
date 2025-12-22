import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# =============================
# 1. 基础配置与工具函数
# =============================
st.set_page_config(
    page_title="电子游戏评级信息研究平台",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_video_base64(file_path):
    """将视频转换为Base64以解决Streamlit播放刷新问题"""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

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
# 2. 数据配置
# =============================
GAMES_DATA = {
    "Red Dead Redemption 2": {
        "prefix": "Red",
        "esrb_level": "17+ (M - Mature)",
        "keywords": "鲜血与血腥, 强烈暴力 (Blood and Gore, Intense Violence)",
        "summary": "玩家使用旧西部武器进行第一人称和第三人称战斗。慢动作镜头展示了子弹穿透敌人，血液从伤口喷涌而出的画面。一个使用加特林机枪的任务导致角色的肢体和面部血肉横飞。游戏中包含酷刑和屠杀的场景。",
        "video_duration_str": "01:01:03",
        "raw_events": [
            {"start_time": "07:30", "end_time": "11:23", "level": 2, "keywords": "与人枪战", "gif_timestamp": "09:29"},
            {"start_time": "14:28", "end_time": "16:15", "level": 1, "keywords": "空手打斗", "gif_timestamp": "15:47"},
            {"start_time": "26:34", "end_time": "27:04", "level": 1, "keywords": "马的尸体", "gif_timestamp": "26:38"},
            {"start_time": "31:05", "end_time": "36:50", "level": 2, "keywords": "与野兽枪战", "gif_timestamp": "34:02"},
            {"start_time": "51:04", "end_time": "59:36", "level": 2, "keywords": "与人枪战", "gif_timestamp": "55:02"},
        ]
    },
    "Detroit: Become Human": {
        "prefix": "Detroit",
        "esrb_level": "17+ (M - Mature)",
        "keywords": "含血液, 强烈暴力 (Blood, Intense Violence)",
        "summary": "玩家角色经常以各种方式对其他角色进行拳打、射击、刺伤和伤害。展示了血迹斑斑的尸体和处决场面。此外，还有家庭暴力的场景，既有屏幕上直接展示的，也有暗示或发生在屏幕之外的。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "prefix": "Hades",
        "esrb_level": "13+ (T - Teenager)",
        "keywords": "含血液, 暴力 (Blood, Violence)",
        "summary": "战斗是这款动作游戏的核心。你会看到一些血溅效果，当主角“死亡”时，你可能会看到他被尖刺刺穿，或者脸朝下倒在一滩血泊中。战斗中可以使用各种武器及魔法攻击。",
        "video_duration_str": "01:00:22",
        "raw_events": [
            {"start_time": "01:10", "end_time": "06:10", "level": 1, "keywords": "战斗场景", "gif_timestamp": "05:14"},
            {"start_time": "37:48", "end_time": "42:47", "level": 1, "keywords": "战斗场景", "gif_timestamp": "42:40"},
        ]
    }
}

# =============================
# 3. 各子系统界面函数
# =============================

def show_system_1():
    st.header("📊 系统一：暴力程度时间轴分析")
    
    LEVEL_MAP = {1: "轻度", 2: "中度", 3: "重度"}
    LEVEL_ORDER = ["轻度", "中度", "重度"]
    
    selected_game = st.selectbox("选择游戏", list(GAMES_DATA.keys()), key="s1_game")
    game_cfg = GAMES_DATA[selected_game]

    st.subheader("📄 游戏内容总结")
    st.markdown(f'<div style="background-color:#f5f7fa; padding:20px; border-radius:8px; font-size:20px; color:#2c3e50;">{game_cfg["summary"]}</div>', unsafe_allow_html=True)

    st.subheader("📈 暴力程度时间轴")
    events = []
    base_time = pd.Timestamp("1970-01-01")
    total_sec = time_str_to_seconds(game_cfg["video_duration_str"])
    end_video_time = base_time + pd.Timedelta(seconds=total_sec)

    for idx, e in enumerate(game_cfg["raw_events"]):
        events.append({
            "ID": idx,
            "start": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["start_time"])),
            "end": base_time + pd.Timedelta(seconds=time_str_to_seconds(e["end_time"])),
            "level": LEVEL_MAP[e["level"]],
            "gif_timestamp_str": e["gif_timestamp"]
        })
    
    df = pd.DataFrame(events)
    for lvl in LEVEL_ORDER:
        if lvl not in df["level"].values:
            df = pd.concat([df, pd.DataFrame([{"ID": -1, "start": base_time, "end": base_time, "level": lvl}])])

    fig = px.timeline(
        df, x_start="start", x_end="end", y="level", color="level",
        category_orders={"level": LEVEL_ORDER},
        custom_data=["ID"],
        color_discrete_map={"轻度": "#FDB462", "中度": "#FB6A4A", "重度": "#CB181D"},
        range_x=[base_time, end_video_time]
    )
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=20), xaxis=dict(tickformat="%H:%M:%S", title="视频时间"), yaxis=dict(title=None))
    
    selected_point = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    st.subheader("🎬 事件动态预览")
    selection = selected_point.get("selection", {}).get("points", [])
    if selection:
        clicked_id = selection[0].get("customdata", [-1])[0]
        if clicked_id != -1:
            row = df[df["ID"] == clicked_id].iloc[0]
            prefix = game_cfg["prefix"]
            ts_str = row["gif_timestamp_str"]
            vid_path = os.path.join("static", "video_cache", f"{prefix}_evt_{clicked_id}_{time_str_to_seconds(ts_str)}s.mp4")
            
            v_base64 = get_video_base64(vid_path)
            if v_base64:
                st.markdown(f'<video width="900" autoplay loop muted playsinline><source src="data:video/mp4;base64,{v_base64}" type="video/mp4"></video>', unsafe_allow_html=True)
            else:
                st.error(f"找不到视频文件: {vid_path}")
    else:
        st.info("💡 请点击上方时间轴中的彩色方块查看视频片段")

def show_system_2():
    st.header("🖼️ 系统二：ESRB 游戏年龄评级")
    selected_game = st.selectbox("选择游戏", list(GAMES_DATA.keys()), key="s2_game")
    data = GAMES_DATA[selected_game]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📋 评级详情")
        st.markdown(f"""
        **年龄评级:** <span style="font-size:24px; color:#e74c3c;">{data['esrb_level']}</span>  
        **关键提示词:** {data['keywords']}  
        **详细描述:** <div style="background-color:#fdfefe; padding:15px; border-left:5px solid #3498db; font-size:18px;">{data['summary']}</div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("🖼️ 评级示意图")
        img_path = os.path.join("static", "images", f"{data['prefix']}_cover.png")
        if os.path.exists(img_path):
            st.image(img_path, caption=f"{selected_game} 评级参考图", use_container_width=True)
        else:
            st.warning(f"图片未找到: {img_path}")

def show_system_3():
    st.header("🎥 系统三：Common Sense Media 暴力内容总结")
    selected_game = st.selectbox("选择游戏", list(GAMES_DATA.keys()), key="s3_game")
    data = GAMES_DATA[selected_game]

    st.subheader("📄 暴力行为描述")
    st.markdown(f'<div style="font-size:22px; padding:10px; color:#2c3e50;">{data["summary"]}</div>', unsafe_allow_html=True)

    st.subheader("📽️ 暴力内容典型片段演示")
    vid_path = os.path.join("static", "videos", f"{data['prefix']}_demo.mp4")
    v_base64 = get_video_base64(vid_path)
    if v_base64:
        st.markdown(f'<video width="100%" controls autoplay loop muted><source src="data:video/mp4;base64,{v_base64}" type="video/mp4"></video>', unsafe_allow_html=True)
    else:
        st.warning(f"视频演示文件未找到: {vid_path}")

# =============================
# 4. 页面导航逻辑
# =============================

# 初始化页面状态
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    # --- 欢迎页面渲染 ---
    st.write("# ")
    st.markdown("<h1 style='text-align: center;'>欢迎您参加关于“电子游戏评级信息呈现方式”的学术研究项目</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # 居中对齐容器
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.write("### 请选择下方其中一个系统进行体验：")
        # 修改为竖向排列
        if st.button("🚀 系统 1：暴力时间轴分析", use_container_width=True):
            st.session_state.page = "系统 1"
            st.rerun()
        
        st.write("") # 增加间距
        if st.button("🖼️ 系统 2：静态信息展示", use_container_width=True):
            st.session_state.page = "系统 2"
            st.rerun()
            
        st.write("") # 增加间距
        if st.button("🎥 系统 3：动态语义展示", use_container_width=True):
            st.session_state.page = "系统 3"
            st.rerun()

else:
    # --- 进入系统后的侧边栏 ---
    with st.sidebar:
        st.title("🚀 系统切换")
        # 修复逻辑点：确保选项字符串与下方 if 判断一致
        nav_selection = st.radio(
            "前往：",
            ["系统 1", "系统 2", "系统 3"],
            index=["系统 1", "系统 2", "系统 3"].index(st.session_state.page)
        )
        if nav_selection != st.session_state.page:
            st.session_state.page = nav_selection
            st.rerun()
        
        st.write("---")
        if st.button("⬅️ 返回主页"):
            st.session_state.page = 'home'
            st.rerun()

    # --- 页面内容路由渲染 ---
    # 修复逻辑点：移除多余的后缀，确保与 session_state.page 字符串完全匹配
    if st.session_state.page == "系统 1":
        show_system_1()
    elif st.session_state.page == "系统 2":
        show_system_2()
    elif st.session_state.page == "系统 3":
        show_system_3()