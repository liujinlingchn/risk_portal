import logging

from bin import globalization

from bin.utils.excepts import ParamError
from bin.utils.runtime import redis_pool
from conf import config

from qfcommon3.base.dbpool import get_connection_exception
from qfcommon3.web.core import Handler
from qfcommon3.web.httpcore import ChunkedResponse
from qfcommon3.web import validator


langs = globalization.LANGS
log = logging.getLogger()


class BaseHandler(Handler):

    def initial(self):
        self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})
        log.debug("lang : %s", self.req.environ.get('HTTP_LANG'))
        self.lang_all = self.req.environ.get('HTTP_LANG')
        if not self.lang_all:
            self.lang_all = self.req.input().get('lang', 'zh-cn')
        # zh-cn 中文，英文 en-us
        self.lang = self.lang_all.split('-')[0]
        self.langconf = langs[self.lang]
        self.lang_resp = self.langconf.RESPMSG

    def check_cate(self, cate=[], userid=None):
        raise NotImplementedError("NotImplemented")

    def get_perms(self, userid=None, reload=False):
        raise NotImplementedError("NotImplemented")

    def check_perms(self, perm_codes, userid=None):
        if not perm_codes:
            return True

        for flag in (False, True):
            user_perms = self.get_perms(userid, flag)
            if set(perm_codes) & set(user_perms):
                return True

        return False

    def clean_data(self):
        data = self.req.inputjson()
        v = validator.Validator(self.check_fields)
        err = v.verify(data)
        if err:
            log.debug("check params error(%s)", err)
            raise ParamError(self.lang_resp.PARAM_ERROR)
        return v.data

    def is_valid_sessionid(self, sessionid):
        '''判断sessionid在应用有效

        登录指定时间以后自动失效

        params:
            sessionid(str): sessionid
        return:
            ret(bool): 是否失效

        '''

        sessionid_redis_key = '_risk_portal_{}_'.format(sessionid)

        ret = redis_pool.get(sessionid_redis_key)
        return False if not ret else True

    def reset_sessionid(self, sessionid):
        '''重置sessionid的应用有效状态'''

        sessionid_redis_key = '_risk_portal_{}_'.format(sessionid)

        # 默认的时间是cookie的有效期
        redis_pool.set(sessionid_redis_key, '1', config.SESSION_EXPIRE)

    def del_sessionid(self, sessionid):
        sessionid_redis_key = '_risk_portal_{}_'.format(sessionid)
        redis_pool.delete(sessionid_redis_key)

    def get_org_uid(self, userid=None):
        '''获取商户机构uid'''
        if not userid:
            try:
                return self.user.ses.data['groupid']
            except:
                pass

        admin = None
        with get_connection_exception('qf_org') as db:
            userid = userid or self.user.userid
            admin = db.select_one(
                'org_admin', where={'userid': userid},
                fields='qd_uid'
            )

        if not admin:
            raise ParamError('org不存在')

        try:
            self.user.ses['org_uid'] = admin['qd_uid']
        except:
            pass

        return admin['qd_uid']


def get_qd_of_org(org_uid):
    ret = []

    if not org_uid:
        return ret

    with get_connection_exception('qf_org') as db:
        one = []
        one = db.select(
            table='qd_user',
            fields='qd_uid',
            where={'level': 2, 'parent': org_uid, 'status': 0},
        )
        one_uids = [i['qd_uid'] for i in one]
        if not one_uids:
            return ret

        two = []
        two = db.select(
            table='qd_user',
            fields='qd_uid',
            where={'level': 3, 'parent': ('in', one_uids), 'status': 0},
        )
        two_uids = [i['qd_uid'] for i in two]
        one_uids.extend(two_uids)
        ret = one_uids
    return ret


class BaseChunkedHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        super(BaseChunkedHandler, self).__init__(*args, **kwargs)
        self.resp = ChunkedResponse()

    def set_callback(self, func):
        self.resp.set_callback(func)
