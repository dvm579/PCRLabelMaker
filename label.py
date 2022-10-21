import os, sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pyqrcode
import codes


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def rapid_label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(252, 81))):
    qr = pyqrcode.create(code_text)
    qr.png(resource_path(os.path.join('working', 'qr.png')), scale=3, quiet_zone=1)

    pdfmetrics.registerFont(TTFont('barcodefont', resource_path(os.path.join('fonts', 'SplineSansMono-Medium.ttf'))))
    pdfmetrics.registerFont(TTFont('brandingfont', resource_path(os.path.join('fonts', 'Americane Bold.ttf'))))

    label_canvas.drawInlineImage(resource_path(os.path.join('working', 'qr.png')), 5, 15,
                                 width=55, height=55, preserveAspectRatio=True)
    label_canvas.setFont('barcodefont', 8)
    label_canvas.drawRightString(60, 7, code_text)
    label_canvas.setFont('brandingfont', 6)
    label_canvas.drawRightString(236, 9, 'PHL Rapid Testing Services')

    label_canvas.setFont('brandingfont', 12)
    label_canvas.drawString(65, 55, 'Name: _____________________________')
    label_canvas.drawString(65, 21, 'D O B  : _______/_______/_____________')

    label_canvas.showPage()
    return label_canvas


def saliva_label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(144, 144))):
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


def nasal_label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(306, 144))):
    # QR Code
    qrcode = pyqrcode.create(code_text)
    qrcode.png(resource_path(os.path.join('working', 'qr.png')), scale=3, quiet_zone=1)
    label_canvas.drawInlineImage(resource_path(os.path.join('working', 'qr.png')),
                                 15, 38, width=80, height=80, preserveAspectRatio=True)

    # Code Text
    print_text = code_text[:3] + '-' + code_text[3:7] + '-' + code_text[7:]
    pdfmetrics.registerFont(TTFont('barcodefont', resource_path(os.path.join('fonts', 'SplineSansMono-Medium.ttf'))))
    label_canvas.setFont('barcodefont', 9)
    label_canvas.drawCentredString(x=55, y=26, text=print_text)

    # Branding
    pdfmetrics.registerFont(TTFont('brandingfont', resource_path(os.path.join('fonts', 'Americane Bold.ttf'))))
    label_canvas.setFont('brandingfont', 9)
    label_canvas.drawCentredString(x=55, y=121, text="PRISM HEALTH LAB")
    
    # Written Patient Info Fields
    label_canvas.drawRightString(x=296, y=115, text='______________________________________________________')
    label_canvas.drawRightString(x=296, y=105, text='First Name')
    label_canvas.drawRightString(x=296, y=70, text='______________________________________________________')
    label_canvas.drawRightString(x=296, y=60, text='Last Name')
    label_canvas.drawRightString(x=296, y=25, text='______________________________________________________')
    label_canvas.drawRightString(x=296, y=15, text='Date of Birth')
    label_canvas.setFont('brandingfont', 15)
    label_canvas.drawString(x=155, y=25.5, text='/')
    label_canvas.drawString(x=210, y=25.5, text='/')

    # Save Page
    label_canvas.showPage()
    return label_canvas


def label_set(loc_id: str, fmt: str, qty: int):
    if fmt == 'S':
        label_set_canvas = canvas.Canvas(resource_path(os.path.join('working', 'labels.pdf')), pagesize=(144, 144))
        if loc_id == '':
            loc_id = '001'
    elif fmt == 'N':
        label_set_canvas = canvas.Canvas(resource_path(os.path.join('working', 'labels.pdf')), pagesize=(306, 144))
        if loc_id == '':
            loc_id = '002'
    elif fmt == 'R':
        label_set_canvas = canvas.Canvas(resource_path(os.path.join('working', 'labels.pdf')), pagesize=(252, 81))
        if loc_id == '':
            loc_id = 'RT'
    else:
        raise TypeError('Only "S", "N", and "R" allowed for format values')

    init_kit_num = codes.next_kit_num(codes.get_prev_kit_num(loc_id))
    kit_num = init_kit_num
    for i in range(qty):
        if fmt == 'S':
            saliva_label(codes.make_barcode(loc_id=loc_id, kit_num=kit_num), label_canvas=label_set_canvas)
        elif fmt == 'N':
            nasal_label(codes.make_barcode(loc_id=loc_id, kit_num=kit_num), label_canvas=label_set_canvas)
        elif fmt == 'R':
            rapid_label(codes.make_barcode(loc_id=loc_id, kit_num=kit_num), label_canvas=label_set_canvas)
        else:
            raise TypeError('Only "S", "N", and "R" allowed for format values')
        if i + 1 != qty:
            kit_num = codes.next_kit_num(kit_num)
    label_set_canvas.save()
    codes.update_db(loc_id=loc_id, new_kit_num=kit_num)

    filename = loc_id + '_' + init_kit_num + '-' + kit_num + '.pdf'
    os.rename(resource_path(os.path.join('working', 'labels.pdf')),
              resource_path(os.path.join('output', filename)))
    os.remove(resource_path(os.path.join('working', 'qr.png')))
    return filename
