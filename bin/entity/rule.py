import logging
import datetime
# from pymysql.err import IntegrityError
from qfcommon3.base import dbpool
from bin.utils.tools import create_id
# from bin.utils.excepts import DBError
log = logging.getLogger()


def check_salience(salience):
    if not 1 <= int(salience) <= 1000:
        log.debug("check salience fail")
        return False
    return True


def check_status(status, status_list):
    if int(status) not in status_list:
        log.debug("check status fail")
        return False
    return True


class Rule(object):
    status_created = 1
    status_checked = 2
    status_published = 3
    status_check_fail = 4
    status_offline = 5
    status_map = {
        status_created: "未校验",
        status_checked: "已校验",
        status_published: "已发布",
        status_check_fail: "检查失败",
        status_offline: "已下线"
    }

    def __init__(self, name, description, salience, status, rule_when, rule_then, groupid, op_userid):
        self.name = name
        self.description = description
        self.salience = salience
        self.status = status
        # when then str
        self.rule_when = rule_when
        self.rule_then = rule_then
        self.groupid = groupid
        self.op_userid = op_userid
        self.id = None
        self.ctime = None
        self.utime = None

    @classmethod
    def _build_by_record(cls, record):
        rule = cls(
            name=record['name'],
            description=record['description'],
            salience=record['salience'],
            status=record['status'],
            rule_when=record['rule_when'],
            rule_then=record['rule_then'],
            groupid=record['groupid'],
            op_userid=record['op_userid'])
        rule.id = record['id']
        rule.ctime = record['ctime']
        rule.utime = record['utime']
        return rule

    def gen_resp(self):
        resp = self.__dict__.copy()
        resp['id'] = str(resp['id'])
        for k in ('utime', ):
            resp.pop(k)
        resp['status_desc'] = self.status_map[resp['status']]
        rg = RuleGroup.load(resp['groupid'])
        resp['groupid'] = str(resp['groupid'])
        resp['groupid_name'] = rg.name
        return resp

    @staticmethod
    def batch_load(where, start, end):
        other = "order by ctime desc"
        if end:
            other = "order by ctime desc limit %d,%d" % (start, end)

        cnt = 0
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one('rules', fields="count(*) as total", where=where)
            cnt = record['total']

        with dbpool.get_connection_exception('qf_risk_3') as conn:
            records = conn.select('rules', where=where, other=other)
            if records:
                return cnt, [Rule._build_by_record(record).gen_resp() for record in records]
            else:
                return cnt, []

    @classmethod
    def load(cls, rule_id):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one('rules', where={'id': rule_id})
            if record:
                return cls._build_by_record(record)
            return None

    def _check_unique(self):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one("rules", where={"name": self.name})
            if record:
                return True
            return False

    def _create(self):
        if self._check_unique():
            log.info("func=create rule|name=%s has existed in db", self.name)
            return False, "DUPLICATE_DATA"

        self.id = create_id()
        self.utime = self.ctime = datetime.datetime.now()
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            affected_lines = conn.insert('rules', self.__dict__)
            if affected_lines != 1:
                log.info('save rules failed: affected_lines=%s', affected_lines)
                return False, "CREATE_ERROR"
            return True, None

    def _update(self):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            self.utime = datetime.datetime.now()
            affected_lines = conn.update('rules', self.__dict__, where={'id': self.id})
            if affected_lines != 1:
                log.info('save rules failed: affected_lines=%s', affected_lines)
                return False, "EDIT_ERROR"
            return True, None

    def save(self):
        if not check_salience(self.salience):
            return False, "PARAM_ERROR"
        if not check_status(self.status, list(self.status_map.keys())):
            return False, "PARAM_ERROR"

        if self.id is None and self.ctime is None:
            return self._create()
        else:
            return self._update()


class RuleGroup(object):
    status_valid = 1
    status_discard = 2
    status_map = {
        status_valid: "有效",
        status_discard: "废弃"
    }

    def __init__(self, name, description, salience, status, op_userid):
        self.name = name
        self.description = description
        self.salience = salience
        self.status = status
        self.op_userid = op_userid
        self.id = None
        self.ctime = None
        self.utime = None
        self.checksum = None
        self.excute_type = None

    @classmethod
    def _build_by_record(cls, record):
        grule = cls(
            name=record['name'],
            description=record['description'],
            salience=record['salience'],
            status=record['status'],
            op_userid=record['op_userid'])
        grule.id = record['id']
        grule.ctime = record['ctime']
        grule.utime = record['utime']
        grule.checksum = record['checksum']
        return grule

    @classmethod
    def load(cls, grule_id):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one('rule_group', where={'id': grule_id})
            if record:
                return cls._build_by_record(record)
            return None

    def _check_unique(self):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one("rule_group", where={"name": self.name})
            if record:
                return True
            return False

    def _update(self):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            self.utime = datetime.datetime.now()
            affected_lines = conn.update('rule_group', self.__dict__, where={'id': self.id})
            if affected_lines != 1:
                log.info('save rule_group failed: affected_lines=%s', affected_lines)
                return False, "EDIT_ERROR"
            return True, None

    def _create(self):
        if self._check_unique():
            log.info("func=create rule_group|name=%s has existed in db", self.name)
            return False, "DUPLICATE_DATA"

        self.id = create_id()
        self.utime = self.ctime = datetime.datetime.now()
        self.checksum = ''
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            affected_lines = conn.insert('rule_group', self.__dict__)
            if affected_lines != 1:
                log.info('save rule_group failed: affected_lines=%s', affected_lines)
                return False, "CREATE_ERROR"
            return True, None

    def save(self):
        if not check_salience(self.salience):
            return False, "PARAM_ERROR"
        if not check_status(self.status, list(self.status_map.keys())):
            return False, "PARAM_ERROR"

        if self.id is None and self.ctime is None:
            return self._create()
        else:
            return self._update()

    def gen_resp(self):
        resp = self.__dict__.copy()
        resp['id'] = str(resp['id'])
        for k in ('utime', 'excute_type', 'checksum'):
            resp.pop(k)
        resp['status_desc'] = self.status_map[resp['status']]
        return resp
