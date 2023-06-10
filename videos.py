import av
import cv2
import numpy as np
import streamlit as st
from pathlib import Path
from streamlit_webrtc import (
    ClientSettings,
    VideoTransformerBase,
    WebRtcMode
)

HERE = Path(__file__).parent
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False},
)

class VideoRecorder:
    def __init__(self):
        self.frames = []
        self.recording = False

    def add_frame(self, frame):
        if self.recording:
            self.frames.append(frame)
            if len(self.frames) > 10 * 30:  # Maximum recording length: 10 seconds
                self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.frames = []

    def stop_recording(self):
        self.recording = False

    def get_recorded_video(self):
        return self.frames

class OpenCVVideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.recorder = VideoRecorder()

    def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        self.recorder.add_frame(img)

        return img

def main():
    st.title("Video Editor")

    recorder = VideoRecorder()
    transformer = OpenCVVideoTransformer()

    if st.button("Start"):
        recorder.start_recording()

    if st.button("Stop"):
        recorder.stop_recording()
        recorded_video = recorder.get_recorded_video()

        if recorded_video:
            st.video(np.array(recorded_video))
        else:
            st.warning("No video recorded.")

    webrtc_ctx = st.webrtc_streamer(
        key="opencv-filter",
        mode=WebRtcMode.SENDRECV,
        client_settings=WEBRTC_CLIENT_SETTINGS,
        video_transformer_factory=transformer,
        async_transform=True,
    )

if __name__ == "__main__":
    main()
