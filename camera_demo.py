import tkinter as tk
from tkinter import ttk
from pypylon import pylon
import cv2
from PIL import Image, ImageTk
import threading


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basler Camera Demo")
        self.running = True

        # ---------------------------------------------------------- #
        #                         Camera setup                       #
        # ---------------------------------------------------------- #

        info = pylon.DeviceInfo()
        info.SetDeviceClass("BaslerUsb")
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice(info)
        )
        self.camera.Open()
        self.camera.AcquisitionMode.Value = "Continuous"
        self.camera.ExposureAuto.Value = "Off"
        self.camera.ExposureTime.Value = 30000
        self.camera.GainAuto.Value = "Off"
        self.camera.Gain.Value = 20
        self.camera.AcquisitionFrameRateEnable.SetValue(True)
        self.camera.AcquisitionFrameRate.SetValue(30.0)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        self.update_thread = threading.Thread(target=self.updateFrame, daemon=True)
        self.update_thread.start()

        # ---------------------------------------------------------- #
        #                          UI setup                          #
        # ---------------------------------------------------------- #

        self.videoLabel = ttk.Label(root)
        self.videoLabel.pack()

        # control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # FPS controls
        tk.Label(control_frame, text="FPS").grid(row=0, column=0, padx=5)
        self.fps_slider = tk.Scale(
            control_frame,
            from_=1,
            to=60,
            resolution=1,
            orient="horizontal",
            length=200,
            command=self.updateFPS,
        )
        self.fps_slider.set(30)
        self.fps_slider.grid(row=0, column=1)

        self.fpsValueLabel = tk.Label(control_frame, text="30")
        self.fpsValueLabel.grid(row=0, column=2, padx=5)

        # gain controls
        tk.Label(control_frame, text="Gain").grid(row=1, column=0, padx=5)
        max_gain = self.camera.Gain.GetMax()
        self.gain_slider = tk.Scale(
            control_frame,
            from_=0,
            to=max_gain,
            resolution=0.1,
            orient="horizontal",
            length=200,
            command=self.updateGain,
        )
        self.gain_slider.set(20)
        self.gain_slider.grid(row=1, column=1)

        self.gainValueLabel = tk.Label(control_frame, text="20.00")
        self.gainValueLabel.grid(row=1, column=2, padx=5)

        # quit button
        self.quitButton = ttk.Button(root, text="Quit", command=self.quit)
        self.quitButton.pack(pady=10)

        # ---------------------------------------------------------- #
        #                       Helper functions                     #
        # ---------------------------------------------------------- #

    def updateFPS(self, val):
        try:
            fps_val = float(val)
            max_fps = self.camera.ResultingFrameRate.GetMax()
            fps_val = min(fps_val, max_fps)

            self.camera.AcquisitionFrameRate.SetValue(fps_val)
            self.fpsValueLabel.config(text=f"{int(fps_val)}")
        except Exception as e:
            print("FPS error:", e)

    def updateGain(self, val):
        try:
            gain_val = float(val)
            max_gain = self.camera.Gain.GetMax()
            gain_val = min(gain_val, max_gain)

            self.camera.Gain.SetValue(gain_val)
            self.gainValueLabel.config(text=f"{gain_val:.2f}")
        except Exception as e:
            print("Gain error:", e)

    def updateFrame(self):
        while self.running and self.camera.IsGrabbing():
            try:
                grab = self.camera.RetrieveResult(
                    5000, pylon.TimeoutHandling_ThrowException
                )
                if grab.GrabSucceeded():
                    image = self.converter.Convert(grab)
                    frame = image.GetArray()

                    resized = cv2.resize(frame, (1280, 720))
                    finalImage = Image.fromarray(
                        cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                    )
                    imageDisplay = ImageTk.PhotoImage(image=finalImage)

                    self.videoLabel.configure(image=imageDisplay)
                    self.videoLabel.image = imageDisplay
                grab.Release()
            except Exception as e:
                print("Frame grab error:", e)

    def quit(self):
        self.running = False

        if self.camera.IsGrabbing():
            try:
                self.camera.CancelGrab()
                self.camera.StopGrabbing()
            except Exception as e:
                print("Stop error:", e)

        try:
            self.camera.Close()
        except Exception as e:
            print("Close error:", e)

        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
