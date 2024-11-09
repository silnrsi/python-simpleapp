import wx  # type: ignore

from argsupport.gooey.gui.components.widgets.dropdown import Dropdown
from argsupport.gooey.python_bindings import types as t
from argsupport.gooey.gui import formatters


class Counter(Dropdown):

    def setValue(self, value):
        index = self._meta['choices'].index(value) + 1
        self.widget.SetSelection(index)

    def getUiState(self) -> t.FormField:
        widget: wx.ComboBox = self.widget
        return t.Counter(
            id=self._id,
            type=self.widgetInfo['type'],
            selected=self.getWidgetValue(),
            choices=widget.GetStrings(),
            error=self.error.GetLabel() or None,
            enabled=self.IsEnabled(),
            visible=self.IsShown()
        )



    def formatOutput(self, metadata, value):
        return formatters.counter(metadata, value)
