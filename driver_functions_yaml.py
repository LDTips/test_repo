import logging


def driver_universal(key_split: list[str], diff_dict: dict, file_type: str, new_value: int | str) -> dict:
    message = "Could not assign key {}-{}-{}-{}. No match"
    if len(key_split) == 1:
        for case in range(2):
            try:
                if case == 0:
                    diff_dict[file_type][key_split[0]] = new_value
                elif case == 1:
                    diff_dict[key_split[0]] = new_value
                break
            except (KeyError, TypeError) as e:
                if case == 1:
                    logging.exception(message.format(file_type, key_split[0], "", ""))
                else:
                    continue
    elif len(key_split) == 2:
        for case in range(3):
            try:
                if case == 0:
                    diff_dict[file_type][key_split[0]][key_split[1]] = new_value
                elif case == 1:
                    diff_dict[file_type][key_split[0]][0][key_split[1]] = new_value
                elif case == 2:
                    diff_dict[file_type][key_split[0]][0][key_split[1]][0] = new_value
                break
            except (KeyError, TypeError) as e:
                if case == 2:
                    logging.exception(message.format(file_type, key_split[0], key_split[1], ""))
                else:
                    continue

    elif len(key_split) == 3:
        for case in range(3):
            try:
                if case == 0:
                    diff_dict[file_type][key_split[0]][0][key_split[1]][0][key_split[2]] = new_value
                if case == 1:
                    diff_dict[file_type][key_split[0]][0][key_split[1]][key_split[2]] = new_value
                if case == 2:
                    diff_dict[file_type][key_split[0]][key_split[1]][key_split[2]] = new_value
                break
            except (KeyError, TypeError) as e:
                if case == 2:
                    logging.exception(message.format(file_type, key_split[0], key_split[1], key_split[2]))
                else:
                    continue
    return diff_dict
