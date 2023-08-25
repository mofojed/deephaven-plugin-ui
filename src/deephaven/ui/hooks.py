from .shared_internal import _get_context


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
