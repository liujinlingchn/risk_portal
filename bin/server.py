import os
import sys
from gevent import monkey
HOME = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(HOME))
monkey.patch_all()

from qfcommon3.base import logger, loader
if __name__ == '__main__':
    loader.loadconf_argv(HOME)
else:
    loader.loadconf(HOME)

import config
import urls

if 'QFNAME' in os.environ:
    config.QFNAME = os.environ['QFNAME']

# 导入服务日志
if config.LOGFILE:
    log = logger.install(config.LOGFILE, when=config.LOGWHEN)
else:
    log = logger.install('stdout')

from qfcommon3.web import core
from qfcommon3.web import runner


# 导入WEB URLS
config.URLS = urls

app = core.WebApplication(config)

if __name__ == '__main__':
    # 导入自定义服务端口
    if len(sys.argv) > 2:
        config.PORT = int(sys.argv[2])
    runner.run_simple(app, host=config.HOST, port=config.PORT)
