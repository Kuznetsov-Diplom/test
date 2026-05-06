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
    # Правильный вызов без 'name' (пока библиотека так работает)
    detector = MediaPipeFaceDetector(min_detection_confidence=0.85)
    pipeline.add_step(detector)
    st.session_state.pipeline = pipeline

pipeline = st.session_state.pipeline

# Боковая панель
st.sidebar.header("🔧 Пайплайн")
step_names = [step.name for step in pipeline.steps]
current_step_name = st.sidebar.selectbox("Текущий шаг", step_names, index=0)

# Параметры шага
if current_step_name == "unnamed_step":  # пока имя по умолчанию
    conf = st.sidebar.slider("min_detection_confidence", 0.5, 1.0, 0.85, 0.05)
    pipeline.update_step_params(current_step_name, min_detection_confidence=conf)

# Основной экран
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📹 Серверная камера — Live (реальное время)")
    ctx = webrtc_streamer(
        key="biometric",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        video_frame_callback=None,  # обработка вручную ниже
    )

with col2:
    st.subheader("📊 Статус пайплайна")
    if ctx.video_frame:
        frame = ctx.video_frame.to_ndarray(format="bgr24")
        context = pipeline.process_single_frame(frame)

        # Оверлей
        overlay = pipeline.get_overlay_frame(context)
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
        st.image(overlay_rgb, channels="RGB", use_column_width=True)

        # Метрики (пока частично заполняются)
        st.metric("Face detected • Confidence", f"{context.confidence:.2f}")
        st.metric("ROI", f"{context.roi_size[0]}×{context.roi_size[1]} px")
        if context.inter_pupil_distance > 0:
            st.metric("Межзрачковое расстояние", f"{context.inter_pupil_distance:.0f} px")
        st.metric("Стабилизация", f"{context.stabilization:.0f}%")
        st.progress(context.confidence)
        st.caption(f"Шаг: {context.current_step} | FPS ≈ 30")
    else:
        st.info("Подключи камеру ↑")

# Кнопки
col_btn1, col_btn2, col_btn3 = st.columns(3)
col_btn1.button("🔄 Запустить заново", use_container_width=True)
col_btn2.button("📸 Сохранить кадр", use_container_width=True)
col_btn3.button("📤 Экспорт вектора", use_container_width=True, disabled=True)
 
st.info("Пока работает только **Шаг 1: Детекция лица (MediaPipe)**. Остальные шаги добавим по plan.md.")