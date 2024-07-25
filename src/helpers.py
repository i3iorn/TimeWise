import inspect


def get_app():
    frame = inspect.currentframe()
    while frame is not None:
        frame = frame.f_back
        if "f_locals" not in frame.__dir__() or "self" not in frame.f_locals:
            continue
        if frame.f_locals["self"].__class__.__name__ == "TimeWise":
            break

    return frame.f_locals.get('self', None) if frame is not None else None
