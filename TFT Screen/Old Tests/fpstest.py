import cv2

cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("JPEG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 5)

frame = cap.read()
fps = int(cap.get(5))
print(fps)

