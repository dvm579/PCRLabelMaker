import os, sys, subprocess, platform
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pyqrcode
import codes


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(96, 96))):
    # QR Code
    qrcode = pyqrcode.create(code_text)
    qrcode.png(resource_path(os.path.join('working', 'qr.png')), scale=3, quiet_zone=1)
    label_canvas.drawInlineImage(resource_path(os.path.join('working', 'qr.png')),
                                 20.5, 19.5, width=55, height=55, preserveAspectRatio=True)
    # Text
    print_text = code_text[:3] + '-' + code_text[3:7] + '-' + code_text[7:]
    pdfmetrics.registerFont(TTFont('barcodefont', resource_path(os.path.join('fonts', 'SplineSansMono-Medium.ttf'))))
    label_canvas.setFont('barcodefont', 9)
    label_canvas.drawCentredString(x=48, y=8, text=print_text)

    # Branding
    pdfmetrics.registerFont(TTFont('brandingfont', resource_path(os.path.join('fonts', 'Americane Bold.ttf'))))
    label_canvas.setFont('brandingfont', 9)
    label_canvas.drawCentredString(x=48, y=80, text="PRISM HEALTH LAB")

    # Save Page
    label_canvas.showPage()
    return label_canvas


def label_set(loc_id, qty):
    qty = int(qty)
    if loc_id == '':
        loc_id = '001'

    init_kit_num = codes.next_kit_num(codes.get_prev_kit_num(loc_id))
    kit_num = init_kit_num
    label_set_canvas = canvas.Canvas(resource_path(os.path.join('working', 'labels.pdf')), pagesize=(96, 96))
    for i in range(qty):
        label(codes.make_barcode(loc_id=loc_id, kit_num=kit_num), label_canvas=label_set_canvas)
        if i + 1 != qty:
            kit_num = codes.next_kit_num(kit_num)
    label_set_canvas.save()
    codes.update_db(loc_id=loc_id, new_kit_num=kit_num)

    filename = loc_id + '_' + init_kit_num + '-' + kit_num + '.pdf'
    os.rename(resource_path(os.path.join('working', 'labels.pdf')),
              resource_path(os.path.join('output', filename)))
    os.remove(resource_path(os.path.join('working', 'qr.png')))
    return filename


def show_pdf(filename):
    filepath = resource_path(os.path.join('output', filename))
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


if __name__ == '__main__':
    quantity = input("Qty: ")
    location = input("Location ID (leave blank for default): ")
    label_file = label_set(location, quantity)
    show_pdf(label_file)
