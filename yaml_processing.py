import yaml


def foo(yaml_parsed: dict) -> None:
    """
    Test function please ignore
    :return: None
    """
    # TODO - Learn if the arrays from the loaded yamls are always one element only
    # To avoid a situation where we end up with a list with single element
    # if type(x) is list:
    #     x = x[0]
    # elif type(x) is dict:
    #     x = x.get("next element")
    # else:
    #     print("error")
    #
    # print(type(yaml_parsed.get('amf').get('sbi')))
    # print(type(yaml_parsed['amf']))
    # print(type(yaml_parsed['amf']['guami']))
    # print(yaml_parsed['amf']['guami'])
    # print(type(yaml_parsed['amf']['guami'][0]))
    # print(type(yaml_parsed['amf']['guami'][0]['plmn_id']))
    # print(type(yaml_parsed['amf']['guami'][0]['plmn_id']['mcc']))
    # print(yaml_parsed['amf']['guami'])
    # print(yaml_parsed['amf']['guami'][0]['plmn_id']['mcc'])
    pass


def read_yaml(file_path: str) -> dict:
    """
    Reads a yaml file specified in the file_path
    :param file_path: str
    :return:
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


def main():
    yaml_data = read_yaml("./transfers/some_folder/learning.yaml")
    foo(yaml_data)


if __name__ == "__main__":
    main()
