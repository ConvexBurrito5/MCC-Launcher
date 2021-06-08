import os
import time
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

import minecraft_launcher_lib as mc
import py7zr
import wx

documents = os.path.expanduser("~/Documents/")
mcc_dir = documents + "MCC/"
work_dir = mcc_dir + "work/"
backup_dir = mcc_dir + "backup/"

backups = ["resourcepacks", "screenshots", "saves", "options.txt"]

url = 'https://adomainhopefullynobodyhas.wordpress.com/'
response = urllib.request.urlopen(url)
webContent = str(response.read())
startpos = webContent.find("VERS:")
endpos = webContent.find("EEEEE")
subStr = webContent[startpos:endpos]

temp_words = subStr.split()

version = (temp_words[0])[5:]
loader_version = (temp_words[1])[17:]
current_dl = (temp_words[2])[21:]
java_location = (temp_words[3])[5:]

java_location = java_location.replace("^", " ")
java_location = java_location.replace("/", "\\")

upd_num = (temp_words[4])[7:]

minecraft_directory = mc.utils.get_minecraft_directory()


def Backup():
    if os.path.isdir(backup_dir):
        shutil.rmtree(backup_dir)
        os.mkdir(backup_dir)
    else:
        os.mkdir(backup_dir)

    for i in backups:
        if os.path.isfile(work_dir + '/' + i) or os.path.isdir(work_dir + '/' + i):
            shutil.move(work_dir + '/' + i, backup_dir + '/' + i)


def RestoreBackup():
    for i in backups:
        if os.path.isdir(backup_dir + '/' + i) or os.path.isfile(backup_dir + '/' + i):
            shutil.move(backup_dir + '/' + i, work_dir + '/' + i)


attempts = 0


def Update(up_url):
    global attempts
    dlg = wx.MessageDialog(None, "Downloading Updates, this might take a while")
    dlg.ShowModal()
    dlg.Destroy()
    Backup()
    if os.path.isdir(work_dir):
        try:
            shutil.rmtree(work_dir)
        except:
            dlg = wx.MessageDialog(None, "Error has occurred, restart your computer and it will be resolved")
            dlg.ShowModal()
            dlg.Destroy()
            return False
    up_url = "http://www." + up_url
    temp_path_7z = mcc_dir + "temp.7z"
    temp_path = mcc_dir + "temp"
    urllib.request.urlretrieve(up_url, temp_path_7z)
    archive = py7zr.SevenZipFile(temp_path_7z, mode='r')
    archive.extractall(path=temp_path)
    archive.close()
    shutil.move(temp_path + "/work", work_dir)
    os.remove(temp_path_7z)
    os.rmdir(temp_path)
    RestoreBackup()
    return True


def install_fabric():
    global version
    if not os.path.isfile(minecraft_directory + "/launcher_profiles.json"):
        dlg = wx.MessageDialog(None, "You need to run the regular launcher at least once")
        dlg.ShowModal()
        dlg.Destroy()
        return False
    if os.path.isdir(minecraft_directory + "/versions/fabric-loader-" + loader_version + "-" + version):
        return True
    latest_installer_version = mc.fabric.get_latest_installer_version()
    dl_url = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/" + latest_installer_version + "/fabric-installer-" + latest_installer_version + ".jar"
    urllib.request.urlretrieve(dl_url, mcc_dir + "fabric.jar")
    print("\"" + java_location + "\"" + " -jar " + mcc_dir + "fabric.jar client -dir " + minecraft_directory + " -mcversion " + version)
    os.system("\"" + java_location + "\"" + " -jar " + mcc_dir + "fabric.jar client -dir " + minecraft_directory + " -mcversion " + version)
    dlg = wx.MessageDialog(None, "You need to run Fabric " + version + " at least once in the regular launcher")
    dlg.ShowModal()
    dlg.Destroy()
    return False
    pass


def run_game(login):
    os.chdir(mcc_dir)
    if not install_fabric():
        return False

    if os.path.isfile(mcc_dir + "update.txt"):
        f = open(mcc_dir + "update.txt", "r")
        old = f.read()
        f.close()
        if old != current_dl:
            Update(current_dl)
        os.remove(mcc_dir + "update.txt")
        f = open(mcc_dir + "update.txt", "a")
        f.write(current_dl)
        f.close()
    else:
        Update(current_dl)
        f = open(mcc_dir + "update.txt", "a")
        f.write(current_dl)
        f.close()

    options = {
        "username": login["selectedProfile"]["name"],
        "uuid": login["selectedProfile"]["id"],
        "token": login["accessToken"],
        "executablePath": java_location,  # The path to the java executable
        "gameDirectory": work_dir,
        "customResolution": True,
        "resolutionWidth": "1280",
        "resolutionHeight": "720"
    }
    try:
        minecraft_command = mc.command.get_minecraft_command("fabric-loader-" + loader_version + "-" + version, minecraft_directory, options)
        start_time = time.time()
        subprocess.call(minecraft_command)
        end_time = time.time()

        if end_time - start_time < 5:
            dlg = wx.MessageDialog(None, "You need to run Fabric " + version + " at least once in the regular launcher")
            dlg.ShowModal()
            dlg.Destroy()
    except:
        dlg = wx.MessageDialog(None, "You need to run Fabric " + version + " at least once in the regular launcher")
        dlg.ShowModal()
        dlg.Destroy()

    return True
