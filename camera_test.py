from pypylon import pylon
import cv2

# --------------------------------------------------------------------------------------- #
#                                   Initialize camera                                     #
# --------------------------------------------------------------------------------------- #
info = pylon.DeviceInfo()
info.SetDeviceClass("BaslerUsb")

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
camera.Open()
camera.AcquisitionMode.Value = "Continuous"

try:
    node = camera.GetNodeMap().GetNode("AcquisitionFrameRateEnable")
    if node and pylon.IsWritable(node):
        node.Value = True
        camera.AcquisitionFrameRate.Value = 30.0
except:
    pass

# --------------------------------------------------------------------------------------- #
#                                   Camera parameters                                     #
# --------------------------------------------------------------------------------------- #

camera.ExposureAuto.Value = "Off"
camera.ExposureTime.Value = 30000.0
camera.GainAuto.Value = "Off"
camera.Gain.Value = 20.0

# --------------------------------------------------------------------------------------- #
#                                      Camera capture                                     #
# --------------------------------------------------------------------------------------- #

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# convert captured image for cv display (Mono8 -> RGB)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_RGB8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

print("Press any button to close the program")
cv2.namedWindow("Basler Continuos Preview", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Basler Continuos Preview", 1200, 800)

while camera.IsGrabbing():
    grab = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab.GrabSucceeded():
        image = converter.Convert(grab)
        final_image = image.GetArray()

        cv2.imshow("Basler Continuos Preview", final_image)

        key = cv2.waitKey(1) & 0xFF

        if key != 255:
            break

    grab.Release()

# --------------------------------------------------------------------------------------- #
#                                       Stop camera                                       #
# --------------------------------------------------------------------------------------- #

camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
