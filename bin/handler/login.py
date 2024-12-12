import traceback
import logging

from qfcommon3.qfpay.qfresponse import success
from thriftclient3.apollo.ttypes import UserQuery

from conf import config
from bin.utils.excepts import ParamError

# my
from bin.handler.base import BaseHandler
from bin.utils.decorator import check
from bin.utils import tools
from qfcommon3.qfpay import defines
from qfcommon3.qfpay import apollouser

log = logging.getLogger()


class Login(BaseHandler):
    '''登录'''

    @check()
    def POST(self):
        # 'username', 'password'
        self._base_err = self.lang_resp.LOGIN_ERROR
        values = self.req.inputjson()

        # 加载用户信息
        uq = UserQuery(names=[values['username']])
        userinfos = tools.call_apollo('findUsers', uq)
        if not userinfos or not userinfos[0]:
            raise ParamError(self.lang_resp.LOGIN_ERROR)
        userinfo = userinfos[0]
        log.debug("username=%s|userinfo=%s", values['username'], userinfo)

        if not tools.apo_pass_check(values['username'], values['password']):
            raise ParamError(self.lang_resp.LOGIN_ERROR)

        # 判断用户状态是否合法
        if userinfo.state not in (defines.QF_USTATE_NEW, defines.QF_USTATE_VARIFIED, defines.QF_USTATE_ACTIVE, defines.QF_USTATE_OK):
            pass

        data = {
            'user_cates': [i.code for i in userinfo.userCates],
            'nickname': userinfo.shopname,
            'username': userinfo.username,
            'userid': userinfo.uid,
        }
        ses = apollouser.ApolloSession(expire=config.SESSION_EXPIRE, addr=config.SESSION_SERVERS)
        ses.data.update(data)
        ses.save()

        # 设置保存sessionid 到用户代理
        self.resp.set_cookie('session_id', ses._sesid, **config.COOKIE_CONFIG)

        # 登陆超时设置
        # self.reset_sessionid(ses._sesid)

        data['sessionid'] = ses._sesid

        return success(data)


class Logout(BaseHandler):

    def POST(self):
        try:
            sesid = self.get_cookie('session_id')
            if sesid:
                ses = apollouser.ApolloSession(sesid, addr=config.SESSION_SERVERS)
                ses.logout()
                self.resp.del_cookie('session_id')
                # self.del_sessionid(sesid)
                log.info('userid {}, username {}, sesid {} logout'.format(ses.data.get('userid'), ses.data.get('username'), sesid))
        except:
            log.warn(traceback.format_exc())

        return success({})
