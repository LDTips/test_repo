# personal note:
# this whole module most likely could be optimised, as there are repeating patters.
# TODO - if I have too much time, optimise all of these methods

def driver_amf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the amf.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
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
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
    """
    diff_dict['ausf'][key_split[0]][0][key_split[1]] = new_value
    return diff_dict


def driver_bsf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the bsf.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
    """
    if key_split[0] == 'db_uri':
        diff_dict[key_split[0]] = new_value
    else:
        diff_dict['bsf'][key_split[0]][0][key_split[1]] = new_value
    return diff_dict


def driver_hss(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the hss.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
    """
    if key_split[0] == "db_uri":
        diff_dict[key_split[0]] = new_value
    else:
        diff_dict['hss'][key_split[0]] = new_value
    return diff_dict


def driver_mme(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the mme.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
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


def driver_nrf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the nrf.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
    """
    if key_split[1] == 'addr':  # len(key_split) == 3
        if key_split[2] == '4':  # addr-4 means to modify ipv4 version of addr (found at index 0)
            diff_dict['nrf'][key_split[0]][0][key_split[1]][0] = new_value
        elif key_split[2] == '6':  # addr-6 means to modify ipv4 version of addr (found at index 1)
            diff_dict['nrf'][key_split[0]][0][key_split[1]][1] = new_value
        else:
            raise KeyError
    else:  # port, len(key_split) == 2
        diff_dict['nrf'][key_split[0]][0][key_split[1]] = new_value

    return diff_dict


def driver_nssf(key_split: list[str], diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the nssf.yaml file.
    Assigns new_value to a specified key (key_split) in diff_dict
    :param key_split: list[str]
    :param diff_dict: dict
    :param new_value: int or str
    :return: dict
    """
    if len(key_split) == 2:
        diff_dict['nssf'][key_split[0]][0][key_split[1]] = new_value
    else:  # len(key_split) == 3
        diff_dict['nssf'][key_split[0]][0][key_split[1]][key_split[2]] = new_value

    return diff_dict