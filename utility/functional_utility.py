#arbi
def call_handler(condition_to_handler, *args, **kwargs):
    matched = False
    return_list = []
    for condition, handler_list in condition_to_handler.items():
        if matched is False:
            if condition(kwargs["operand"]):
                # remove the operand from kwargs
                kwargs.pop("operand")
                if len(handler_list) == 0:
                    raise Exception("no handler found")
                for handler in handler_list:
                    return_list.append(handler(**kwargs))
                break
        else:
            if condition(kwargs["operand"]):
                raise Exception("multiple handlers found")
    else:
        raise Exception("no handler found")
    return return_list