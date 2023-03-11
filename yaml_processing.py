import fabric
import ruamel.yaml as yaml
import logging
import copy
import os
import driver_functions_yaml
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


def modify_yaml(src_dict: dict, new_values_dict: dict, file_type: str) -> dict:
    """
    Function creates a modified deep copy of src_dict with values present in the new_values_dict
    Modification is done according to the passed file_type. Every config file of open5gs has different structure
    :param src_dict: dict
    :param new_values_dict: dict
    :param file_type: str
    :return: dict
    """
    diff_dict = copy.deepcopy(src_dict)  # By default, python does a shallow cpy, which results in modifying amf_dict
    for key in new_values_dict:
        diff_dict = driver_functions_yaml.driver_universal_exp(key.split("-"), diff_dict, file_type, new_values_dict[key])

    return diff_dict


def test_amf():
    yaml_data_amf = read_yaml("./transfers/all_open5gs/amf.yaml")
    # AMF testing section
    test_dict_amf = {'sbi-addr': "1.1.1.1", 'sbi-port': 111, 'ngap-addr': "1.1.1.1", 'metrics-addr': "1.1.1.1",
                     'metrics-port': 11, 'guami-plmn_id-mcc': 111, 'guami-plmn_id-mnc': 111, 'guami-amf_id-region': 111,
                     'guami-amf_id-set': 111, 'tai-plmn_id-mcc': 111, 'tai-plmn_id-mnc': 111, 'tai-tac': 111,
                     'plmn_support-plmn_id-mcc': 111, 'plmn_support-plmn_id-mnc': 111, 'plmn_support-s_nssai-sst': 111,
                     'security-integrity_order': [111, 111, 111], 'security-ciphering_order': [111, 111, 111],
                     'network_name-full': "111111", "amf_name": "111111"}
    new_yaml_data = modify_yaml(yaml_data_amf, test_dict_amf, "amf")
    #print(yaml.dump(new_yaml_data_amf))
    write_yaml("./transfers/some_folder/new_amf.yaml", new_yaml_data, overwrite=True)


def test_smf():
    # test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234, 'pfcp-addr': "11.11.11.11", 'gtpc-addr': "11.11.11.11",
    #              'gtpu-addr': "11.11.11.11", 'metrics-addr': "11.11.11.11", 'metrics-port': 1234, 'dns': "11.11.11.11",
    #              'mtu': 1111, 'ctf-enabled': "aaaa", 'freeDiameter': "/etc", 'subnet-addr': "11.11.11.11/11",
    #              'subnet-dnn': "internet"}
    test_dict = {'subnet0-addr': "11.11.11.11/11",
                'subnet0-dnn': "internet",
                 'subnet1-addr': "22.22.22.22/22",
                 'subnet1-dnn': "internet2"
                 }
    yaml_data1 = read_yaml("./transfers/some_folder/new_smf.yaml")
    yaml_data2 = read_yaml("./transfers/all_open5gs/smf.yaml")
    new_yaml_data = modify_yaml(yaml_data2, test_dict, "smf")
    print(yaml_data2['smf']['subnet'][0]['addr'])
    # print(yaml_data1)
    # print(yaml_data2)
    print(yaml.dump(new_yaml_data))
    #write_yaml("./transfers/some_folder/new_smf.yaml", new_yaml_data, overwrite=True)


def test_upf():
    test_dict = {'pfcp0-addr': "11.11.11.11", 'metrics0-addr': "11.11.11.11", 'metrics0-port': 1234,
                 'gtpu0-addr': "11.11.11.11", 'subnet0-addr': "11.11.11.11", 'subnet0-dnn': "internet", 'subnet0-dev': "ogstun"}
    yaml_data = read_yaml("./transfers/all_open5gs/upf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "upf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_upf.yaml", new_yaml_data, overwrite=True)


def main():
    # TODO - Is the lack of ability to rename standalone values in yaml files ok?
    # e.g. BSF.yaml has db_uri value as bsf: db_uri (nested), but also db_uri: (standalone)
    # Currently the way new_value dictionaries are formatted does not allow to modify db_uri standalone if there exists
    # A different version of the same value name nested. Only the nested will be updated
    # If only one exists (only nested or only standalone), there is no issue

    logging.basicConfig(filename="processing_yaml.log", level=logging.INFO)
    logging.info("\n--------------------------------------\n"
                 "Start log {}"
                 "\n--------------------------------------"
                 .format(datetime.now()))
    test_upf()


if __name__ == "__main__":
    main()
