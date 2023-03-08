import ruamel.yaml as yaml
import logging
import copy
import os
import typing
import driver_functions_yaml


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


def write_yaml(file_path: str, yaml_data: dict, *, overwrite: bool = False) -> None:
    """
    Writes yaml_data to the provided file in file_path.
    If overwrite flag is set, the destination file will be overwritten with the passed yaml_data
    If overwrite flag is not set and the file exists, FileExistsError is raised and yaml_data is not written
    Otherwise, overwrite flag has no effect
    :param file_path: str
    :param yaml_data: dict
    :param overwrite: bool
    :return: None
    """
    try:
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError("Overwrite file was not set, but file {} exists!".format(file_path))
        with open(file_path, 'w') as output:
            # Output compared with https://www.yamldiff.com/ - It is semantically the same
            yaml.dump(yaml_data, output, default_flow_style=False)
    except FileExistsError as e:
        logging.exception(e)


def modify_yaml(src_dict: dict, new_values_dict: dict) -> dict:
    """
    Function modifies specified src_dict with values present in the new_values_dict
    Using specified driver_function. Every yaml configuration file has different datastructure
    Hence different driver functions should be used for different yaml files
    :param src_dict: dict
    :param new_values_dict: dict
    :return: dict
    """
    # TODO - Determine how to get the config file name from the src_dict
    method_name = "driver_" + "amf"
    function = getattr(driver_functions_yaml, method_name)  # Raises AttributeError if function does not exist
    diff_dict = copy.deepcopy(src_dict)  # By default, python does a shallow cpy, which results in modifying amf_dict
    for key in new_values_dict:
        try:
            diff_dict = function(key, diff_dict, new_values_dict[key])
        except KeyError:
            # print("KeyError caught for {}".format(key))
            logging.exception("Key {} was not found in amf.yaml, but was passed in new_values dict".format(key))

    return diff_dict


def main():
    logging.basicConfig(filename="processing_yaml.log", level=logging.INFO)
    yaml_data_amf = read_yaml("./transfers/some_folder/amf.yaml")
    # AMF testing section
    test_dict_amf = {'sbi-addr': "1.1.1.1", 'sbi-port': 111, 'ngap-addr': "1.1.1.1", 'metrics-addr': "1.1.1.1",
                     'metrics-port': 11, 'guami-plmn_id-mcc': 111, 'guami-plmn_id-mnc': 111, 'guami-amf_id-region': 111,
                     'guami-amf_id-set': 111, 'tai-plmn_id-mcc': 111, 'tai-plmn_id-mnc': 111, 'tai-tac': 111,
                     'plmn_support-plmn_id-mcc': 111, 'plmn_support-plmn_id-mnc': 111, 'plmn_support-s_nssai-sst': 111,
                     'security-integrity_order': [111, 111, 111], 'security-ciphering_order': [111, 111, 111],
                     'network_name-full': "111111", "amf_name": "111111"}
    new_yaml_data_amf = modify_yaml(yaml_data_amf, test_dict_amf)
    print(yaml.dump(new_yaml_data_amf))
    write_yaml("./transfers/some_folder/new_amf.yaml", new_yaml_data_amf, overwrite=False)

    # UPF testing section
    #yaml_data_upf = read_yaml("./transfers/some_folder/upf.yaml")
    #print(yaml_data_upf['upf']['subnet'])
    #print(yaml.dump(yaml_data_upf))


if __name__ == "__main__":
    main()
