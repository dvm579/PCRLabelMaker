import os, sys, subprocess, platform
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pyqrcode
from printnodeapi import Gateway
import base64
import codes


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(144, 144))):
    # QR Code
    qrcode = pyqrcode.create(code_text)
    qrcode.png(resource_path(os.path.join('working', 'qr.png')), scale=3, quiet_zone=1)
    label_canvas.drawInlineImage(resource_path(os.path.join('working', 'qr.png')),
                                 32, 32, width=80, height=80, preserveAspectRatio=True)
    # Text
    print_text = code_text[:3] + '-' + code_text[3:7] + '-' + code_text[7:]
    pdfmetrics.registerFont(TTFont('barcodefont', resource_path(os.path.join('fonts', 'SplineSansMono-Medium.ttf'))))
    label_canvas.setFont('barcodefont', 15)
    label_canvas.drawCentredString(x=72, y=8, text=print_text)

    # Branding
    pdfmetrics.registerFont(TTFont('brandingfont', resource_path(os.path.join('fonts', 'Americane Bold.ttf'))))
    label_canvas.setFont('brandingfont', 15)
    label_canvas.drawCentredString(x=72, y=120, text="PRISM HEALTH LAB")

    # Save Page
    label_canvas.showPage()
    return label_canvas


def label_set(loc_id, qty):
    qty = int(qty)
    if loc_id == '':
        loc_id = '001'

    init_kit_num = codes.next_kit_num(codes.get_prev_kit_num(loc_id))
    kit_num = init_kit_num
    label_set_canvas = canvas.Canvas(resource_path(os.path.join('working', 'labels.pdf')), pagesize=(144, 144))
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


def print_pdf(filename):
    printnode = Gateway(apikey='_axRw1YfsMn7VJjm7no1PvO4sxXd-RQrFZG98cttpew')
    with open(resource_path(os.path.join('output', filename)), "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    encoded_string = base64.b64encode(pdf_bytes).decode('ascii')
    printjob = printnode.PrintJob(printer=70973429, title='PCR Labels', base64=encoded_string)
    os.remove(resource_path(os.path.join('output', filename)))
    print(printjob.id)


def execute(action):
    if action.upper() == 'S':
        show_pdf(label_file)
    elif action.upper() == 'P':
        print_pdf(label_file)
    else:
        action = input("""\nSorry, I didn't understand. Enter "S" to see the labels or "P" to print them to DYMO 1: """)
        execute(action)


if __name__ == '__main__':
    quantity = input("Qty: ")
    location = input("Location ID (leave blank for default): ")
    label_file = label_set(location, quantity)
    a = input("\nLabels Created.\n[S]how or [P]rint?")
    execute(a)


