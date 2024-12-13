from bin.handler import ping
from bin.handler import login
from bin.handler import rule

urls = (
    ('^/risk_portal/ping$', ping.Ping),
    ('^/risk_portal/v1/user/login$', login.Login),
    ('^/risk_portal/v1/user/logout$', login.Logout),

    # 规则
    ('^/risk_portal/v1/rule/create$', rule.RuleCreate),

    # 规则组
    ('^/risk_portal/v1/rule_group/create$', rule.RuleGroupCreate),
)
