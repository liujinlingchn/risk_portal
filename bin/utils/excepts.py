from qfcommon3.qfpay.qfresponse import QFRET


class BaseError(Exception):

    def __init__(self, errmsg='', resperr=None, errcode=QFRET.PARAMERR):
        self.errmsg = errmsg
        self.errcode = getattr(self, 'errcode', errcode)
        self.resperr = resperr or errmsg

    def __str__(self):
        return '[code:%s] errormsg:%s' % (self.errcode, self.errmsg)


class SessionError(BaseError):
    errcode = QFRET.SESSIONERR


class ParamError(BaseError):
    errcode = QFRET.PARAMERR


class ThirdError(BaseError):
    errcode = QFRET.THIRDERR


class DBError(BaseError):
    errcode = QFRET.DBERR


class CacheError(BaseError):
    errcode = QFRET.DATAERR


class ReqError(BaseError):
    errcode = QFRET.REQERR


class UserError(BaseError):
    errcode = QFRET.USERERR


class ServerError(BaseError):
    errcode = QFRET.SERVERERR


class NoData(BaseError):
    errcode = QFRET.NODATA


class IoError(BaseError):
    errcode = QFRET.IOERR
