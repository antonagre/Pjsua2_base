import sys
import account
import endpoint
import settings
import os
import time

# You may try to enable pjsua worker thread by setting USE_THREADS below to True *and*
# recreate the swig module with adding -threads option to swig (uncomment USE_THREADS 
# in swig/python/Makefile). In my experiment this would crash Python as reported in:
# http://lists.pjsip.org/pipermail/pjsip_lists.pjsip.org/2014-March/017223.html
USE_THREADS = False

write=sys.stdout.write

class Application():
    """
    The Application main
    """
    def __init__(self):
        global USE_THREADS
        # Accounts
        self.accList = []

        self.quitting = False

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
        self.start()

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
            self.mainLoop()



    def _createAcc(self, acc_cfg):
        acc = account.Account(self)
        acc.cfg = acc_cfg
        self.accList.append(acc)
        acc.create(acc.cfg)
        acc.cfgChanged = False

    def mainLoop(self):
        while(not self.quitting):
            print("ref")
            self.ep.libHandleEvents(10)
            time.sleep(5)

    def _onClose(self):
        self.saveConfig()
        self.quitting = True
        self.ep.libDestroy()
        self.ep = None
        self.update()
        self.quit()



def main():
    app = Application()

if __name__ == '__main__':
    main()
