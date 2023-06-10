import av
import cv2
import numpy as np
import streamlit as st
from pathlib import Path
from typing import Literal
from streamlit_webrtc import (
    ClientSettings,
    VideoTransformerBase,
    WebRtcMode,
    webrtc_streamer,
)

# Import your video editing functions
from modules.Cartoon.main import cartoonify
from modules.SmoothSlider.main import half_slide
from modules.ThugLife.main import overlay_thuglife
from modules.TimeFreeze.main import time_freeze
from modules.ScanFreeze.main import line_freeze
from modules.HeartEyes.main import overlay_heart_eyes
from modules.Moustaches.main import overlay_moustache
from modules.BlurFaces.main import blur_all_faces
from modules.DevilFace.main import horns_nd_fangs_overlay
from helper.descriptor import filter_info
from helper.utils import file_checker

HERE = Path(__file__).parent
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False},
)

def video_filters(transform_type):
    """ Video transforms with OpenCV """

    file_checker_return = file_checker(transform_type)

    class OpenCVVideoTransformer(VideoTransformerBase):
        type: Literal[
            "Live Stream",
            "Cartoonie",
            "Half Slide - Horizontal",
            "Half Slide - Vertical",
            "Line Freeze - Horizontal",
            "Line Freeze - Vertical",
            "Thug Life",
            "Time Freeze - Ssim",
            "Time Freeze - Rcnn",
            "Heart Eyes",
            "Moustaches",
            "Face Blur",
            "Devil-ie"
        ]

        def __init__(self) -> None:
            self.type = "Live Stream"
            # Initialize any required variables for video editing
            # ...

        def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1)

            if self.type == "Live Stream":
                pass
            elif self.type == "Half Slide - Horizontal":
                # Call your half_slide function
                img = half_slide(img, self.last_frame, "horizontal")
                self.last_frame = img
            elif self.type == "Half Slide - Vertical":
                # Call your half_slide function
                img = half_slide(img, self.last_frame, "vertical")
                self.last_frame = img
            elif self.type == "Line Freeze - Horizontal":
                # Call your line_freeze function
                img = line_freeze(img, self.final_array, self.x, "horizontal")
                self.final_array = img
                self.x += 1
            elif self.type == "Line Freeze - Vertical":
                # Call your line_freeze function
                img = line_freeze(img, self.final_array, self.y, "vertical")
                self.final_array = img

            # Rest of the code for other transformations...

            return img

    filter_info(transform_type)

    if file_checker_return[0] == True:
        webrtc_ctx = webrtc_streamer(
            key="opencv-filter",
            mode=WebRtcMode.SENDRECV,
            client_settings=WEBRTC_CLIENT_SETTINGS,
            video_transformer_factory=OpenCVVideoTransformer,
            async_transform=True,
        )

        if webrtc_ctx.video_transformer:
            webrtc_ctx.video_transformer.type = transform_type

def main():
    transform_types = [
        "Live Stream",
        "Cartoonie",
        "Half Slide - Horizontal",
        "Half Slide - Vertical",
        "Line Freeze - Horizontal",
        "Line Freeze - Vertical",
        "Thug Life",
        "Time Freeze - Ssim",
        "Time Freeze - Rcnn",
        "Heart Eyes",
        "Moustaches",
        "Face Blur",
        "Devil-ie"
    ]

    st.title("Video Editor")

    selected_transform = st.selectbox("Video Transformations", transform_types)
    st.text("Selected Transformation: " + selected_transform)

    video_filters(selected_transform)

if __name__ == "__main__":
    main()
