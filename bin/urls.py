from bin.handler import ping
from bin.handler import login
from bin.handler import rule

urls = (
    ('^/risk_portal/ping$', ping.Ping),
    ('^/risk_portal/v1/user/login$', login.Login),
    ('^/risk_portal/v1/user/logout$', login.Logout),

    # 规则
    ('^/risk_portal/v1/rule/create$', rule.RuleCreate),
    ('^/risk_portal/v1/rule/(?P<rule_id>\d+)$', rule.RuleInfo),
    ('^/risk_portal/v1/rule/edit$', rule.RuleEdit),
    ('^/risk_portal/v1/rules$', rule.RuleInfos),
    ('^/risk_portal/v1/rule/migrate$', rule.RuleMigrate),

    # 规则组
    ('^/risk_portal/v1/rule_group/create$', rule.RuleGroupCreate),
)
