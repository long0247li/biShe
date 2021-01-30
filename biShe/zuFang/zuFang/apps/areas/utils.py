import logging

from django.http import JsonResponse

# 创建日志记录器：导入创建日志器才能使用
logger = logging.getLogger('django')

ERR_LIST = {
    4001: "DBERR 数据库查询错误",
    4002: "NODATA 无数据",
    4003: "DATAEXIST 数据已存在",
    4004: "DATAERR 数据错误",
    4101: "SESSIONERR 用户未登录",
    4102: "LOGINERR 用户登录失败",
    4103: "PARAMERR 参数错误",
    4104: "USERERR 用户不存在或未激活",
    4105: "ROLEERR 用户身份错误",
    4106: "PWDERR 密码错误",
    4201: "REQERR 非法请求或请求次数受限",
    4202: "IPERR IP受限",
    4301: "THIRDERR 第三方系统错误",
    4302: "IOERR 文件读写错误",
    4500: "SERVERERR 内部错误",
    4501: "UNKOWNERR 未知错误",
}


# 打印错误
def return_err(code, e=None, s=''):
    logger.error(e)
    return JsonResponse({
        'errno': code,
        'errmsg': ERR_LIST.get(code) + s,
    })
