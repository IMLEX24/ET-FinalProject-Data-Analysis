from datetime import datetime

from .logger_config import logger

TIME_STAMPS = dict()
TIME_STAMPS["log_ts"] = (0, 0)


def log_ts(func):
    """utility decorator to log runtime

    Args:
        func : function to run
    """
    global TIME_STAMPS

    def wrapper(*args, **kargs):
        start = datetime.now()
        ret = func(*args, **kargs)
        erapsed_time = (datetime.now() - start).total_seconds()

        fn_name = func.__name__
        t, called = TIME_STAMPS.get(fn_name, (0, 0))
        TIME_STAMPS[fn_name] = (t + erapsed_time, called + 1)

        if erapsed_time > 0.1:
            logger.info(f"{fn_name} took {erapsed_time:.2f} seconds")
        TIME_STAMPS[fn_name] = (
            t + (datetime.now() - start).total_seconds(),
            called + 1,
        )
        return ret

    return wrapper
