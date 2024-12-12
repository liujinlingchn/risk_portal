import logging
import datetime
from qfcommon3.base import dbpool
from bin.utils.tools import create_id
log = logging.getLogger()


class Rule(object):
    def __init__(self, name, description, salience, status, rule_when, rule_then, groupid, op_userid):
        self.name = name
        self.description = description
        self.salience = salience
        self.status = status
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
    
    @classmethod
    def load(cls, rule_id):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            record = conn.select_one('rules', where={'id': rule_id})
            if not record:
                return None
            return cls._build_by_record(record)

    def save(self):
        with dbpool.get_connection_exception('qf_risk_3') as conn:
            if self.id is None and self.ctime is None:
                self.id = create_id()
                self.ctime = datetime.datetime.now()
                affected_lines = conn.insert('rules', self.__dict__)
            else:
                self.utime = datetime.datetime.now()
                affected_lines = conn.update('rules', self.__dict__, where={'id': self.id})
            if affected_lines != 1:
                log.info('save rule failed: affected_lines=%s', affected_lines)
                return False
            return True