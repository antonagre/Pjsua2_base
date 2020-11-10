import pjsua2 as pj
import endpoint as ep

# Call class
class Call(pj.Call):
    """
    High level Python Call object, derived from pjsua2's Call object.
    """
    def __init__(self, acc, peer_uri='', chat=None, call_id = pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.acc = acc
        self.peerUri = peer_uri
        self.chat = chat
        self.connected = False
        self.onhold = False

    def onCallState(self, prm):
        ci = self.getInfo()
        self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED


    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for mi in ci.media:
            print("cici")
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
              (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or \
               mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
                m = self.getMedia(mi.index)
                am = pj.AudioMedia.typecastFromMedia(m)
                # connect ports
                ep.Endpoint.instance.audDevManager().getCaptureDevMedia().startTransmit(am)
                am.startTransmit(ep.Endpoint.instance.audDevManager().getPlaybackDevMedia())

                if mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD and not self.onhold:
                    self.onhold = True
                elif mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE and self.onhold:
                    self.onhold = False


    def onInstantMessage(self, prm):
        pass

    def onInstantMessageStatus(self, prm):
        if prm.code/100 == 2: return

    def onTypingIndication(self, prm):
        pass

    def onDtmfDigit(self, prm):
        pass

    def onCallMediaTransportState(self, prm):
        pass

