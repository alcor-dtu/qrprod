import pyqrcode

def create_qr_code_image(text, destination_file):
    url = pyqrcode.create(text)
    url.png(destination_file, scale=10)