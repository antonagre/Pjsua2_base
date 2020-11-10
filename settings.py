import pjsua2 as pj

# Transport setting
class SipTransportConfig:
	def __init__(self, type, enabled):
		#pj.PersistentObject.__init__(self)
		self.type = type
		self.enabled = enabled
		self.config = pj.TransportConfig()
	def readObject(self, node):
		child_node = node.readContainer("SipTransport")
		self.type = child_node.readInt("type")
		self.enabled = child_node.readBool("enabled")
		self.config.readObject(child_node)
	def writeObject(self, node):
		child_node = node.writeNewContainer("SipTransport")
		child_node.writeInt("type", self.type)
		child_node.writeBool("enabled", self.enabled)
		self.config.writeObject(child_node)

# Account setting with buddy list
class AccConfig:
	def __init__(self):
		self.enabled = True
		self.config = pj.AccountConfig()
		self.buddyConfigs = []
	def readObject(self, node):
		acc_node = node.readContainer("Account")
		self.enabled = acc_node.readBool("enabled")
		self.config.readObject(acc_node)
		buddy_node = acc_node.readArray("buddies")
		while buddy_node.hasUnread():
			buddy_cfg = pj.BuddyConfig()
			buddy_cfg.readObject(buddy_node)
			self.buddyConfigs.append(buddy_cfg)
	def writeObject(self, node):
		acc_node = node.writeNewContainer("Account")
		acc_node.writeBool("enabled", self.enabled)
		self.config.writeObject(acc_node)
		buddy_node = acc_node.writeNewArray("buddies")
		for buddy in self.buddyConfigs:
			buddy_node.writeObject(buddy)

	
# Master settings
class AppConfig:
	def __init__(self):
		self.epConfig = pj.EpConfig()	# pj.EpConfig()
		self.udp = SipTransportConfig(pj.PJSIP_TRANSPORT_UDP, True)
		self.tcp = SipTransportConfig(pj.PJSIP_TRANSPORT_TCP, True)
		self.tls = SipTransportConfig(pj.PJSIP_TRANSPORT_TLS, False)
		self.accounts = []		# Array of AccConfig
		
	def loadFile(self, file):
		json = pj.JsonDocument()
		json.loadFile(file)
		root = json.getRootContainer()
		self.epConfig = pj.EpConfig()
		self.epConfig.readObject(root)
		
		tp_node = root.readArray("transports")
		self.udp.readObject(tp_node)
		self.tcp.readObject(tp_node)
		if tp_node.hasUnread():
			self.tls.readObject(tp_node)
			
		acc_node = root.readArray("accounts")
		while acc_node.hasUnread():
			acfg = AccConfig()
			acfg.readObject(acc_node)
			self.accounts.append(acfg)
			
	def saveFile(self,file):
		json = pj.JsonDocument()
		
		# Write endpoint config
		json.writeObject(self.epConfig)
		
		# Write transport config
		tp_node = json.writeNewArray("transports")
		self.udp.writeObject(tp_node)
		self.tcp.writeObject(tp_node)
		self.tls.writeObject(tp_node)
		
		# Write account configs
		node = json.writeNewArray("accounts")
		for acc in self.accounts:
			acc.writeObject(node)
		json.saveFile(file)
