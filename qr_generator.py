# qr_generator.py
import qrcode
import os
import json
import time

def generate_qr_for_data(data_dict, filename=None, save_path="assets/"):
    """
    Generate QR image containing JSON of data_dict.
    Returns path to saved image.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    payload = json.dumps(data_dict, ensure_ascii=False)
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    if filename is None:
        fname = f"qr_{int(time.time())}.png"
    else:
        fname = filename if filename.endswith(".png") else f"{filename}.png"

    fullpath = os.path.join(save_path, fname)
    img.save(fullpath)
    return fullpath
