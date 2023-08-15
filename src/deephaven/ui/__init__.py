# The UI widget plugin

from deephaven.plugin import Registration, Callback
from typing import List, Any
from deephaven.plugin.object_type import Exporter, BidirectionalObjectType, MessageStream
import json
import io
from .component import *

NAME = "deephaven.ui.Panel"
TEXT_INPUT_NAME = "deephaven.ui.TextInput"

__version__ = '0.0.1.dev0'

class DeephavenUiPanel:
    def __init__(self, component):
        self._component = component

class DeephavenUiMessageStream(MessageStream):
    def __init__(self, panel: DeephavenUiPanel, connection: MessageStream):
        self._panel = panel
        self._connection = connection

    def start(self) -> None:
        result = self._component()
        self.send_result(result)
        add_component_listener(self.on_component_updated)

    def send_result(self, result) -> None:
        payload = json.dumps({ 'result': result }).encode()
        self._connection.on_data(payload, self.objects)

    def on_close(self) -> None:
        pass

    def on_data(self, payload: bytes, references: List[Any]) -> None:
        print(f"Data received: {payload}")

    def on_component_updated(self, component, result):
        if component == self._panel._component:
            self.send_result(result)

class DeephavenUiPanelType(BidirectionalObjectType):
    @property
    def name(self) -> str:
        return NAME

    def is_type(self, obj: any) -> bool:
        return isinstance(obj, DeephavenUiPanel)

    # def to_bytes(self, exporter: Exporter, panel: DeephavenUiPanel) -> bytes:
    #     return export_figure(exporter, figure)

    def create_client_connection(self, obj: object, connection: MessageStream):
        client_connection = DeephavenUiMessageStream(obj, connection)
        client_connection.start()
        return client_connection

class TextInput:
    def __init__(self, initial_value, on_change):
        self._component = component
        self._value = initial_value
        self._on_change = on_change

class TextInputMessageStream(MessageStream):
    def __init__(self, text_input: TextInput, connection: MessageStream):
        self._text_input = text_input
        self._connection = connection

    def on_close(self) -> None:
        pass

    def on_data(self, payload: bytes, references: List[Any]) -> None:
        print(f"TextInput Data received: {payload}, {type(payload)}, {str(payload)}")
        print(f"Bytes decoded: {io.BytesIO(payload).read().decode()}")
        # print(f"Bytes: {payload[0]}")
        # self._text_input._on_change(payload.decode())

class TextInputType(BidirectionalObjectType):
    @property
    def name(self) -> str:
        return TEXT_INPUT_NAME

    def is_type(self, obj: any) -> bool:
        return isinstance(obj, TextInput)

    # def to_bytes(self, exporter: Exporter, panel: DeephavenUiPanel) -> bytes:
    #     return export_figure(exporter, figure)

    def create_client_connection(self, obj: object, connection: MessageStream):
        client_connection = TextInputMessageStream(obj, connection)
        connection.on_data("".encode(), [])
        return client_connection

class UIRegistration(Registration):
    @classmethod
    def register_into(cls, callback: Callback) -> None:
        callback.register(DeephavenUiPanelType)
        callback.register(TextInputType)
