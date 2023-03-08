import ruamel.yaml as yaml
import logging

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
            print("Error while processing the file. Reason: ")
            print(e)
            return {}
        # print(yaml.dump(yaml_parsed))
    return yaml_parsed


def modify_amf(amf_dict: dict, new_values_dict: dict) -> dict:
    """
    Method modifies the amf.yaml file.
    It is important for the new_values_dict to be of format separated with hyphens
    That is e.g. to modify amf: sbi: addr:, key in new_values dict should be amf-sbi-addr
    :param amf_dict: dict
    :param new_values_dict: dict
    :return: dict
    """
    # TODO - Test the whole function
    diff_dict = amf_dict.copy()
    for key in new_values_dict:
        try:
            key_split = key.split("-")
            # TODO - Optimise below if statements (if possible)
            if len(key_split) == 2:  # For sbi, ngap and metrics
                diff_dict['amf'][key_split[0]][0][key_split[1]] = new_values_dict[key]
            elif len(key_split) == 3:
                if key_split[1] == 's_nssai':  # Special case. It's not formatted as other
                    diff_dict['amf'][key_split[0]][0][key_split[1]][0][key_split[2]] = new_values_dict[key]
                else:
                    diff_dict['amf'][key_split[0]][0][key_split[1]][key_split[2]] = new_values_dict[key]
        except KeyError:
            logging.exception("Key {} was not found in amf.yaml, but was passed in new_values dict".format(key))

    # print(diff_dict['amf']['guami'][0]['amf_id']['region'])
    # diff_dict['amf']['sbi'][0]['addr'] = new_values_dict['sbi_addr']
    return diff_dict


def main():
    logging.basicConfig(filename="yaml_processing.log", level=logging.INFO)
    yaml_data = read_yaml("./open5gs_default_configs/amf.yaml")
    new_yaml_data = modify_amf(yaml_data, {'plmn_support-s_nssai-sst': 1234, 'sbi-addr': '53.123.123.123'})
    print(yaml.dump(yaml_data))
    #print(yaml.dump(new_yaml_data))
    # print(yaml_data['amf']['plmn_support'][0]['s_nssai'][0]['sst'])


if __name__ == "__main__":
    main()
