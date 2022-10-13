import os, subprocess, platform
from printnodeapi import Gateway
import base64
from label import resource_path, label_set


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