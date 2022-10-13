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


def rapid_label(code_text: str, label_canvas=canvas.Canvas(resource_path('sample_label.pdf'), pagesize=(252, 81))):
    qr = pyqrcode.create(code_text)
    qr.png(resource_path('qr.png'), scale=3, quiet_zone=1)

    pdfmetrics.registerFont(TTFont('barcodefont', resource_path(os.path.join('fonts', 'SplineSansMono-Medium.ttf'))))
    pdfmetrics.registerFont(TTFont('brandingfont', resource_path(os.path.join('fonts', 'Americane Bold.ttf'))))

    label_canvas.drawInlineImage(resource_path('qr.png'), 5, 15, width=55, height=55, preserveAspectRatio=True)
    label_canvas.setFont('barcodefont', 8)
    label_canvas.drawRightString(60, 7, code_text)
    label_canvas.setFont('brandingfont', 6)
    label_canvas.drawRightString(236, 9, 'PHL Rapid Testing Services')

    label_canvas.setFont('brandingfont', 12)
    label_canvas.drawString(65, 55, 'Name: ______________________')
    label_canvas.drawString(65, 21, 'DOB: _____/_____/___________')

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
    printjob = printnode.PrintJob(printer=71644274, title='PCR Labels', base64=encoded_string)
    os.remove(resource_path(os.path.join('output', filename)))
    print(printjob.id)


def execute(action, label_format, label_file):
    if action.upper() == 'S':
        show_pdf(label_file)
    elif action.upper() == 'P':
        shape_key = {'S': '30332 Square', 'N': '30336 Small Multipurpose', 'R': '30252 Address'}
        input('\nPlease make sure your printer preferences are set properly for this paper.'
              '\nGo to Settings -> Bluetooth and Devices -> Printers -> DYMO LabelWriter 450 -> Printer Preferences '
              '-> Advanced'
              '\nUnder "Paper Size" select ' + shape_key[label_format] +
              '\nPress [Enter] to confirm the printer is ready.')
        print_pdf(label_file)
    else:
        action = input("""\nSorry, I didn't understand. Enter "S" to see the labels or "P" to print them to DYMO 1: """)
        execute(action, label_format, label_file)


def main():
    # Input
    form = input("Select one:\n\n[S]aliva Direct\n[N]asal Swab\n[R]apid Test\n\n").upper()
    quantity = int(input("Quantity: "))
    location = ''

    # Input Processing/Label Creation
    label_file = label_set(location, form, quantity)

    # Label Output Flow
    a = input("\nLabels Created.\n[S]how or [P]rint? ")
    execute(a, form, label_file)


if __name__ == '__main__':
    main()
