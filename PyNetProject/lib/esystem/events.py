import inspect


class Event(object):

    def __init__(self, **signature):
        self._signature = signature
        self._argnames = set(signature.keys())
        self._handlers = []

    def _kwargs_str(self):
        return ", ".join(k + "=" +
                         (v.__name__ if hasattr(v, "__name__") else v.name if hasattr(v, "name") else str(v))
                         for k, v in self._signature.items())

    def remove_listener(self, handler):
        self._handlers.remove(handler)
        return self

    def add_listener(self, handler):
        params = inspect.signature(handler).parameters
        valid = True
        arg_names = set(n for n in params.keys())
        if arg_names != self._argnames:
            valid = False
        else:
            for p in params.values():
                if p.kind == p.VAR_KEYWORD:
                    valid = True
                    break
                if p.kind not in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY):
                    valid = False
                    break
        if not valid:
            raise ValueError("Listener must have these arguments: (%s)"
                             % self._kwargs_str())
        self._handlers.append(handler)
        return self

    def invoke(self, *args, **kwargs):
        if args or set(kwargs.keys()) != self._argnames:
            raise ValueError("This Event must be called with these " +
                             "keyword arguments: (%s)" % self._kwargs_str())
        for handler in self._handlers[:]:
            handler(**kwargs)

    def __repr__(self):
        return "EventHook(%s)" % self._kwargs_str()
