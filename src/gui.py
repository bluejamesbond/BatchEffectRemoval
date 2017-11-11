import wx

def prompt(message='', default='', title=''):
    app = wx.App()
    dlg = wx.TextEntryDialog(None, message, value=default, caption=title)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    app.Destroy()
    return result


def confirm(message, title=''):
    app = wx.App()
    dlg = wx.MessageDialog(None, message, title, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    app.Destroy()
    return result

def alert(message, title=''):
    app = wx.App()
    dlg = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    app.Destroy()

def openFile(message, wildcard="*"):
    app = wx.App()
    with wx.FileDialog(None, message, wildcard=wildcard,
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        app.Destroy()

        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return  # the user changed their mind

        # Proceed loading the file chosen by the user
        return fileDialog.GetPath()

def saveFile(message, wildcard="*"):
    app = wx.App()
    with wx.FileDialog(None, message, wildcard=wildcard,
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
        app.Destroy()
        
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return  # the user changed their mind

        # Proceed loading the file chosen by the user
        return fileDialog.GetPath()
