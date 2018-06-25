import pyqrcode
import qrtools

def create_qr_code_image(text, destination_file):
    url = pyqrcode.create(text)
    url.png(destination_file, scale=10)
    
 
def decode_qr_code_image(image_path):
    qr = qrtools.QR()
    success = qr.decode(image_path)
    return success, qr.data