# coding: utf-8

import traceback
import logging

from bin.utils.excepts import BaseError, SessionError
from conf import config

from qfcommon3.qfpay.apollouser import ApolloUser
from qfcommon3.qfpay.qfresponse import QFRET, error

log = logging.getLogger()

# 数据函数dict
data_funcs = {}


def func_register(mode='valid'):
    '''注册接口'''
    def _(func):
        if mode == 'valid':
            data_funcs[func.__name__] = func
        return func
    return _


@func_register()
def login(func):
    def _(self, *args, **kw):
        # 验证登陆
        sessionid = self.get_cookie('session_id')
        self.user = ApolloUser(sessionid=sessionid, addr=config.SESSION_SERVERS)
        if not self.user.is_login():
            log.info('user not login')
            raise SessionError(self.langconf.RESPMSG.USER_NOT_LOGIN)

        # 验证登陆是否有效
        '''
        if not self.is_valid_sessionid(sessionid):
            self.user.logout()
            self.resp.del_cookie('sessionid')
            log.info('session timeout')
            raise SessionError(self.langconf.RESPMSG.USER_TIMEOUT)
        self.reset_sessionid(sessionid)
        '''

        # 加载部分信息到handler 实例
        # self.role = self.user.ses['role']
        # self.org_uid = self.user.ses['org_uid']
        # self.sessionid = sessionid
        self.userid = int(self.user.ses['userid'])

        ret = func(self, *args, **kw)

        if self.user.ses.data:
            self.user.ses.save()
        return ret
    return _


@func_register()
def cate_perm(func):
    '''验证用户角色和权限'''
    def _(self, *args, **kw):
        # 用户角色验证
        if not self.check_cate():
            raise SessionError(self.langconf.RESPMSG.WRONG_USER_CATE)

        # 用户权限验证
        perm_codes = getattr(self, '_perm_codes', None)
        if isinstance(perm_codes, str):
            perm_codes = [perm_codes]

        if not self.check_perms(perm_codes):
            raise SessionError(self.langconf.RESPMSG.USER_HAS_NO_PERMISSION)

        ret = func(self, *args, **kw)

        return ret
    return _


def check(funcs=None):
    def _(func):
        def __(self, *args, **kwargs):
            try:
                del_func = func
                deco_funcs = []
                if funcs:
                    deco_funcs = (
                        funcs if isinstance(funcs, (list, tuple)) else [funcs]
                    )
                for f in deco_funcs[::-1]:
                    if callable(f):
                        del_func = del_func(f)
                    elif f in data_funcs:
                        del_func = data_funcs[f](del_func)
                return del_func(self, *args, **kwargs)
            except BaseError as e:
                log.warn(traceback.format_exc())
                errcode, errinfo = e.errcode, e.errmsg
            except:
                log.warn(traceback.format_exc())
                errinfo = getattr(self, '_base_err', 'param error')
                errcode = QFRET.PARAMERR

            return error(errcode, errinfo, errinfo)

        return __
    return _


def raise_excp(info='param error'):
    def _(func):
        def __(self, *args, **kwargs):
            try:
                # 错误信息
                module_name = getattr(self, '__module__', '')
                class_name = getattr(getattr(self, '__class__', ''), '__name__', '')
                func_name = getattr(func, '__name__', '')
                errinfo = '%s %s %s' % (module_name, class_name, func_name)

                return func(self, *args, **kwargs)
            except BaseError as e:
                log.warn('[%s] error: %s' % (errinfo, e))
                return self.write(error(e.errcode, respmsg=e.errmsg))
            except:
                log.warn('[%s] error:%s' % (errinfo, traceback.format_exc()))
                return self.write(error(QFRET.PARAMERR, respmsg=info))

        return __

    return _
