import os
from moviepy.editor import VideoFileClip

def convert_gifs_to_mp4(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for filename in os.listdir(source_dir):
        if filename.endswith(".gif"):
            gif_path = os.path.join(source_dir, filename)
            mp4_path = os.path.join(target_dir, filename.replace(".gif", ".mp4"))
            
            print(f"正在转换: {filename}...")
            try:
                clip = VideoFileClip(gif_path)
                # 使用 libx264 编码，保证网页兼容性
                clip.write_videofile(mp4_path, codec="libx264", audio=False)
                clip.close()
            except Exception as e:
                print(f"转换 {filename} 失败: {e}")

if __name__ == "__main__":
    # 根据你的项目结构调整路径
    source = os.path.join("static", "gif_cache")
    target = os.path.join("static", "video_cache")
    convert_gifs_to_mp4(source, target)
    print("转换完成！")