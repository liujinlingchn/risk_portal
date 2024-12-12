
import logging
from qfcommon3.qfpay.qfresponse import success
from qfcommon3.web import validator
from bin.handler.base import BaseHandler
from bin.utils.decorator import check
log = logging.getLogger()


class RuleCreate(BaseHandler):

    check_fields = [
        validator.Field("name", validator.T_STR, True, match=r'^\w{1,48}$'),
        validator.Field("description", validator.T_STR, True, match=r'^\w{0,48}$'),
        validator.Field("salience", validator.T_INT, True),
        validator.Field("status", validator.T_INT, True),
        validator.Field("rule_when", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("rule_then", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("groupid", validator.T_STR, True, match=r'^\d{1,999}$'),
        validator.Field("group_name", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
    ]

    @check('login')
    def POST(self):
        # NOTE _base_err
        self._base_err = self.lang_resp.LOGIN_ERROR
        data = self.clean_data()
        return success(data)
