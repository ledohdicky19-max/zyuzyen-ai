import streamlit as st
import os
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

st.set_page_config(page_title="Zyuzyen AI", layout="centered")
st.title("🎬 Zyuzyen AI - Web App")

# 1. Input Kustomisasi
bg_file = st.file_uploader("Upload Background:", type=["png", "jpg"])
logo_file = st.file_uploader("Upload Logo (Opsional):", type=["png", "jpg"])
nama_akun = st.text_input("Nama Akun/Watermark Teks:", "@ZyuzyenAI")

# 2. Input Video
tab1, tab2 = st.tabs(["📁 Upload Video", "🔗 Link YouTube"])
input_video_path = None
with tab1:
    up_file = st.file_uploader("Video:", type=["mp4"])
    if up_file:
        input_video_path = f"temp_{up_file.name}"
        with open(input_video_path, "wb") as f: f.write(up_file.getbuffer())
with tab2:
    link_yt = st.text_input("Link YouTube:")

col1, col2 = st.columns(2)
with col1: durasi_menit = st.number_input("Durasi (menit):", min_value=1, value=1)
with col2: jumlah_klip = st.number_input("Jumlah klip:", min_value=1, value=1)

if st.button("Proses & Download"):
    if not bg_file or (not input_video_path and not link_yt):
        st.error("⚠️ Lengkapi data!")
    else:
        with st.spinner('Sedang memproses video...'):
            try:
                if link_yt:
                    ydl_opts = {'format': 'best', 'outtmpl': 'input.mp4'}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([link_yt])
                    input_video_path = "input.mp4"
                
                with open("temp_bg.jpg", "wb") as f: f.write(bg_file.getbuffer())
                
                video = VideoFileClip(input_video_path)
                bg = ImageClip("temp_bg.jpg").set_duration(durasi_menit * 60)
                
                if not os.path.exists("output"): os.makedirs("output")
                
                for i in range(jumlah_klip):
                    start = i * (durasi_menit * 60)
                    clip = video.subclip(start, start + (durasi_menit * 60))
                    
                    layers = [bg.resize(clip.size), clip.set_position("center")]
                    if logo_file:
                        with open("temp_logo.png", "wb") as f: f.write(logo_file.getbuffer())
                        logo = ImageClip("temp_logo.png").resize(height=50).set_position(('left', 'top'))
                        layers.append(logo)
                        
                    output_path = f"output/klip_{i+1}.mp4"
                    final = CompositeVideoClip(layers)
                    final.write_videofile(output_path, codec="libx264")
                    
                    # 3. Tombol Download Otomatis
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label=f"⬇️ Download Klip {i+1}",
                            data=file,
                            file_name=f"klip_{i+1}.mp4",
                            mime="video/mp4"
                        )
                
                st.success("✅ Semua klip siap diunduh!")
            except Exception as e:
                st.error(f"Error: {e}")
