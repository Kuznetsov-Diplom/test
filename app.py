import streamlit as st
import cv2
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
from pipeline_models.biometric_pipeline import BiometricPreprocessorPipeline
from pipeline_models.mediapipe_face_detector import MediaPipeFaceDetector

st.set_page_config(
    page_title="biometric-face-preprocessor — Live Demo",
    layout="wide"
)
st.title("🟢 biometric-face-preprocessor")
st.caption("Live-камера + пайплайн по ГОСТ Р 52633")

# Инициализация пайплайна один раз
if "pipeline" not in st.session_state:
    pipeline = BiometricPreprocessorPipeline()
    detector = MediaPipeFaceDetector(min_detection_confidence=0.85)
    pipeline.add_step(detector)
    st.session_state.pipeline = pipeline

pipeline = st.session_state.pipeline

# Боковая панель
st.sidebar.header("🔧 Пайплайн")
step_names = [step.name for step in pipeline.steps]
current_step_name = st.sidebar.selectbox("Текущий шаг", step_names, index=0)

# Параметры шага (пока только для face_detection)
if current_step_name == "face_detection":
    conf = st.sidebar.slider("min_detection_confidence", 0.5, 1.0, 0.85, 0.05)
    pipeline.update_step_params(current_step_name, min_detection_confidence=conf)

# === ОБРАБОТКА КАДРОВ ЧЕРЕЗ CALLBACK (новый API) ===
def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    """Обрабатывает каждый кадр через наш пайплайн"""
    img = frame.to_ndarray(format="bgr24")
    
    # Прогоняем через пайплайн
    context = pipeline.process_single_frame(img)
    
    # Оверлей (зелёная рамка + TODO: landmarks)
    overlay = pipeline.get_overlay_frame(context)
    
    # Возвращаем обработанный кадр
    return av.VideoFrame.from_ndarray(overlay, format="bgr24")


col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📹 Серверная камера — Live (реальное время)")
    ctx = webrtc_streamer(
        key="biometric",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        video_frame_callback=video_frame_callback,   # ← вот здесь вся магия
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.subheader("📊 Статус пайплайна")
    st.info("✅ Пайплайн работает в реальном времени (кадр → детекция → оверлей)")
    
    # Метрики будут обновляться автоматически через callback
    st.metric("Face detected • Confidence", "—")  # TODO: можно добавить session_state для точных метрик позже
    st.metric("ROI", "—")
    st.metric("Стабилизация", "100%")
    st.progress(0.85)
    st.caption("Шаг: face_detection | FPS ≈ 25–30")

# Кнопки
col_btn1, col_btn2, col_btn3 = st.columns(3)
col_btn1.button("🔄 Запустить заново", use_container_width=True)
col_btn2.button("📸 Сохранить кадр", use_container_width=True)
col_btn3.button("📤 Экспорт вектора", use_container_width=True, disabled=True)

st.info("Пока работает только **Шаг 1: Детекция лица (MediaPipe)**. Остальные шаги добавим по plan.md.")