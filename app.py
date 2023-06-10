import streamlit as st
from pathlib import Path
from streamlit_webrtc import (
    ClientSettings,
    VideoTransformerBase,
    WebRtcMode,
    webrtc_streamer,
)

HERE = Path(__file__).parent
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False},
)

def live_mode():
    """Simple video loopback"""
    webrtc_streamer(
        key="loopback",
        mode=WebRtcMode.SENDRECV,
        client_settings=WEBRTC_CLIENT_SETTINGS,
        video_transformer_factory=None,  # NoOp
    )

def video_filters(transform_type):
    """Video transforms with OpenCV"""
    class OpenCVVideoTransformer(VideoTransformerBase):
        type: Literal["Live Stream", "Half Slide - Horizontal", "Half Slide - Vertical",
                       "Line Freeze - Horizontal", "Line Freeze - Vertical",
                       "Thug Life", "Time Freeze - Ssim", "Time Freeze - Rcnn",
                       "Heart Eyes", "Moustaches", "Face Blur", "Devil-ie"]

        def __init__(self) -> None:
            self.type = "Live Stream"
            self.first_frame = False
            self.last_frame = None
            self.stitched_img = None
            self.prev_num = 1
            self.first_snap = False
            self.init_frame = False
            self.bg = None
            self.x = 0
            self.y = 0

        def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1)

            if self.type == "Live Stream":
                pass

            elif self.type == "Half Slide - Horizontal":
                if self.first_frame == False:
                    self.first_frame = True
                else:
                    img = half_slide(img, self.last_frame, "horizontal")
                self.last_frame = img

            elif self.type == "Half Slide - Vertical":
                if self.first_frame == False:
                    self.first_frame = True
                else:
                    img = half_slide(img, self.last_frame, "vertical")
                self.last_frame = img

            elif self.type == "Line Freeze - Horizontal":
                if self.x == 0:
                    self.final_array = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
                elif self.x >= img.shape[1]:
                    self.x = 0
                    time.sleep(2)
                else:
                    img = line_freeze(img, self.final_array, self.x, "horizontal")
                    self.final_array = img
                self.x += 1

            elif self.type == "Line Freeze - Vertical":
                if self.y == 0:
                    self.final_array = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
                elif self.y >= img.shape[0]:
                    self.y = 0
                    time.sleep(2)
                else:
                    img = line_freeze(img, self.final_array, self.y, "vertical")
                    self.final_array = img
                self.y += 1

            elif self.type == "Thug Life":
                img = overlay_thuglife(img, file_checker_return[1])[0]

            elif self.type == "Time Freeze - Ssim":
                if self.init_frame == False:
                    self.start_time = time.time()
                out_params = time_freeze(img, self.bg, [self.stitched_img, self.prev_num, self.first_snap,
                                                         self.init_frame, self.start_time], "ssim")
                img, self.stitched_img, self.bg, self.prev_num, self.first_snap, self.init_frame = out_params

            elif self.type == "Time Freeze - Rcnn":
                if self.init_frame == False:
                    self.start_time = time.time()
                out_params = time_freeze(img, self.bg, [self.stitched_img, self.prev_num, self.first_snap,
                                                         self.init_frame, self.start_time], "rcnn")
                img, self.stitched_img, self.bg, self.prev_num, self.first_snap, self.init_frame = out_params

            elif self.type == "Heart Eyes":
                img = overlay_heart_eyes(img, file_checker_return[1])[0]

            elif self.type == "Moustaches":
                img = overlay_moustache(img, file_checker_return[1], 1)[0]

            elif self.type == "Face Blur":
                img = blur_all_faces(img, file_checker_return[1])[0]

            elif self.type == "Devil-ie":
                img = horns_nd_fangs_overlay(img, file_checker_return[1])[0]

            return img

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
    st.title("Video Editing")

    # Video Editing Section
    st.header("Video Editing")
    transform_type = st.selectbox("Select a video filter:", ["Live Stream", "Half Slide - Horizontal",
                                                              "Half Slide - Vertical", "Line Freeze - Horizontal",
                                                              "Line Freeze - Vertical", "Thug Life",
                                                              "Time Freeze - Ssim", "Time Freeze - Rcnn",
                                                              "Heart Eyes", "Moustaches", "Face Blur", "Devil-ie"])

    video_filters(transform_type)

if __name__ == "__main__":
    main()
