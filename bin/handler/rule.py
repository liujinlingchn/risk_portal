
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
        validator.Field("name", validator.T_STR, True, match=r'^\S{1,48}$'),
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


class RuleInfo(BaseHandler):

    @check('login')
    def GET(self, rule_id):
        r = Rule.load(rule_id)
        if not r:
            raise ParamError(self.lang_resp.PARAM_ERROR)
        return success(r.gen_resp())


class RuleEdit(BaseHandler):

    check_fields = [
        validator.Field("id", validator.T_INT, True),
        validator.Field("name", validator.T_STR, True, match=r'^\S{1,48}$'),
        validator.Field("description", validator.T_STR, True, match=r'^[\s\S]{0,48}$'),
        validator.Field("salience", validator.T_INT, True),
        validator.Field("status", validator.T_INT, True),
        validator.Field("rule_when", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("rule_then", validator.T_STR, True, match=r'^[\s\S]{1,999}$'),
        validator.Field("groupid", validator.T_INT, True),
    ]

    @check('login')
    def POST(self):
        self._base_err = self.lang_resp.EDIT_ERROR
        data = self.clean_data()
        rg = RuleGroup.load(data['groupid'])
        r = Rule.load(data['id'])
        if not rg or not r:
            raise ParamError(self.lang_resp.PARAM_ERROR)

        data['op_userid'] = self.userid
        r.__dict__.update(data)
        ok, resp = r.save()
        if ok:
            return success(r.gen_resp())
        else:
            raise ServerError(getattr(self.lang_resp, resp))


class RuleInfos(BaseHandler):

    check_fields = [
        validator.Field("id", validator.T_INT),
        validator.Field("name", validator.T_STR, False, match=r'^\S{1,48}$'),
        validator.Field("salience", validator.T_INT),
        validator.Field("status", validator.T_INT),
        validator.Field("sctime", validator.T_DATETIME),
        validator.Field("ectime", validator.T_DATETIME),
        validator.Field("page", validator.T_INT, True),
        validator.Field("page_size", validator.T_INT, True),
    ]

    @check('login')
    def GET(self):
        data = self.clean_data()
        where = {}
        if self.check_ctime(data):
            where['ctime'] = ('between', (data['sctime'], data['ectime']))
        data.pop('sctime', None)
        data.pop('ectime', None)
        dstart, dend = self.page_slicing(data)
        where.update(data)
        cnt, value = Rule.batch_load(where, dstart, dend)
        return success({'total': cnt, 'rules': value})


class RuleMigrate(BaseHandler):

    check_fields = [
        validator.Field("rule_id", validator.T_INT, True),
        validator.Field("target_gid", validator.T_INT, True),
    ]

    @check('login')
    def POST(self):
        data = self.clean_data()
        r = Rule.load(data['rule_id'])
        rg = RuleGroup.load(data['target_gid'])
        if not r or not rg:
            raise ParamError(self.lang_resp.PARAM_ERROR)

        if rg.status != RuleGroup.status_valid:
            log.info("target_groupid=%s|status is discard", rg.id)
            raise ParamError(self.lang_resp.PARAM_ERROR)

        r.groupid = data['target_gid']
        ok, resp = r.save()
        if ok:
            return success(r.gen_resp())
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


class RuleGroupInfo(BaseHandler):

    @check('login')
    def GET(self, gid):
        rg = RuleGroup.load(gid)
        if not rg:
            raise ParamError(self.lang_resp.PARAM_ERROR)
        return success(rg.gen_resp())
