

def driver_amf(key_split: str, diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the amf.yaml file.
    Updates a single key in diff_dict
    :param key_split: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    # TODO - Optimise below if statements (if possible)
    if len(key_split) == 1:  # for amf_name
        diff_dict['amf'][key_split[0]] = new_value

    elif len(key_split) == 2:  # For sbi, ngap and metrics
        if key_split[0] in ("security", "network_name"):  # For security, network name
            diff_dict['amf'][key_split[0]][key_split[1]] = new_value
        else:
            diff_dict['amf'][key_split[0]][0][key_split[1]] = new_value

    elif len(key_split) == 3:  # For guami, tai, plmn_support
        if key_split[1] == 's_nssai':  # Special case. It's not formatted as other
            diff_dict['amf'][key_split[0]][0][key_split[1]][0][key_split[2]] = new_value
        else:
            diff_dict['amf'][key_split[0]][0][key_split[1]][key_split[2]] = new_value

    return diff_dict


def driver_ausf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the ausf.yaml file.
    Updates a single key in diff_dict
    :param key_split: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    diff_dict['ausf'][key_split[0]][0][key_split[1]] = new_value
    return diff_dict


def driver_bsf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the ausf.yaml file.
    Updates a single key in diff_dict
    :param key_split: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    if key_split[0] == 'db_uri':
        diff_dict[key_split[0]] = new_value
    else:
        diff_dict['bsf'][key_split[0]][0][key_split[1]] = new_value
    return diff_dict


def driver_hss(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the hss.yaml file.
    Updates a single key in diff_dict
    :param key_split: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    if key_split[0] == "db_uri":
        diff_dict[key_split[0]] = new_value
    else:
        diff_dict['hss'][key_split[0]] = new_value
    return diff_dict


def driver_mme(key_split: str, diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the mme.yaml file.
    Updates a single key in diff_dict
    :param key_split: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    # TODO - Optimise below if statements (if possible)
    if len(key_split) == 1:  # for mme_name
        diff_dict['mme'][key_split[0]] = new_value

    elif len(key_split) == 2:
        if key_split[0] in ("s1ap", "gtpc", "metrics"):  # For s1ap, gtpc and metrics
            diff_dict['mme'][key_split[0]][0][key_split[1]] = new_value
        else:  # For security, network name, gummei-mme_gid/mme_code, tai-tac
            diff_dict['mme'][key_split[0]][key_split[1]] = new_value

    elif len(key_split) == 3:  # For gummei, tai
        diff_dict['mme'][key_split[0]][key_split[1]][key_split[2]] = new_value

    return diff_dict
