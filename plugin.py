from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.ActionMap import NumberActionMap, ActionMap
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigInteger, getConfigListEntry, ConfigSlider, ConfigEnableDisable

class TranscodingSetup(ConfigListScreen, Screen):
	skin = 	"""
		<screen position="center,center" size="500,114" title="TranscodingSetup">
			<eLabel position="0,0" size="500,22" font="Regular;20" text="Default values for trancoding" />

			<widget name="config" position="4,26" font="Regular;20" size="492,60" />

			<ePixmap pixmap="skin_default/buttons/red.png" position="0,76" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="150,76" size="140,40" alphatest="on" />

			<widget source="key_red" render="Label" position="0,76" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1"/>
			<widget source="key_green" render="Label" position="150,76" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1"/>

		</screen>
		"""

	def KeyNone(self):
		None

	def callbackNone(self, *retval):
		None

	def __init__(self, session):
		bitrate_choices = [( 50, "50 kbps" ), ( 100, "100 kbps" ), ( 200, "200 kbps" ), ( 500, "500 kbps" ), ( 1000, "1 Mbps" ), ( 2000, "2 Mbps" )]
		size_choices = [ "480p", "576p", "720p" ]

		current_bitrate_value = ""
		current_size = ""

		Screen.__init__(self, session)

		config_list = []
		ConfigListScreen.__init__(self, config_list)

		self.bitrate = ConfigSelection(choices = bitrate_choices)
		self.size = ConfigSelection(choices = size_choices)

		config_list.append(getConfigListEntry(_("Bitrate"), self.bitrate));
		config_list.append(getConfigListEntry(_("Video size"), self.size));

		self["config"].list = config_list

		rawcontent = []

		with open("/etc/enigma2/streamproxy.conf", "r") as f:
			rawcontent = f.readlines()
			rawcontent = [x.translate(None, ' \n\r')for x in rawcontent]
			f.close()

		self.content = []

		for line in rawcontent:
			if not line.startswith('#') and not line.startswith(';'):
				tokens = line.split('=')

				if(tokens[0] == "bitrate"):
					for tuple in bitrate_choices:
						if int(tokens[1]) <= int(tuple[0]):
							self.bitrate.setValue(tuple[0])
							break

				if(tokens[0] == "size"):
					self.size.setValue(tokens[1])

				self.content += [ tokens ]

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "ColorActions" ],
		{
			"red": self.keyCancel,
			"green": self.keyGo,
			"ok": self.keyGo,
			"cancel": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Quit"))
		self["key_green"] = StaticText(_("Set"))

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keyCancel(self):
		self.close()

	def keyGo(self):
		for token in self.content:
			if(token[0] == "bitrate"):
				token[1] = self.bitrate.getValue()

			if(token[0] == "size"):
				token[1] = self.size.getValue()

		with open("/etc/enigma2/streamproxy.conf", "w") as f:
			for token in self.content:
				f.write("%s = %s\n" % (token[0], token[1]))
			f.close()

		self.close()

def main(session, **kwargs):
	session.open(TranscodingSetup)

def Plugins(**kwargs):
	return [PluginDescriptor(name = _("TranscodingSetup"), description = _("Set up default transcoding parameters"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main)]
