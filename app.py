import streamlit as st
from utils import *
from PIL import Image
import time
import io
import subprocess
import cv2

# Initialize session state for settings
if 'obj_thresh' not in st.session_state:
    st.session_state['obj_thresh'] = 0.4
if 'nms_thresh' not in st.session_state:
    st.session_state['nms_thresh'] = 0.45
if 'image_format' not in st.session_state:
    st.session_state['image_format'] = 'PNG'

# Function to reset settings to default
def reset_settings():
    st.session_state['obj_thresh'] = 0.4
    st.session_state['nms_thresh'] = 0.45
    st.session_state['image_format'] = 'PNG'
    st.rerun()  # Reload the entire app

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        height: 100%;
        margin: 0;
    }
    [data-testid="stApp"] {
        display: flex;
        flex-direction: column;
    }
    .main-content {
        flex: 1 0 auto;
    }
    .title {
        color: #c6ccd5;
        font-size: 3em;
        font-family: 'IBM Plex Sans', sans-serif;
        text-align: center;
        margin-bottom: 0.2em;
        font-weight: 600;
    }
    .subheader {
        color: #9aa1aa;
        font-size: 1.5em;
        font-family: 'IBM Plex Sans', sans-serif;
        text-align: center;
        margin-bottom: 2em;
        font-weight: 400;
    }
    .footer {
        flex-shrink: 0;
        color: #999999;
        text-align: center;
        margin-top: 2em;
        font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Object Detection Project</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Precision Object Detection for Transportation</div>', unsafe_allow_html=True)

# Sidebar settings
st.sidebar.header("Settings")

# Object Threshold
st.sidebar.subheader("Object Threshold")
st.sidebar.write("The Object Threshold controls the confidence level required to detect an object. "
                 "A higher value means fewer but more confident detections, while a lower value means more detections but with less confidence.")
st.session_state['obj_thresh'] = st.sidebar.slider('Adjust Object Threshold', 0.0, 1.0, st.session_state['obj_thresh'])

# Non-max Suppression Threshold
st.sidebar.subheader("Non-max Suppression Threshold")
st.sidebar.write("The Non-max Suppression (NMS) Threshold controls the overlap allowed between detected objects. "
                 "A lower value means stricter overlap rules, which reduces duplicate detections, while a higher value allows more overlap.")
st.session_state['nms_thresh'] = st.sidebar.slider('Adjust NMS Threshold', 0.0, 1.0, st.session_state['nms_thresh'])

# Image Format
st.sidebar.subheader("Output Image Format")
st.session_state['image_format'] = st.sidebar.selectbox('Choose Format', ('PNG', 'JPEG'), index=['PNG', 'JPEG'].index(st.session_state['image_format']))

# Reset button
if st.sidebar.button('Reset'):
    reset_settings()

# File uploader
uploaded_file = st.file_uploader("Choose an image or video...", type=["jpg", "png", "mp4"])

# Try an example button
example_image_path = "preview16.jpg"
example_video_converted = 'example_video_converted.mp4'

# Function to load example files as BytesIO objects
def load_example_as_bytesio(file_path):
    with open(file_path, "rb") as f:
        return io.BytesIO(f.read())

# Load example files into BytesIO objects
example_image = load_example_as_bytesio(example_image_path)

# Buttons for example image and video
if st.button('Try an Example Image', type="primary"):
    uploaded_file = example_image
    uploaded_file.name = "example_image.jpg"

# EXAMPLE VIDEO
#########################
if 'try_example' not in st.session_state:
    st.session_state.try_example = False
if 'play_video' not in st.session_state:
    st.session_state.play_video = False
if 'run_detection' not in st.session_state:
    st.session_state.run_detection = False

# Function to reset states when 'Try an Example Video' is clicked
def reset_states():
    st.session_state.play_video = False
    st.session_state.run_detection = False
def reset_all_states():
    st.session_state.try_example = False
    st.session_state.play_video = False
    st.session_state.run_detection = False

# Handle 'Try an Example Video' button
if st.button('Try an Example Video', type="primary"):
    st.session_state.try_example = True
    reset_states()

# try:
if st.session_state.try_example:
    # Handle 'Play Pre-detected Video' button
    if st.button('Play Pre-detected Video'):
        st.session_state.play_video = True
        st.session_state.run_detection = False  # Ensure the other option is not active

    # Handle 'Run Detection on Video' button
    if st.button('Run Detection on Video'):
        st.session_state.run_detection = True
        st.session_state.play_video = False  # Ensure the other option is not active

    # Show videos based on the button clicked
    if st.session_state.play_video:
        st.write("Example video:")
        st.video("example_video.mp4")
        st.write("")
        st.write("Example video detected:")
        st.video("example_video_converted.mp4")
        reset_all_states()

    if st.session_state.run_detection:
        st.video("example_video.mp4")
        st.write("Processing video with object detection...")
        video_path = "example_video.mp4"
        output_path = "detected_video.mp4"

        detect_video(video_path, output_path, obj_thresh=st.session_state['obj_thresh'], nms_thresh=st.session_state['nms_thresh'])

        output_path1 = "detected_video1.mp4"
        command = f"ffmpeg -y -i {output_path} -vcodec libx264 {output_path1}"
        subprocess.call(command, shell=True)
        st.toast('🎉 Done!', icon='✅')
        st.write("")
        st.write("Detected video:")
        st.video(output_path1)

        with open(output_path1, "rb") as file:
            st.download_button(
                label="📥 Download Video [MP4]",
                data=file,
                file_name="detected_video.mp4",
                mime="video/mp4"
            )
        reset_all_states()
############################
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension in ["jpg", "png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("")

        with st.status("Detecting..."):
            st.write("🚀 Processing image...")
            time.sleep(0.5)
            st.write("🔍 Localizing objects...")
            detected_image = detect_image(image, obj_thresh=st.session_state['obj_thresh'], nms_thresh=st.session_state['nms_thresh'])
            st.write("🏷️ Labelling...")
            time.sleep(1)
        st.toast('🎉 Done!', icon='✅')
        if type(detected_image) == str:
            st.write("")
            if st.session_state['obj_thresh'] >= 0.6:
                st.write("No objects detected. Try lowering the Object Threshold.")
            else:
                st.write(detected_image)
        else:
            st.image(detected_image, caption='Detected Image.', use_column_width=True)

            # Convert the image to a BytesIO object and provide a download button
            buffer = io.BytesIO()
            detected_image.save(buffer, format=st.session_state['image_format'])
            buffer.seek(0)

            st.download_button(
                label=f"📥 Download image [High Quality - {st.session_state['image_format']}]",
                data=buffer,
                file_name=f"detected_image.{st.session_state['image_format'].lower()}",
                mime=f"image/{st.session_state['image_format'].lower()}"
            )

    elif file_extension in ["mp4"]:
        with open("video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        example_video = "video1.mp4"
        if uploaded_file != example_video:
            video_path = "video.mp4"
        st.write("Uploaded video:")
        st.video(uploaded_file)
        output_path = "detected_video.mp4"

        detect_video(video_path, output_path, obj_thresh=st.session_state['obj_thresh'], nms_thresh=st.session_state['nms_thresh'])

        output_path1 = "detected_video1.mp4"
        command = f"ffmpeg -y -i {output_path} -vcodec libx264 {output_path1}"
        subprocess.call(command, shell=True)
        st.toast('🎉 Done!', icon='✅')
        st.write("")
        st.write("Detected video:")
        st.video(output_path1)

        with open(output_path1, "rb") as file:
            st.download_button(
                label="📥 Download Video [MP4]",
                data=file,
                file_name="detected_video.mp4",
                mime="video/mp4"
            )

for i in range(7):
    st.write("")
st.markdown('<div class="footer">This app uses YOLOv3 to detect objects in images and videos</div>', unsafe_allow_html=True)
st.write("")
st.markdown('<div class="footer">A project by Kevin Chang</div>', unsafe_allow_html=True)
