import wx
import os

import minecraft_launcher_lib as mc
from game import run_game

documents = os.path.expanduser("~/Documents/")
mcc_dir = documents + "MCC/"

minecraft_directory = mc.utils.get_minecraft_directory()

if not os.path.isdir(minecraft_directory):
    os.mkdir(minecraft_directory)
pass_path = minecraft_directory + "/temp.txt"


class LoginFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.panel = wx.Panel(self)
        self.email_label = wx.StaticText(self.panel, label="Email:")
        self.email_input = wx.TextCtrl(self.panel, size=(140, -1))

        temp_email_use = ""
        if os.path.isfile(mcc_dir + "username.txt"):
            f = open(mcc_dir + "username.txt", "r")
            temp_email_use = f.read()
            f.close()

        self.email_input.SetValue(temp_email_use)

        self.password_label = wx.StaticText(self.panel, label="Password:")
        self.password_input = wx.TextCtrl(self.panel, size=(140, -1), style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)

        temp_pass_use = ""
        if os.path.isfile(pass_path):
            f = open(pass_path, "r")
            temp_pass_use = f.read()
            f.close()

        self.password_input.SetValue(temp_pass_use)

        self.check_box = wx.CheckBox(self.panel, style=wx.ALIGN_LEFT, label="Keep me logged in")
        if os.path.isfile(pass_path):
            self.check_box.SetValue(True)

        self.quit_button = wx.Button(self.panel, label="Quit")
        self.button = wx.Button(self.panel, label="Login")

        # Set sizer for the frame, so we can change frame size to match widgets
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.LEFT)

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.email_label, (0, 0))
        self.sizer.Add(self.email_input, (0, 1))
        self.sizer.Add(self.password_label, (1, 0))
        self.sizer.Add(self.password_input, (1, 1))
        self.sizer.Add(self.check_box, (2, 1))
        self.sizer.Add(self.button, (3, 1), (1, 1), flag=wx.EXPAND)
        self.sizer.Add(self.quit_button, (3, 0), (1, 1), flag=wx.EXPAND)
        #self.sizer.Add(self.button, (2, 0), (1, 2), flag=wx.EXPAND)

        # Set simple sizer for a nice border
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        # Use the sizers
        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.password_input.Bind(wx.EVT_TEXT_ENTER, self.OnLogin)
        self.button.Bind(wx.EVT_BUTTON, self.OnLogin)
        self.quit_button.Bind(wx.EVT_BUTTON, self.OnQuit)

        self.Centre()

    def OnLogin(self, e):
        login = mc.account.login_user(self.email_input.GetValue(), self.password_input.GetValue())

        if os.path.isfile(mcc_dir + "username.txt"):
            os.remove(mcc_dir + "username.txt")
        f = open(mcc_dir + "username.txt", "a")
        f.write(self.email_input.GetValue())
        f.close()

        if "error" in login:
            # Dialogue
            dlg = wx.MessageDialog(None, "Login Incorrect")
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.Hide()
            if self.check_box.GetValue():
                if os.path.isfile(pass_path):
                    os.remove(pass_path)
                f = open(pass_path, "a")
                f.write(self.password_input.GetValue())
                f.close()
            else:
                if os.path.isfile(pass_path):
                    os.remove(pass_path)
            if(not run_game(login)):
                self.Destroy()
        self.Destroy()

    def OnQuit(self, e):
        self.Destroy()

app = wx.App(False)

if not os.path.isdir(mcc_dir):
    os.mkdir(mcc_dir)

frame = LoginFrame(None)
frame.Show()
app.MainLoop()
