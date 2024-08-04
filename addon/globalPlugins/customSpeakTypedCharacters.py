# customSpeakTypedCharacters: Custom Speak Typed Characters for NVDA
# Copyright 2024 Cary-rowen <manchen_0528@outlook.com>
# License: GNU General Public License version 2.0

from enum import Enum
from typing import Callable
import globalPluginHandler
import controlTypes
import ui
import config
from scriptHandler import script
from NVDAObjects import NVDAObject
import inputCore

# We do not enable localization of add-ons at this time
# addonHandler.initTranslation()

#: Configuration specification, adding customizeSpeakTypedCharacters option
confspec = {
	"customizeSpeakTypedCharacters": "integer(default=2)"
}
config.conf.spec["keyboard"] = confspec

class SpeakTypedCharactersMode(Enum):
	OFF = 0
	ON = 1
	EDITABLE_ONLY = 2

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		#: Read the last value used by the user, default to EDITABLE_ONLY if not set
		if "customizeSpeakTypedCharacters" not in config.conf["keyboard"]:
			config.conf["keyboard"]["customizeSpeakTypedCharacters"] = SpeakTypedCharactersMode.EDITABLE_ONLY.value

	def is_editable(self, obj: NVDAObject) -> bool:
		"""
		Check if the object is an editable control.
		"""
		controls = {controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_DOCUMENT, controlTypes.ROLE_TERMINAL}
		return (obj.role in controls or controlTypes.STATE_EDITABLE in obj.states) and controlTypes.STATE_READONLY not in obj.states

	def event_typedCharacter(self, obj: NVDAObject, nextHandler: Callable[[], None], ch: str) -> None:
		"""
		Handle typed character event based on the customizeSpeakTypedCharacters setting.
		"""
		mode = SpeakTypedCharactersMode(int(config.conf["keyboard"]["customizeSpeakTypedCharacters"]))
		if mode == SpeakTypedCharactersMode.EDITABLE_ONLY:
			config.conf["keyboard"]["speakTypedCharacters"] = self.is_editable(obj)
		else:
			config.conf["keyboard"]["speakTypedCharacters"] = (mode == SpeakTypedCharactersMode.ON)
		nextHandler()

	@script(
		description=_("Cycle through speak typed characters modes: off, on, and on for editable controls only."),
		gestures=["kb:NVDA+2"]
	)
	def script_toggleSpeakTypedCharacters(self, gesture: inputCore.InputGesture) -> None:
		"""
		Toggle the speak typed characters mode between off, on, and on for editable controls only.
		"""
		current_value = SpeakTypedCharactersMode(int(config.conf["keyboard"]["customizeSpeakTypedCharacters"]))
		#: Cycle through OFF, ON, EDITABLE_ONLY
		new_value = SpeakTypedCharactersMode((current_value.value + 1) % 3)
		config.conf["keyboard"]["customizeSpeakTypedCharacters"] = new_value.value

		match new_value:
			case SpeakTypedCharactersMode.OFF:
				config.conf["keyboard"]["speakTypedCharacters"] = False
				state = _("speak typed characters off")
			case SpeakTypedCharactersMode.ON:
				config.conf["keyboard"]["speakTypedCharacters"] = True
				state = _("speak typed characters on")
			case SpeakTypedCharactersMode.EDITABLE_ONLY:
				state = _("speak typed characters in editable controls only")

		ui.message(state)
