import os
import datetime
import shutil

def parse_whatsapp_name(filename):
    filename, ext = os.path.splitext(filename)
    filetype, date, progressive = os.path.basename(filename).split("-")
    progressive = "00"+progressive[2:]

    if filetype.lower() == "img":
        filetype = "P"
    else:
        filetype = "V"
    return f"{filetype}_{date[:4]}_{date[4:6]}_{date[6:8]}_{progressive}{ext}"


def filename_from_last_modify(filename):
    _, ext = os.path.splitext(filename)
    if ext[1:] == "jpg":
        filetype = "P"
    else:
        filetype = "V"
    t = os.path.getmtime(filename)
    mod = datetime.datetime.fromtimestamp(t)
    return f"{filetype}_{mod.year}_{mod.month}_{mod.day}_{mod.hour}{mod.minute}{mod.second}{ext}"


myp = "C:\\backupcell\\mem\\DCIM\\P_20160721_095724.jpg"
print(filename_from_last_modify(myp))

myp = "C:\\backupcell\\mem\\DCIM\\V_20201110_174829.mp4"
print(filename_from_last_modify(myp))

myp = "C:\\backupcell\\mem\\WhatsAppImages\\IMG-20150112-WA0000.jpg"
print(parse_whatsapp_name(myp))

myp = "C:\\backupcell\\mem\\WhatsAppVideo\\VID-20170110-WA0002.mp4"
print(parse_whatsapp_name(myp))

src = "D:\\prova.txt"
dst = "D:\\prova_rinominato.txt"
shutil.move(src,dst)
