import logging
import traceback
from qfcommon3.server.client import ThriftClient
from thriftclient3.apollo import ApolloServer
from thriftclient3.apollo.ttypes import ApolloException
from thriftclient3.spring import Spring
from conf import config
log = logging.getLogger()


def call_apollo(func, *args, **kw):
    apcli = ThriftClient(config.APOLLO_SERVERS, ApolloServer, raise_except=True)
    return apcli.call(func, *args, **kw)


def apo_pass_check(username, password):
    # 用户是否存在和校验密码
    try:
        return call_apollo('checkUsername', username, password)
    except ApolloException:
        # 1007, 1008
        return None
    except:
        log.warn(traceback.format_exc())
        return None


def create_id():
    return ThriftClient(config.SPRING_FRAMED, Spring, framed=True, raise_except=True).getid()
