import cv2


def takeImage():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")
    while True:
        ret, frame = cam.read()
        cv2.imshow("test", frame)
        k = cv2.waitKey(1)
        if k % 256 == 32:
            # SPACE pressed
            cv2.imwrite("img.jpg", frame)
            break
    cam.release()
    cv2.destroyAllWindows()
