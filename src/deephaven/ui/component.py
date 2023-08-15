# Prototype for programmatic layouts/callbacks
# Uses a React-like syntax, with hooks
_deephaven_current_context = {}
_deephaven_component_listeners = []

# Convenience function for debugging
def _reset_state():
    global _deephaven_current_context
    _deephaven_current_context = {}


def _notify_listener_updated(component, result):
    for listener in _deephaven_component_listeners:
        listener(component, result)


def add_component_listener(listener):
    _deephaven_component_listeners.append(listener)

CHILD_INDEX_KEY = "_child_index"
CHILD_CONTEXT_KEY = "_child_context"
HOOK_INDEX_KEY = "_hook_index"
RERENDER_KEY = "_rerender"
STATE_KEY = "_state"

def component(func):
    """
    Render a component. Re-run when kwargs or state changes.
    """

    def render(**kwargs):
        # Set the context for this components render cycle
        # Necessary for hooks to work
        global _deephaven_current_context
        parent_context = _deephaven_current_context

        # We're just using a sequential key, when this should probably be randomly generated UUID or something
        child_index = parent_context.get(CHILD_INDEX_KEY, -1) + 1

        # Get the child contexts from the parent
        parent_context[CHILD_INDEX_KEY] = child_index
        child_contexts = parent_context.get(CHILD_CONTEXT_KEY, {})

        # Grab this renders context
        current_context = child_contexts.get(child_index, {})
        child_contexts[child_index] = current_context
        parent_context[CHILD_CONTEXT_KEY] = child_contexts

        # print("render 10 current_context is" + str(current_context))
        def rerender():
            global _deephaven_current_context
            current_context.pop(HOOK_INDEX_KEY, None)
            current_context.pop(CHILD_INDEX_KEY, None)
            _deephaven_current_context = current_context

            # TODO: Need the return value from the render function
            # Also need to listen for when the child rerenders?
            result = func(**kwargs)

            child_contexts[child_index] = current_context
            _deephaven_current_context = parent_context

            return result

        # For now just re-render the whole tree when any state changes
        if RERENDER_KEY not in parent_context:
            def toplevel_rerender():
                result = rerender()
                _notify_listener_updated(render, result)

            parent_context[RERENDER_KEY] = toplevel_rerender

        current_context[RERENDER_KEY] = parent_context.get(RERENDER_KEY)

        return rerender()

    return render


def use_state(initial_value):
    # print("use_state 10 current_context is" + str(_deephaven_current_context))
    # Just using a sequential index for hooks, this should be valid
    hook_index = _deephaven_current_context.get(HOOK_INDEX_KEY, -1) + 1
    _deephaven_current_context[HOOK_INDEX_KEY] = hook_index

    # Grab the state from the context
    state = _deephaven_current_context.get(STATE_KEY, {})
    _deephaven_current_context[STATE_KEY] = state

    # Grab the value from the state, re-assign it if necessary
    value = state.get(hook_index, initial_value)
    state[hook_index] = value

    # Grab the rerender function so we can rerender the component when value is set
    rerender = _deephaven_current_context.get(RERENDER_KEY)

    def set_value(new_value):
        # Set the value in the state and trigger a rerender
        state[hook_index] = new_value
        rerender()

    return value, set_value
