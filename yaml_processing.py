import ruamel.yaml as yaml
import logging
import copy


def read_yaml(file_path: str) -> dict:
    """
    Reads a yaml file specified in the file_path
    :param file_path: str
    :return: dict
    """
    with open(file_path, 'r') as text:
        try:
            yaml_parsed = yaml.safe_load(text)
        except yaml.YAMLError as e:
            logging.exception("Unable to process yaml stream:\n {}".format(e))
            return {}
        # print(yaml.dump(yaml_parsed))
    return yaml_parsed


def modify_amf(amf_dict: dict, new_values_dict: dict) -> dict:
    """
    Method modifies the amf.yaml file and returns a new modified amf.yaml dict.
    It is important for the new_values_dict to be of format separated with hyphens
    That is e.g. to modify amf: sbi: addr:, key in new_values dict should be amf-sbi-addr
    The amount of if statemets is due to nonunified way the amf.yaml file is designed
    Lists are present "sometimes" and at different levels (notice the [0] when referencing value in diff_dict)
    :param amf_dict: dict
    :param new_values_dict: dict
    :return: dict
    """
    diff_dict = copy.deepcopy(amf_dict)  # By default, python does a shallow cpy, which results in modifying amf_dict
    for key in new_values_dict:
        try:
            # print("Current key is {}".format(key))
            key_split = key.split("-")
            # TODO - Optimise below if statements (if possible)
            if len(key_split) == 1:  # for amf_name
                diff_dict['amf'][key_split[0]] = new_values_dict[key]

            elif len(key_split) == 2:  # For sbi, ngap and metrics
                if key_split[0] in ("security", "network_name"):  # For security, network name
                    diff_dict['amf'][key_split[0]][key_split[1]] = new_values_dict[key]
                else:
                    diff_dict['amf'][key_split[0]][0][key_split[1]] = new_values_dict[key]

            elif len(key_split) == 3:  # For guami, tai, plmn_support
                if key_split[1] == 's_nssai':  # Special case. It's not formatted as other
                    diff_dict['amf'][key_split[0]][0][key_split[1]][0][key_split[2]] = new_values_dict[key]
                else:
                    diff_dict['amf'][key_split[0]][0][key_split[1]][key_split[2]] = new_values_dict[key]
        except KeyError:
            # print("KeyError caught for {}".format(key))
            logging.exception("Key {} was not found in amf.yaml, but was passed in new_values dict".format(key))

    return diff_dict


def main():
    logging.basicConfig(filename="yaml_processing.log", level=logging.INFO)
    yaml_data = read_yaml("./transfers/some_folder/amf.yaml")
    # Dictionary for testing if all modifications work. Last testing was OK!
    test_dict = {'sbi-addr': "1.1.1.1", 'sbi-port': 1111, 'ngap-addr': "1.1.1.1", 'metrics-addr': "1.1.1.1",
                 'metrics-port': 1111, 'guami-plmn_id-mcc': 111, 'guami-plmn_id-mnc': 111, 'guami-amf_id-region': 111,
                 'guami-amf_id-set': 111, 'tai-plmn_id-mcc': 111, 'tai-plmn_id-mnc': 111, 'tai-tac': 111,
                 'plmn_support-plmn_id-mcc': 111, 'plmn_support-plmn_id-mnc': 111, 'plmn_support-s_nssai-sst': 111,
                 'security-integrity_order': [111, 111, 111], 'security-ciphering_order': [111, 111, 111],
                 'network_name-full': "111111", "amf_name": "111111"}
    new_yaml_data = modify_amf(yaml_data, test_dict)
    print(yaml.dump(new_yaml_data))

    with open('./transfers/some_folder/new_amf.yaml', 'w') as output:
        # Output compared with https://www.yamldiff.com/ - It is semantically the same
        yaml.dump(new_yaml_data, output, default_flow_style=False)


if __name__ == "__main__":
    main()
