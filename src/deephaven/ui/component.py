# Prototype for programmatic layouts/callbacks
# Uses a React-like syntax, with hooks
import functools
from typing import Optional


class RenderContext:
    """
    Context for rendering a component.
    """
    def __init__(self):
        self._hook_index = -1
        self._state = {}
        self._children_context = {}
        self._on_change = lambda: None

    def _notify_change(self):
        """
        Notify the parent context that this context has changed.
        Note that we're just re-rendering the whole tree on change.
        TODO: We should be able to do better than this, and only re-render the parts that have actually changed.
        """
        # print("MJB _notify_change")
        self._on_change()

    def set_on_change(self, on_change):
        """
        Set the on_change callback.
        """
        self._on_change = on_change

    def get_state(self, key, default=None):
        """
        Get the state for the given key.
        """
        if key not in self._state:
            self._state[key] = default
        return self._state[key]

    def set_state(self, key, value):
        """
        Set the state for the given key.
        """
        self._state[key] = value
        self._notify_change()

    def get_child_context(self, key):
        """
        Get the child context for the given key.
        """
        if key not in self._children_context:
            child_context = RenderContext()
            child_context.set_on_change(self._notify_change)
            self._children_context[key] = child_context
        return self._children_context[key]

    def start_render(self):
        """
        Start rendering this component.
        """
        self._hook_index = -1

    def finish_render(self):
        """
        Finish rendering this component.
        """
        # TODO: Should verify that the correct number of hooks were called, state is correct etc
        pass

    def next_hook_index(self):
        """
        Increment the hook index.
        """
        self._hook_index += 1
        return self._hook_index


class UiSharedInternals:
    _current_context: Optional[RenderContext] = None

    @property
    def current_context(self) -> RenderContext:
        return self._current_context


_deephaven_ui_shared_internals: UiSharedInternals = UiSharedInternals()


def _get_context() -> RenderContext:
    return _deephaven_ui_shared_internals.current_context


def _set_context(context):
    _deephaven_ui_shared_internals._current_context = context


class ComponentNode:
    def __init__(self, component_type, render):
        """
        Create a component node.
        :param component_type: Type of the component. Typically, the module joined with the name of the function.
        :param render: The render function to call when the component needs to be rendered.
        """
        self._type = component_type
        self._render = render

    def render(self, context: RenderContext, render_deep=True):
        """
        Render the component.
        :param context: The context to render the component in.
        :param render_deep: Whether to render the component's children.
        :return: The rendered component.
        """
        def render_child(child, child_context):
            if isinstance(child, ComponentNode):
                return child.render(child_context, render_deep)
            else:
                return child

        # print("MJB ComponentNode.render")
        result = self._render(context)
        if render_deep:
            # Array of children returned, render them all
            if isinstance(result, list):
                result = [render_child(child, context.get_child_context(i)) for i, child in enumerate(result)]
            else:
                result = render_child(result, context.get_child_context(0))
        return result

    @property
    def type(self):
        return self._type


def _get_component_type(func):
    """
    Get the type of the component from the passed in function.
    """
    return func.__module__ + "." + func.__qualname__


def component(func):
    """
    Create a ComponentNode from the passed in function.
    """

    @functools.wraps(func)
    def make_component_node(*args, **kwargs):
        component_type = _get_component_type(func)

        def render(context: RenderContext):
            """
            Render the component. Should only be called when actually rendering the component, e.g. exporting it to the client.
            :param context: Context to render the component in
            :return: The rendered component.
            """
            old_context = _get_context()
            # print("MJB old context is " + str(old_context) + " and new context is " + str(context))

            _set_context(context)
            context.start_render()

            result = func(*args, **kwargs)

            context.finish_render()
            # print("Resetting to old context" + str(old_context))
            _set_context(old_context)
            return result

        return ComponentNode(component_type, render)

    return make_component_node


def use_state(initial_value):
    # print("use_state 10 current_context is" + str(_deephaven_current_context))
    # Just using a sequential index for hooks, this should be valid
    context = _get_context()
    hook_index = context.next_hook_index()

    value = context.get_state(hook_index, initial_value)

    def set_value(new_value):
        # Set the value in the context state and trigger a rerender
        # print("MJB use_state set_value called with " + str(new_value))
        context.set_state(hook_index, new_value)

    return value, set_value
