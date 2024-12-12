import os
from webconfig import *
# from qfcommon3.qfpay import dbenc

# 服务地址
HOST = '0.0.0.0'
# 服务端口
PORT = 7990
# 调试模式: 生产环境必须为False
DEBUG = False
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 日志文件配置
LOGFILE = {
    'root': {
        'filename': {
            'DEBUG': os.path.join(HOME, '../log/0.risk_portal.log'),
            'ERROR': os.path.join(HOME, '../log/0.risk_portal.error.log'),
        }
    }
}
LOGFILE = None
LOGWHEN = 'midnight'
SESSION_EXPIRE = 60 * 60 * 24 * 30
COOKIE_CONFIG = {
    'max_age': 86400,
    'domain': None,
}

'''
dbconf = dbenc.DBConf()
DATABASE = {
    'qf_risk_3': dbconf.get_dbpool('qf_risk_3', engine='pymysql', conn=50),
}
'''
DATABASE = {
    'qf_risk_3': {
        'engine': 'pymysql',
        'db': 'qf_risk_3',
        'host': '172.100.101.109',
        'port': 3306,
        'user': 'qfpay',
        'passwd': 'devENV@2022@@',
        'charset': 'utf8',
        'idle_timeout': 60,
        'conn': 50}
}
REDIS_CONF = {
    'host': 'redis',
    'port': 6379,
    'password': '',
    'db': 9,
}
APOLLO_SERVERS = [{'addr': ('apollo', 6700), 'timeout': 10000}]
SESSION_SERVERS = [{'addr': ('session', 4700), 'timeout': 2000}]
