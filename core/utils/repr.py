import shutil
from collections import OrderedDict
from .strings import tab_left

class NiceRepr:
    _repr_ = []

    def __repr__(self, max_size=None):
        # if spaces:
        #     print('i', spaces, self.__class__.__name__)
        props = OrderedDict()
        for key in self._repr_:
            if isinstance(key, dict):
                props.update(key)
            else:
                item = getattr(self, key)
                props[key] = item
        return nice_repr(props, name=self.__class__.__name__, max_size=max_size)


def nice_repr(value, name=None, max_size=None):

    if max_size is None:
        terminal_size = shutil.get_terminal_size().columns
        max_size =  terminal_size - 3

    if name is not None:
        max_size -= len(name)

    if isinstance(value, NiceRepr):
        return value.__repr__(max_size=max_size)

    elif isinstance(value, (list, tuple)):
        output = "[" if isinstance(value, list) else '('
        inner = ', '.join([nice_repr(v, max_size=max_size-2) for v in value])
        if '\n' in inner or len(inner) > max_size:
            for v in value:
                output += "\n"
                output += tab_left(nice_repr(v, max_size=max_size-4), spaces=4)
                output += ','
            output = output[:-1]
            output += "\n"
        else:
            output += inner

        output += ']' if isinstance(value, list) else ')'
        return output

    elif isinstance(value, dict):
        key_repr = lambda k: repr(k) if name is None else k
        sep_char = ": " if name is None else f"="
        rep_str = ", ".join([f"{key_repr(k)}{sep_char}{repr(v)}" for k,v in value.items()])
        output = f"{name}(" if name else "{"
        if '\n' in rep_str or len(rep_str) > max_size:
            inner = ""
            for i,(k,v) in enumerate(value.items()):
                if isinstance(v, dict):
                    v_repr = nice_repr(
                        v,
                        max_size=max_size-4-len(sep_char)-len(key_repr(k))
                    )
                elif isinstance(v, NiceRepr):
                    v_repr = v.__repr__(
                        max_size=max_size-4-len(sep_char)-len(key_repr(k))
                    )
                else:
                    v_repr = nice_repr(v, max_size=max_size-4-len(sep_char)-len(key_repr(k)))

                inner += (",\n" if i else "") + f"{key_repr(k)}{sep_char}{v_repr}"
            output += "\n" + tab_left(inner)
            if name:
                output += "\n)"
            else:
                output += "\n}"
            return output
        else:
            if name:
                return output + rep_str + ")"
            else:
                return output + rep_str + "}"

    else:
        return repr(value)
