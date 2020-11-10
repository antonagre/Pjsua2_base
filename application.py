import sys
if sys.version_info[0] >= 3: # Python 3
    from tkinter import ttk
else:
    import ttk
import pjsua2 as pj
import account
import endpoint
import settings
import os
import traceback

# You may try to enable pjsua worker thread by setting USE_THREADS below to True *and*
# recreate the swig module with adding -threads option to swig (uncomment USE_THREADS 
# in swig/python/Makefile). In my experiment this would crash Python as reported in:
# http://lists.pjsip.org/pipermail/pjsip_lists.pjsip.org/2014-March/017223.html
USE_THREADS = False

write=sys.stdout.write

class Application(ttk.Frame):
    """
    The Application main frame.
    """
    def __init__(self):
        global USE_THREADS
        ttk.Frame.__init__(self, name='application', width=300, height=500)
        self.pack(expand='yes', fill='both')
        self.master.title('pjsua2 Demo')
        self.master.geometry('500x500+100+100')

        # Accounts
        self.accList = []

        self.quitting = False

        # Construct GUI
        self.initGui()

        # Instantiate endpoint
        self.ep = endpoint.Endpoint()
        self.ep.libCreate()

        # Default config
        self.appConfig = settings.AppConfig()
        if USE_THREADS:
            self.appConfig.epConfig.uaConfig.threadCnt = 1
            self.appConfig.epConfig.uaConfig.mainThreadOnly = False
        else:
            self.appConfig.epConfig.uaConfig.threadCnt = 0
            self.appConfig.epConfig.uaConfig.mainThreadOnly = True

    def saveConfig(self, filename='pygui.json'):
        # Save disabled accounts since they are not listed in self.accList
        disabled_accs = [ac for ac in self.appConfig.accounts if not ac.enabled]
        self.appConfig.accounts = []

        # Get account configs from active accounts
        for acc in self.accList:
            acfg = settings.AccConfig()
            acfg.enabled = True
            acfg.config = acc.cfg
            self.appConfig.accounts.append(acfg)

        # Put back disabled accounts
        self.appConfig.accounts.extend(disabled_accs)
        # Save
        self.appConfig.saveFile(filename)

    def start(self, cfg_file='pygui.json'):
        global USE_THREADS
        # Load config
        if cfg_file and os.path.exists(cfg_file):
            self.appConfig.loadFile(cfg_file)

        if USE_THREADS:
            self.appConfig.epConfig.uaConfig.threadCnt = 1
            self.appConfig.epConfig.uaConfig.mainThreadOnly = False
        else:
            self.appConfig.epConfig.uaConfig.threadCnt = 0
            self.appConfig.epConfig.uaConfig.mainThreadOnly = True
        self.appConfig.epConfig.uaConfig.threadCnt = 0
        self.appConfig.epConfig.uaConfig.mainThreadOnly = True

        # Initialize library
        self.appConfig.epConfig.uaConfig.userAgent = "pygui-" + self.ep.libVersion().full;
        self.ep.libInit(self.appConfig.epConfig)
        self.master.title('pjsua2 Demo version ' + self.ep.libVersion().full)

        # Create transports
        if self.appConfig.udp.enabled:
            self.ep.transportCreate(self.appConfig.udp.type, self.appConfig.udp.config)
        if self.appConfig.tcp.enabled:
            self.ep.transportCreate(self.appConfig.tcp.type, self.appConfig.tcp.config)
        if self.appConfig.tls.enabled:
            self.ep.transportCreate(self.appConfig.tls.type, self.appConfig.tls.config)

        # Add accounts
        for cfg in self.appConfig.accounts:
            if cfg.enabled:
                self._createAcc(cfg.config)
        # Start library
        self.ep.libStart()
        # Start polling
        if not USE_THREADS:
            self._onTimer()



    def _createAcc(self, acc_cfg):
        acc = account.Account(self)
        acc.cfg = acc_cfg
        self.accList.append(acc)
        ##self.updateAccount(acc)
        acc.create(acc.cfg)
        acc.cfgChanged = False
        ##self.updateAccount(acc)

    def initGui(self):
        # Main pane, a Treeview
        self.tv = ttk.Treeview(self, columns=('Status'), show='tree')
        self.tv.pack(side='top', fill='both', expand='yes', padx=5, pady=5)

        # Handle close event
        self.master.protocol("WM_DELETE_WINDOW", self._onClose)

    def _onTimer(self):
        if not self.quitting:
            self.ep.libHandleEvents(10)
            if not self.quitting:
                self.master.after(50, self._onTimer)

    def _onClose(self):
        self.saveConfig()
        self.quitting = True
        self.ep.libDestroy()
        self.ep = None
        self.update()
        self.quit()


class ExceptionCatcher:
    """Custom Tk exception catcher, mainly to display more information
       from pj.Error exception
    """
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget
    def __call__(self, *args):
        try:
            if self.subst:
                args = apply(self.subst, args)
            return apply(self.func, args)
        except pj.Error as error:
            print("Exception:\r\n")
            print("  ," + error.info() + "\r\n")
            print("Traceback:\r\n")
            print(traceback.print_stack())
            print(1, 'Exception: ' + error.info() + '\n')
        except Exception as error:
            print("Exception:\r\n")
            print("  ," +  str(error) + "\r\n")
            print("Traceback:\r\n")
            print(traceback.print_stack())
            print(1, 'Exception: ' + str(error) + '\n')

def main():
    #tk.CallWrapper = ExceptionCatcher
    app = Application()
    app.start()
    app.mainloop()

if __name__ == '__main__':
    main()
