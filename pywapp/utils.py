import qrcode
from PIL import Image
from threading import Thread, Event

def generateQR(text):
    qr = qrcode.QRCode(version=3, box_size=20, border=10, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.png")
    showImage(path='qrcode.png')

def showImage(path):
    img = Image.open(path)
    img.show()

class MyThread(Thread):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self) -> None:
        self._stop_event.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()