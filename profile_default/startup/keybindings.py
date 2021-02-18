# from IPython import get_ipython
# from prompt_toolkit.enums import DEFAULT_BUFFER
# from prompt_toolkit.keys import Keys
# from prompt_toolkit.filters import HasFocus, HasSelection, ViInsertMode, EmacsInsertMode
# from prompt_toolkit.key_binding.vi_state import InputMode
#
# ip = get_ipython()
#
#
# def switch_to_navigation_mode(event):
#     buf = event.current_buffer
#     vi_state = event.cli.vi_state
#     print(f'vi_state: {vi_state}')
#     # vi_state.input_mode = InputMode.NAVIGATION
#
#
# if getattr(ip, 'pt_app', None):
#     print('\tbinding Keys.ControlN to switch_to_navigation_mode()...')
#     registry = ip.pt_app.key_bindings
#     registry.add_binding(Keys.ControlN,
#                          filter=(HasFocus(DEFAULT_BUFFER)
#                                  #  & ViInsertMode()
#                                  ))(switch_to_navigation_mode)
