import streamlit as st
import cv2
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import numpy as np

from pipeline_models.biometric_pipeline import BiometricPreprocessorPipeline
from pipeline_models.frame_preprocessor import FramePreprocessor
from pipeline_models.mediapipe_face_detector import MediaPipeFaceDetector
from pipeline_models.face_geometric_normalizer import FaceGeometricNormalizer
from pipeline_models.temporal_landmarks_smoother import TemporalLandmarksSmoother

st.set_page_config(page_title="biometric-face-preprocessor — Live Demo", layout="wide")
st.title("biometric-face-preprocessor")
st.caption("Live-камера + полный пайплайн по ГОСТ Р 52633 (шаги 1–3)")

# Инициализация пайплайна
if "pipeline" not in st.session_state:
    pipeline = BiometricPreprocessorPipeline()
    pipeline.add_step(FramePreprocessor(use_grayscale=True))
    pipeline.add_step(MediaPipeFaceDetector(min_detection_confidence=0.85, padding_ratio=0.15))
    pipeline.add_step(FaceGeometricNormalizer(target_size=224))
    pipeline.add_step(TemporalLandmarksSmoother(alpha=0.75))
    st.session_state.pipeline = pipeline

pipeline = st.session_state.pipeline

# ====================== БОКОВАЯ ПАНЕЛЬ ======================
st.sidebar.header("Управление пайплайном")

# Выбор шага для отображения
preview_options = ["raw", "frame_preprocessing", "face_detection", "geometric_normalization", "temporal_landmarks_smoother"]
preview_step = st.sidebar.selectbox(
    "Отображать результат после шага",
    preview_options,
    index=3,
    help="raw = чистая камера"
)

# Параметры текущего шага (только если не raw)
st.sidebar.subheader("Параметры текущего шага")

if preview_step == "frame_preprocessing":
    clahe_clip = st.sidebar.slider("CLAHE clip_limit", 0.0, 5.0, 2.0, 0.1)
    use_gray = st.sidebar.checkbox("Use grayscale", value=True)

elif preview_step == "face_detection":
    conf = st.sidebar.slider("min_detection_confidence", 0.5, 1.0, 0.85, 0.05)
    pad = st.sidebar.slider("ROI padding ratio", 0.05, 0.30, 0.15, 0.01)

elif preview_step == "geometric_normalization":
    target_size = st.sidebar.slider("Target size (px)", 160, 320, 224, 16)
    target_ipd = st.sidebar.slider("Target inter-pupil distance", 60.0, 140.0, 100.0, 1.0)

elif preview_step == "temporal_landmarks_smoother":
    alpha = st.sidebar.slider("EMA alpha (сглаживание)", 0.5, 0.95, 0.75, 0.05)

# Кнопка применения параметров
if st.sidebar.button("Применить параметры", type="primary", use_container_width=True):
    if preview_step == "frame_preprocessing":
        pipeline.update_step_params("frame_preprocessing",
                                    clahe_clip_limit=clahe_clip,
                                    use_grayscale=use_gray)
    elif preview_step == "face_detection":
        pipeline.update_step_params("face_detection",
                                    min_detection_confidence=conf,
                                    padding_ratio=pad)
    elif preview_step == "geometric_normalization":
        pipeline.update_step_params("geometric_normalization",
                                    target_size=target_size,
                                    target_inter_pupil_distance=target_ipd)
    elif preview_step == "temporal_landmarks_smoother":
        pipeline.update_step_params("temporal_landmarks_smoother", alpha=alpha)

    st.sidebar.success("✅ Параметры применены")
    st.rerun()

# ====================== ОБРАБОТКА КАДРОВ ======================
def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    # Останавливаем пайплайн на выбранном шаге
    stop_step = None if preview_step == "raw" else preview_step
    context = pipeline.process_single_frame(img, stop_after_step=stop_step)
    # Получаем нужную картинку
    preview = pipeline.get_preview_frame(context, preview_step)
    return av.VideoFrame.from_ndarray(preview, format="bgr24")


col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Live-камера")
    webrtc_streamer(
        key="biometric",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.subheader("Статус")
    st.info(f"Текущий preview: **{preview_step}**")
    st.caption("Параметры применяются только после нажатия кнопки")
    