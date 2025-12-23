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
        "violence_score": 5,  # 新增：5分
        "keywords": "鲜血与血腥, 强烈暴力 (Blood and Gore, Intense Violence)",
        "summary1": "本作包含频繁的第一人称及第三人称枪战，并通过慢动作镜头特写子弹穿透敌人、血液自伤口喷涌而出的暴力画面。此外，游戏中还存在野兽撕咬人类并导致大量出血的血腥场景，以及静态的动物尸体图像。",
        "summary3": "玩家使用旧西部武器（左轮手枪、步枪、霰弹枪、猎刀、战斧）进行第一人称和第三人称战斗。慢动作镜头展示了子弹穿透敌人，血液从伤口喷涌而出的画面。一个使用加特林机枪的任务导致角色的肢体和面部血肉横飞。游戏中包含酷刑和屠杀的场景，例如有人被吊在树上，早已被遗弃的干瘪腐烂的尸体，以及一个流血的躯干被悬挂在桥下，内脏滴落到地面上，形成一滩血污。",
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
        "violence_score": 4,  # 新增：5分
        "keywords": "含血液, 强烈暴力 (Blood, Intense Violence)",
        "summary1": "本作的核心剧情聚焦于仿生人与人类之间的尖锐冲突，游戏中包含对犯罪现场的直接描绘，其中会涉及人类尸体与血迹。此外，剧情还包含枪击仿生人的暴力场面，其标志性的蓝色血液是本作一个独特的视觉特征。",
        "summary3": "玩家角色经常以各种方式对其他角色进行拳打、射击、刺伤和伤害。展示了血迹斑斑的尸体和处决场面。此外，还有家庭暴力的场景，既有屏幕上直接展示的，也有暗示或发生在屏幕之外的。",
        "video_duration_str": "01:00:06",
        "raw_events": [
            {"start_time": "02:20", "end_time": "09:29", "level": 1, "keywords": "案发现场", "gif_timestamp": "02:27"},
            {"start_time": "15:13", "end_time": "16:45", "level": 1, "keywords": "枪击仿生人", "gif_timestamp": "16:09"},
        ]
    },
    "Hades": {
        "prefix": "Hades",
        "esrb_level": "13+ (T - Teenager)",
        "violence_score": 3,  # 新增：5分
        "keywords": "含血液, 暴力 (Blood, Violence)",
        "summary1": "快节奏的动作战斗是核心玩法，玩家在游戏中主要操控剑、矛、盾、弓等神话冷兵器与冥界怪物进行高频率的砍杀对抗。当敌人或玩家受伤时，画面会出现鲜红的血液喷溅特效和地面积血细节，但敌人死亡后通常会化为光点或烟雾迅速消散。",
        "summary3": "战斗是这款动作游戏的核心，但尽管暴力场面不少，游戏却并非写实风格，也没有采用沉浸式视角（例如第一人称视角或虚拟现实）。你会看到一些血溅效果，当你的主角“死亡”（没错，他是永生的，但他会耗尽能量）时，你可能会看到他被尖刺刺穿，或者脸朝下倒在一滩血泊中。战斗中可以使用各种武器（剑、锤子、弓箭），以及随着游戏进程获得的魔法攻击。",
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
# 3. 各子系统界面函数
# =============================

def show_system_1():
    # 1. 状态初始化
    if 'guide_active' not in st.session_state:
        st.session_state.guide_active = True

    st.header("📊 系统一：Vis-Rate 暴力程度时间轴分析")
    
    LEVEL_MAP = {1: "轻度", 2: "中度", 3: "重度"}
    LEVEL_ORDER = ["轻度", "中度", "重度"]
    
    game_list = list(GAMES_DATA.keys())
    selected_game = st.selectbox("选择游戏", game_list, key="s1_game")
    game_cfg = GAMES_DATA[selected_game]

    # --- 核心修复逻辑：在所有组件渲染前获取点击数据 ---
    # 直接从 session_state 缓存中读取，这样即使图表刷新，点击数据也不会丢失
    selection_state = st.session_state.get("timeline_chart", {})
    points = selection_state.get("selection", {}).get("points", [])
    
    clicked_info = None
    if points:
        # 只要有点选动作，立即关闭引导
        st.session_state.guide_active = False
        # 提取点击的 ID 和 时间戳字符串
        clicked_info = points[0].get("customdata")

    # 2. 数据准备
    st.subheader("📄 游戏内容总结")
    st.markdown(f'<div style="background-color:#f5f7fa; padding:20px; border-radius:8px; font-size:18px; color:#2c3e50; line-height:1.6;">{game_cfg["summary1"]}</div>', unsafe_allow_html=True)

    events = []
    base_time = pd.Timestamp("1970-01-01")
    total_sec = time_str_to_seconds(game_cfg["video_duration_str"])
    end_video_time = base_time + pd.Timedelta(seconds=total_sec)

    for idx, e in enumerate(game_cfg["raw_events"]):
        start_ts = base_time + pd.Timedelta(seconds=time_str_to_seconds(e["start_time"]))
        end_ts = base_time + pd.Timedelta(seconds=time_str_to_seconds(e["end_time"]))
        events.append({
            "ID": idx,
            "start": start_ts,
            "end": end_ts,
            "center": start_ts + (end_ts - start_ts) / 2,
            "level": LEVEL_MAP[e["level"]],
            "gif_timestamp_str": e["gif_timestamp"]
        })
    
    df = pd.DataFrame(events)
    for lvl in LEVEL_ORDER:
        if lvl not in df["level"].values:
            df = pd.concat([df, pd.DataFrame([{"ID": -1, "start": base_time, "end": base_time, "level": lvl}])])

    # 3. 构造图表
    fig = px.timeline(
        df, x_start="start", x_end="end", y="level", color="level",
        category_orders={"level": LEVEL_ORDER},
        custom_data=["ID", "gif_timestamp_str"],
        color_discrete_map={"轻度": "#FDB462", "中度": "#FB6A4A", "重度": "#CB181D"},
        range_x=[base_time, end_video_time]
    )

    # --- 引导 UI：移到方块下方 (ay 正值) ---
    if selected_game == game_list[0] and st.session_state.guide_active:
        target_row = df.iloc[0]
        fig.add_annotation(
            x=target_row['center'],
            y=target_row['level'],
            text="✨ 点击查看 3s 事件视频",
            showarrow=True, 
            arrowhead=3, 
            arrowsize=1.2, 
            arrowwidth=2,
            ax=0, 
            ay=55,  # 设置为正值，使引导气泡出现在方块下方
            font=dict(size=15, color="#333"),
            bgcolor="#FFF9C4", 
            bordercolor="#FBC02D",
            borderwidth=2, 
            borderpad=8, 
            opacity=0.95
        )

    fig.update_layout(
        height=240, 
        margin=dict(l=20, r=20, t=10, b=20), 
        xaxis=dict(tickformat="%M:%S", title="视频时间轴"), 
        yaxis=dict(title=None, tickfont=dict(size=14))
    )
    
    # 渲染图表（必须保留 key="timeline_chart"）
    st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="timeline_chart")

    # 4. 视频显示逻辑（使用在代码开头截获的点击信息）
    st.subheader("🎬 事件动态预览")
    
    if clicked_info and clicked_info[0] != -1:
        clicked_id = clicked_info[0]
        ts_str = clicked_info[1]
        prefix = game_cfg["prefix"]
        vid_path = os.path.join("static", "video_cache", f"{prefix}_evt_{clicked_id}_{time_str_to_seconds(ts_str)}s.mp4")
        
        if os.path.exists(vid_path):
            # 这里的视频会随着第一次点击立即渲染
            st.video(vid_path, format="video/mp4", autoplay=True, loop=True, muted=True)
        else:
            st.error(f"找不到视频文件: {vid_path}")
    else:
        st.info("💡 请点击上方时间轴中的彩色方块查看视频片段")

def show_system_2():
    st.header("🖼️ 系统二：ESRB 游戏年龄评级")
    selected_game = st.selectbox("选择游戏", list(GAMES_DATA.keys()), key="s2_game")
    data = GAMES_DATA[selected_game]

    # 修改为上下布局
    st.subheader("📋 评级详情")
    st.markdown(f"""
    <div style="background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:8px solid #e74c3c; margin-bottom:20px;">
        <p style="font-size:20px;"><strong>年龄评级:</strong> <span style="font-size:28px; color:#e74c3c;">{data['esrb_level']}</span></p>
        <p style="font-size:18px;"><strong>暴力相关的关键词:</strong> {data['keywords']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🖼️ 游戏封面图")
    img_path = os.path.join("static", "images", f"{data['prefix']}_cover.png")
    if os.path.exists(img_path):
        # 控制图片宽度，防止在上下布局中显得过大
        st.image(img_path, caption=f"{selected_game} 评级参考图", width=600)
    else:
        st.warning(f"图片未找到: {img_path}")

def show_system_3():
    st.header("🎥 系统三：Common Sense Media 暴力内容总结")
    selected_game = st.selectbox("选择游戏", list(GAMES_DATA.keys()), key="s3_game")
    data = GAMES_DATA[selected_game]

    # --- 核心修改：将频率作为标题 ---
    score = data.get("violence_score", 0)
    filled_circles = "●" * score
    empty_circles = "○" * (5 - score)
    
    # 使用 HTML 模拟图片中的标题样式
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 25px; margin-bottom: 10px;">
            <span style="font-size: 26px; font-weight: bold; margin-right: 20px;">暴力与恐怖频率：</span>
            <span style="font-size: 32px; letter-spacing: 5px;">{filled_circles}{empty_circles}</span>
        </div>
    """, unsafe_allow_html=True)

    # 紧随其后的文字描述块
    st.markdown(f"""
        <div style="font-size:22px; padding:25px; background-color:#fff4f4; border-radius:12px; color:#2c3e50; line-height:1.6; border: 1px solid #ffebeb;">
            {data["summary3"]}
        </div>
    """, unsafe_allow_html=True)

    # 下方的视频演示
    st.write("---") # 添加分割线美化布局
    st.subheader("📽️ 暴力内容典型片段演示")
    vid_path = os.path.join("static", "videos", f"{data['prefix']}_demo.mp4")
    
    if os.path.exists(vid_path):
        st.video(vid_path, format="video/mp4", autoplay=True, loop=True, muted=True)
    else:
        st.warning(f"视频演示文件未找到: {vid_path}")

# =============================
# 4. 页面导航逻辑
# =============================

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.write("# ")
    st.markdown("<h1 style='text-align: center;'>欢迎您参加关于“电子游戏评级信息呈现方式”的学术研究项目</h1>", unsafe_allow_html=True)
    st.write("---")
    
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.write("### 请选择下方其中一个系统进行体验：")
        if st.button("🚀 系统 1：Vis-Rate 暴力程度时间轴分析", use_container_width=True):
            st.session_state.page = "系统 1"
            st.rerun()
        
        st.write("") 
        if st.button("🖼️ 系统 2：ESRB 游戏年龄评级", use_container_width=True):
            st.session_state.page = "系统 2"
            st.rerun()
            
        st.write("") 
        if st.button("🎥 系统 3：Common Sense Media 暴力内容总结", use_container_width=True):
            st.session_state.page = "系统 3"
            st.rerun()

else:
    with st.sidebar:
        st.title("🚀 系统切换")
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

    if st.session_state.page == "系统 1":
        show_system_1()
    elif st.session_state.page == "系统 2":
        show_system_2()
    elif st.session_state.page == "系统 3":
        show_system_3()