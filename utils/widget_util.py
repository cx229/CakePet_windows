from contextlib import contextmanager

@contextmanager
def signal_blocker(widget):
    """上下文管理器：临时阻塞信号"""
    widget.blockSignals(True)
    try:
        yield
    finally:
        widget.blockSignals(False)