def success(data=None, msg="success"):
    return {"code": 200, "msg": msg, "data": data}


def error(msg="error", code=500):
    return {"code": code, "msg": msg, "data": None}
