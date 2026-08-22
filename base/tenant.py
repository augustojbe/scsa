import threading

_local = threading.local()


def set_current_brokerage(brokerage):
    _local.brokerage = brokerage


def clear_current_brokerage():
    _local.brokerage = None


def get_current_brokerage():
    return getattr(_local, 'brokerage', None)
