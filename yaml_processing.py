import ruamel.yaml as yaml
import logging
import copy
import os
from datetime import datetime


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


def driver(key: list[str], diff_dict: dict, new_value: int | str) -> dict:
    message = "Could not assign key {}. No match".format(key)
    try:
        if len(key) == 1:
            diff_dict[key[0]] = new_value

        if len(key) == 2:
            diff_dict[key[0]][0][key[1]] = new_value

        elif len(key) == 3:
            # Last char of key[1] is the array index, hence we do slicing to get key name, and key[-1] to get arr index
            if (len(diff_dict[key[0]][key[1][:-1]]) - 1) < int(key[1][-1]):  # To avoid access of bad index
                diff_dict[key[0]][key[1][:-1]].append(dict())
            print("diff_dict[{}][{}][{}][{}]".format(key[0], key[1][:-1], int(key[1][-1]), key[2]))
            diff_dict[key[0]][key[1][:-1]][int(key[1][-1])][key[2]] = new_value

        elif len(key) == 4:
            diff_dict[key[0]][key[1]][0][key[2]][key[3]] = new_value

    except (KeyError, TypeError):
        logging.exception(message)

    return diff_dict


def modify_yaml(src_dict: dict, new_values_dict: dict) -> dict:
    """
    Function creates a modified deep copy of src_dict with values present in the new_values_dict
    Modification is done according to the passed file_type. Config cases checked in driver_universal
    Are limited only to the files that we need to edit, rather than all config files
    :param src_dict: dict
    :param new_values_dict: dict
    :return: dict
    """
    diff_dict = copy.deepcopy(src_dict)  # By default, python does a shallow cpy, which results in modifying amf_dict
    for key in new_values_dict:
        diff_dict = driver(key.split("-"), diff_dict, new_values_dict[key])

    return diff_dict


def test_amf():
    yaml_data = read_yaml("./transfers/all_open5gs/amf.yaml")
    test_dict = {'amf-ngap0-addr': "192.168.0.111", 'amf-guami-plmn_id-mcc': "001", 'amf-guami-plmn_id-mnc': "01",
                 'amf-tai-plmn_id-mcc': "001", 'amf-tai-plmn_id-mnc': "01",
                 'amf-plmn_support-plmn_id-mcc': "001", 'amf-plmn_support-plmn_id-mnc': "01"}
    new_yaml_data = modify_yaml(yaml_data, test_dict)
    print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/amf_realconfig_test.yaml", new_yaml_data, overwrite=True)


def test_smf():
    test_dict = {'smf-pfcp0-addr': "192.168.0.111",
                 'smf-subnet0-addr': "10.45.0.1/16", 'smf-subnet0-dnn': "internet",
                 'smf-subnet1-addr': "10.46.0.1/16", 'smf-subnet1-dnn': "internet2",
                 'smf-subnet2-addr': "10.47.0.1/16", 'smf-subnet2-dnn': "ims",
                 'upf-pfcp0-addr': "192.168.0.112", 'upf-pfcp0-dnn': ["internet", "internet2"],
                 'upf-pfcp1-addr': "192.168.0.113", 'upf-pfcp1-dnn': "ims",
                 }
    yaml_data1 = read_yaml("./transfers/all_open5gs/smf.yaml")
    # Uncomment two lines below for the more advanced version from
    # https://github.com/s5uishida/open5gs_5gc_ueransim_nearby_upf_sample_config#changes-in-configuration-files-of-open5gs-5gc-c-plane
    test_dict.update({'smf-info0-s_nssai': [{"sst": 1, "dnn": ["internet"]}],
                      'smf-info0-tai': [{'plmn_id': {'mcc': '001', 'mnc': '01'}, 'tac': 2}]})
    yaml_data1['smf']['info'] = list()  # Needs to be created manually

    new_yaml_data = modify_yaml(yaml_data1, test_dict)
    print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/smf_realconfig_test.yaml", new_yaml_data, overwrite=True)


def test_upf():
    test_dict = {'upf-pfcp0-addr': "192.168.0.112", 'upf-metrics0-addr': "11.11.11.11", 'upf-metrics0-port': 1234,
                 'upf-gtpu0-addr': "192.168.0.112",
                 'upf-subnet0-addr': "10.45.0.1/16", 'upf-subnet0-dnn': "internet", 'upf-subnet0-dev': "ogstun",
                 'upf-subnet1-addr': "10.46.0.1/16", 'upf-subnet1-dnn': "internet2", 'upf-subnet1-dev': "ogstun2"}
    yaml_data = read_yaml("./transfers/all_open5gs/upf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict)
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/upf_realconfig_test.yaml", new_yaml_data, overwrite=True)


def main():
    logging.basicConfig(filename="processing_yaml.log", level=logging.INFO)
    logging.info("\n--------------------------------------\n"
                 "Start log {}"
                 "\n--------------------------------------"
                 .format(datetime.now()))
    # Testing section open5gs
    # test_amf()
    # test_smf()
    # test_upf()


if __name__ == "__main__":
    main()
