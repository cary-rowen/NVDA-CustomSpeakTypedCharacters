# customSpeakTypedCharacters: Custom Speak Typed Characters for NVDA
# Copyright 2024 Cary-rowen <manchen_0528@outlook.com>
# License: GNU General Public License version 2.0

from enum import Enum
from typing import Callable
import addonHandler
import globalPluginHandler
import controlTypes
import ui
import config
import inputCore
from globalCommands import SCRCAT_SPEECH
from scriptHandler import script
from NVDAObjects import NVDAObject

addonHandler.initTranslation()

#: Configuration specification, adding customizeSpeakTypedCharacters and customizeSpeakTypedWords options
confspec = {
	"customizeSpeakTypedCharacters": "integer(default=2)",
	"customizeSpeakTypedWords": "integer(default=2)"
}
config.conf.spec["customSpeakTypedConfig"] = confspec

class SpeakTypedMode(Enum):
	OFF = 0
	ON = 1
	EDITABLE_ONLY = 2

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		#: Read the last value used by the user, default to EDITABLE_ONLY if not set
		if "customizeSpeakTypedCharacters" not in config.conf["customSpeakTypedConfig"]:
			config.conf["customSpeakTypedConfig"]["customizeSpeakTypedCharacters"] = SpeakTypedMode.EDITABLE_ONLY.value
		if "customizeSpeakTypedWords" not in config.conf["customSpeakTypedConfig"]:
			config.conf["customSpeakTypedConfig"]["customizeSpeakTypedWords"] = SpeakTypedMode.EDITABLE_ONLY.value

	@staticmethod
	def is_editable(obj: NVDAObject) -> bool:
		"""
		Check if the object is an editable control.
		"""
		controls = {controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_DOCUMENT, controlTypes.ROLE_TERMINAL}
		return (obj.role in controls or controlTypes.STATE_EDITABLE in obj.states) and controlTypes.STATE_READONLY not in obj.states

	def event_typedCharacter(self, obj: NVDAObject, nextHandler: Callable[[], None], ch: str) -> None:
		"""
		Handle typed character event based on the customizeSpeakTypedCharacters and customizeSpeakTypedWords settings.
		"""
		# Handle characters
		char_mode = SpeakTypedMode(int(config.conf["customSpeakTypedConfig"]["customizeSpeakTypedCharacters"]))
		if char_mode == SpeakTypedMode.EDITABLE_ONLY:
			config.conf["keyboard"]["speakTypedCharacters"] = self.is_editable(obj)
		else:
			config.conf["keyboard"]["speakTypedCharacters"] = (char_mode == SpeakTypedMode.ON)

		# Handle words
		word_mode = SpeakTypedMode(int(config.conf["customSpeakTypedConfig"]["customizeSpeakTypedWords"]))
		if word_mode == SpeakTypedMode.EDITABLE_ONLY:
			config.conf["keyboard"]["speakTypedWords"] = self.is_editable(obj)
		else:
			config.conf["keyboard"]["speakTypedWords"] = (word_mode == SpeakTypedMode.ON)

		nextHandler()

	@script(
		description=_("Cycle through speak typed characters modes: off, on, and on for editable controls only."),
		category=SCRCAT_SPEECH,
		gestures=["kb:NVDA+2"]
	)
	def script_toggleSpeakTypedCharacters(self, gesture: inputCore.InputGesture) -> None:
		"""
		Toggle the speak typed characters mode between off, on, and on for editable controls only.
		"""
		current_value = SpeakTypedMode(int(config.conf["customSpeakTypedConfig"]["customizeSpeakTypedCharacters"]))
		#: Cycle through OFF, ON, EDITABLE_ONLY
		new_value = SpeakTypedMode((current_value.value + 1) % 3)
		config.conf["customSpeakTypedConfig"]["customizeSpeakTypedCharacters"] = new_value.value

		match new_value:
			case SpeakTypedMode.OFF:
				config.conf["keyboard"]["speakTypedCharacters"] = False
				state = _("speak typed characters off")
			case SpeakTypedMode.ON:
				config.conf["keyboard"]["speakTypedCharacters"] = True
				state = _("speak typed characters on")
			case SpeakTypedMode.EDITABLE_ONLY:
				state = _("speak typed characters in editable controls only")

		ui.message(state)

	@script(
		description=_("Cycle through speak typed words modes: off, on, and on for editable controls only."),
		category=SCRCAT_SPEECH,
		gestures=["kb:NVDA+3"]
	)
	def script_toggleSpeakTypedWords(self, gesture: inputCore.InputGesture) -> None:
		"""
		Toggle the speak typed words mode between off, on, and on for editable controls only.
		"""
		current_value = SpeakTypedMode(int(config.conf["customSpeakTypedConfig"]["customizeSpeakTypedWords"]))
		#: Cycle through OFF, ON, EDITABLE_ONLY
		new_value = SpeakTypedMode((current_value.value + 1) % 3)
		config.conf["customSpeakTypedConfig"]["customizeSpeakTypedWords"] = new_value.value

		match new_value:
			case SpeakTypedMode.OFF:
				config.conf["keyboard"]["speakTypedWords"] = False
				state = _("speak typed words off")
			case SpeakTypedMode.ON:
				config.conf["keyboard"]["speakTypedWords"] = True
				state = _("speak typed words on")
			case SpeakTypedMode.EDITABLE_ONLY:
				state = _("speak typed words in editable controls only")

		ui.message(state)
