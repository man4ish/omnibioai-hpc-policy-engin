def validate_gpu_access(roles: list, gpus: int):

    if gpus <= 0:
        return True, "no gpu needed"

    if "gpu_user" not in roles:
        return False, "gpu access denied"

    return True, "gpu allowed"