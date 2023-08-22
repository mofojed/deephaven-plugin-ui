# The UI widget plugin

from deephaven.plugin import Registration, Callback
from typing import List, Any
from deephaven.plugin.object_type import Exporter, BidirectionalObjectType, MessageStream
import json
import io
from .component import *

NAME_COMPONENT_NODE = "deephaven.ui.component.ComponentNode"
NAME_TEXT_INPUT = "deephaven.ui.TextInput"

__version__ = '0.0.1.dev0'


class ComponentNodeMessageStream(MessageStream):
    def __init__(self, node: ComponentNode, connection: MessageStream):
        # print("ComponentNodeMessageStream __init__")
        self._node = node
        self._connection = connection

    def start(self) -> None:
        # print("ComponentNodeMessageStream start")
        context = RenderContext()

        def handle_change():
            # print("MJB ComponentNodeMessageStream handle_change")
            result = self._node.render(context)
            self.send_result(result)

        context.set_on_change(handle_change)
        result = self._node.render(context)
        self.send_result(result)

    def send_result(self, result) -> None:
        # print("MJB send_result result = ", str(result))

        # payload = json.dumps({'result': result}).encode()
        # print("MJB send_result payload = ", payload)
        # self._connection.on_data(payload, [])

        self._connection.on_data('updated'.encode(), result)
        # print("MJB send_result completed")

    def on_close(self) -> None:
        pass

    def on_data(self, payload: bytes, references: List[Any]) -> None:
        print(f"Data received: {payload}")


class ComponentNodeType(BidirectionalObjectType):
    @property
    def name(self) -> str:
        return NAME_COMPONENT_NODE

    def is_type(self, obj: any) -> bool:
        return isinstance(obj, ComponentNode)

    # def to_bytes(self, exporter: Exporter, panel: DeephavenUiPanel) -> bytes:
    #     return export_figure(exporter, figure)

    def create_client_connection(self, obj: ComponentNode, connection: MessageStream):
        client_connection = ComponentNodeMessageStream(obj, connection)
        client_connection.start()
        return client_connection


class TextInput:
    def __init__(self, initial_value, on_change):
        self._value = initial_value
        self._on_change = on_change

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self._on_change(new_value)


def text_input(initial_value, on_change):
    return TextInput(initial_value, on_change)


class TextInputMessageStream(MessageStream):
    def __init__(self, text_input: TextInput, connection: MessageStream):
        self._text_input = text_input
        self._connection = connection

    def on_close(self) -> None:
        pass

    def on_data(self, payload: bytes, references: List[Any]) -> None:
        decoded_payload = io.BytesIO(payload).read().decode()
        self._text_input.value = decoded_payload


class TextInputType(BidirectionalObjectType):
    @property
    def name(self) -> str:
        return NAME_TEXT_INPUT

    def is_type(self, obj: any) -> bool:
        return isinstance(obj, TextInput)

    def create_client_connection(self, obj: TextInput, connection: MessageStream):
        client_connection = TextInputMessageStream(obj, connection)
        connection.on_data(obj.value.encode(), [])
        return client_connection


class UIRegistration(Registration):
    @classmethod
    def register_into(cls, callback: Callback) -> None:
        # print("MJB registering ComponentNodeType")
        callback.register(ComponentNodeType)
        callback.register(TextInputType)
