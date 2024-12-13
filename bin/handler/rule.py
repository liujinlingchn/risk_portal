
import logging
from qfcommon3.qfpay.qfresponse import success
from qfcommon3.web import validator
from bin.handler.base import BaseHandler
from bin.utils.decorator import check
from bin.entity.rule import Rule, RuleGroup
from bin.utils.excepts import ServerError, ParamError
log = logging.getLogger()


class RuleCreate(BaseHandler):

    check_fields = [
        validator.Field("name", validator.T_STR, True, match=r'^\w{1,48}$'),
        validator.Field("description", validator.T_STR, True, match=r'^[\s\S]{0,48}$'),
        validator.Field("salience", validator.T_INT, True),
        validator.Field("status", validator.T_INT, True),
        validator.Field("rule_when", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("rule_then", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("groupid", validator.T_INT, True),
    ]

    @check('login')
    def POST(self):
        self._base_err = self.lang_resp.CREATE_ERROR
        data = self.clean_data()
        rg = RuleGroup.load(data['groupid'])
        if not rg:
            raise ParamError(self.lang_resp.PARAM_ERROR)
        data['op_userid'] = self.userid
        r = Rule(**data)
        ok, resp = r.save()
        if ok:
            return success({})
        else:
            raise ServerError(getattr(self.lang_resp, resp))


class RuleGroupCreate(BaseHandler):

    check_fields = [
        validator.Field("name", validator.T_STR, True, match=r'^\w{1,48}$'),
        validator.Field("description", validator.T_STR, True, match=r'^[\s\S]{0,48}$'),
        validator.Field("salience", validator.T_INT, True),
        validator.Field("status", validator.T_INT, True),
    ]

    @check('login')
    def POST(self):
        self._base_err = self.lang_resp.CREATE_ERROR
        data = self.clean_data()
        data['op_userid'] = self.userid
        rg = RuleGroup(**data)
        # 现在默认全部都是同步执行
        rg.excute_type = 1
        ok, resp = rg.save()
        if ok:
            return success({})
        else:
            raise ServerError(getattr(self.lang_resp, resp))
