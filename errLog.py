import time


def output_errlog(msg):
    """
    error logging function
    :param msg:
    :return:
    """
    errlogfile = "logs/pydmrError" + time.strftime("-%m.%d.%Y") + ".log"
    with open(errlogfile, "a") as f:
        f.write(msg)
    f.close()
