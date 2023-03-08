import ruamel.yaml as yaml


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


def modify_amf(amf_dict: dict, new_values_dict: dict):
    # Function for testing. Not final!
    # sbi
    diff_dict = amf_dict
    diff_dict['amf']['sbi'][0]['addr'] = new_values_dict['sbi_addr']
    return diff_dict


def main():
    yaml_data = read_yaml("./transfers/some_folder/amf.yaml")
    yaml_data = modify_amf(yaml_data, {'sbi_addr': 1234})
    print(yaml.dump(yaml_data))


if __name__ == "__main__":
    main()
