import random
import pjsua2 as pj
import call
import sys

write=sys.stdout.write

# Account class
class Account(pj.Account):
    """
    High level Python Account object, derived from pjsua2's Account object.
    """
    def __init__(self, app):
        pj.Account.__init__(self)
        self.app = app
        self.randId = random.randint(1, 9999)
        self.cfg =  pj.AccountConfig()
        self.cfgChanged = False
        self.buddyList = []
        self.chatList = []
        self.deleting = False

    def statusText(self):
        status = '?'
        if self.isValid():
            ai = self.getInfo()
            if ai.regLastErr:
                status = self.app.ep.utilStrError(ai.regLastErr)
            elif ai.regIsActive:
                if ai.onlineStatus:
                    if len(ai.onlineStatusText):
                        status = ai.onlineStatusText
                    else:
                        status = "Online"
                else:
                    status = "Registered"
            else:
                if ai.regIsConfigured:
                    if ai.regStatus/100 == 2:
                        status = "Unregistered"
                    else:
                        status = ai.regStatusText
                else:
                    status = "Doesn't register"
        else:
            status = '- not created -'
        return status

    def onRegState(self, prm):

        pass

    def onIncomingCall(self, prm):
        c = call.Call(self, call_id=prm.callId)
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 180
        c.answer(call_prm)
        ci = c.getInfo()
        print("Incoming call for account '%s'" % self.cfg.idUri)
        r=input("ACCEPT y/n ")
        if r == "y":
            call_prm.statusCode = 200
            c.answer(call_prm)

            # find/create chat instance
            chat = self.findChat(ci.remoteUri)
            if not chat: chat = self.newChat(ci.remoteUri)

            chat.showWindow()
            chat.registerCall(ci.remoteUri, c)
            chat.updateCallState(c, ci)
        else:
            c.hangup(call_prm)
