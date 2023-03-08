

def driver_amf(key: str, diff_dict: dict, new_value: int | str) -> dict:
    """
    Driver method for the modification of the amf.yaml file.
    Updates a single key in diff_dict
    :param key: str
    :param diff_dict: dict
    :param new_value: int or str
    :return:
    """
    key_split = key.split("-")
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
