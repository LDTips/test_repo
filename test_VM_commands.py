import fabric
import logging
import invoke
import os


def connect(ip_addr: str, *, username: str, key_path: str) -> fabric.Connection:
    """
    Establishes and checks the possibility of an SSH connection with specified parameters.
    If connection is not possible, a message informing about that is written to stderr
    :param ip_addr: str
    :param username: str
    :param key_path: str
    :return: fabric.Connection
    """
    # Initiate connection params
    c = fabric.Connection(
        host=ip_addr,
        user=username,
        port=22,
        connect_timeout=10,
        connect_kwargs={'key_filename': [key_path]}
    )
    # Check if the connection is possible
    try:
        c.open()  # Try opening the connection specified above
        c.close()  # Will not be executed if the connection can not be made
    except TimeoutError:  # Raised by c.open() if connect_timeout is reached
        logging.exception("Connection to {} not established. Reason: timed out.".format(ip_addr))
        exit(1)
        # TODO - Is exit really the best behavior here?
    return c


def execute(target_con: fabric.Connection, *, command: str, sudo: bool = False) -> fabric.Result:
    """
    Performs a command on a machine specified in the connection. Can also be used to execute scripts.
    If sudo is true, the command will be executed as an elevated user.
    invoke.Unexpected exit is thrown by fabric.Connection.sudo or fabric.Connection.run
    if command execution returns an error code (if return_code is not 0)
    :param target_con: fabric.Connection
    :param command: str
    :param sudo: bool
    :return: fabric.Result
    """
    out = "Executed {0.command!r} on {0.connection.host}, got output \n{0.stdout}execution code {0.return_code}\n"
    out_err = "Error during execution of {0.command!r} on {0.connection.host}.\n" \
              "Got output on stderr \n{0.stderr}error code {0.return_code}\n"
    try:
        # If exception occurs, result is not defined. Does not exist in local scope
        if sudo:
            result = target_con.sudo(command, hide=True)
            result.command = result.command[31:]  # Removes redundant "sudo -S -p [...]" before the actual command
        else:
            result = target_con.run(command, hide=True)

        logging.info(out.format(result))
    except invoke.UnexpectedExit as e:  # Details of the failed command execution are in the exception
        if sudo:
            e.result.command = e.result.command[31:]
        logging.exception(out_err.format(e.result))
        return e.result
    else:
        return result


def transfer_file(target_con: fabric.Connection, local_path: str, dest_path: str, *, permissions: str) -> str:
    """
    Transfers a file found at file_path to the machine specified in target_con.
    Due to harder implementation, sudo version of the method might not be implemented in the future
    Permissions determines the permission on the target system. Should be of Linux format e.g. "700"
    Returns the remote path of the file that was put. Returns empty string if transfer failed
    :param target_con: fabric.Connection
    :param local_path: str
    :param dest_path: str
    :param permissions: str
    :return: str
    """

    try:
        # Transfer the file with put
        target_con.put(local_path, dest_path)
        target_con.run('chmod {perm} {path}'.format(perm=permissions, path=dest_path))
    except (OSError, FileNotFoundError) as e:  # General error raised if transfer fails
        logging.exception("Error occurred while transferring {}\nReason: {}".format(local_path, e))
        return ""
    else:
        return dest_path


def get_default_configs(target_con: fabric.Connection, dest_path: str, type: str, *, overwrite: bool = False) -> None:
    """
    Transfers all yaml files of open5gs from the machine specified in the target con to the dest_path
    If overwrite flag is set, the function will overwrite existing files in the path
    If it is not set and files exist in the path, the function will not execute
    This method theoretically does not need to be used every time. One fetch of open5gs and UERANSIM configs
    Might be enough for config file modifications
    :param target_con: fabric.Connection
    :param dest_path: str
    :param type: str
    :param overwrite: bool
    :return: None
    """
    try:
        if os.path.exists(dest_path) and not overwrite:
            raise FileExistsError("Overwrite flag was not set, but files exist in {}".format(dest_path))
        if type.lower() not in ("open5gs", "ueransim"):
            raise ValueError("Invalid type variable passed. Should be open5gs or ueransim")
    except (FileExistsError, ValueError) as e:
        logging.exception(e)
        return
    else:
        if type == "open5gs":
            get_file(target_con, "/etc/open5gs/", dest_path, folder_mode=True)
        else:  # It must be UERANSIM due to earlier if statement
            get_file(target_con, "/root/UERANSIM/config/open5gs-gnb.yaml", dest_path)
            get_file(target_con, "/root/UERANSIM/config/open5gs-ue.yaml", dest_path)


# NOTE. Get method is unable to fetch files into a directory:
# target_con.get(remote_path, "./configs/nrf.yaml")  # e.g. when remote_path is /etc/open5gs/nrf.yaml - works
# target_con.get(remote_path, "./")  # when remote_path is /etc/open5gs/ does not work, because:
# PermissionError: [Errno 13] Permission denied: 'C:\\Users\\batru\\Desktop\\system_commands_testing\\configs'
def get_file(target_con: fabric.connection, remote_path: str, dest_path: str = "", *,
             folder_mode: bool = False) -> None:
    """
    Transfers file from remote machine specified in target_con, to local filesystem.
    If folder_mode is true, it will attempt to transfer whole folder
    Dest_path should be relative to the 'transfers' folder.
    :param target_con: fabric.connection
    :param remote_path: str
    :param dest_path: str
    :param folder_mode: bool
    :return: str
    """
    # TODO - Determine why transferring whole folder does not work. Maybe it is just not possible?
    # TODO - Handle Exceptions
    # Determine the directory contents
    if folder_mode:  # We need to fetch folder contents to transfer files one by one
        # Find only files (not folders) in the specified remote_path
        file_list = execute(target_con, command='find {} -maxdepth 1 -type f'.format(remote_path))
        # Split each file path into different array indexes
        file_list = file_list.stdout.split()
        # Since find gives the full path, we need to extract only the file names to properly specify the destination
        file_names = [file.split("/")[-1] for file in file_list]
        for file_path, file_name in zip(file_list, file_names):
            target_con.get(file_path, "./transfers/{}/{}".format(dest_path, file_name))
    else:
        file_name = remote_path.split("/")[-1]
        target_con.get(remote_path, "./transfers/{}/{}".format(dest_path, file_name))


def install_open5gs(target_con: fabric.Connection) -> None:
    """
    Does necessary file transfers and commands executions to install Open5gs
    On the machine specified by the ip_addr, authenticating with key found in key_path
    :param target_con: fabric.Connection
    :return: None
    """

    message = "Transfer of file {} to dest {} on machine {}"
    src_path = "./scripts/install_open5gs.sh"  # dot specifies relative path
    if target_con.user != "root":
        dest_path = "/home/{}/install_open5gs".format(target_con.user)
    else:
        dest_path = "/root/install_open5gs"

    result_path = transfer_file(target_con, src_path, dest_path, permissions="744")  # rwxr--r--
    if len(result_path) != 0:
        logging.info(message.format(src_path, dest_path, target_con.host) + " successful!")
    else:
        # Logging might not be needed as message is already written out in the transfer_file function
        logging.error(message.format(src_path, dest_path, target_con.host) + " FAILED!")
        return
    # Sudo true is needed in case connection is for the non-root user
    # However, if "no password sudo" is not enabled, this will not work for non-root
    execute(target_con, command="~/install_open5gs.sh", sudo=True)


def setup_end(ip_addr: str, key_path: str) -> None:
    """
    Method prints necessary information regarding user interaction with the machine
    After the setup was completed
    :param ip_addr: str
    :param key_path: str
    :return: None
    """
    print("Machine at address {} has completed setup\nAccess it with the following command:")
    print("ssh -i {key} <username>@{IP}".format(key=key_path, IP=ip_addr))
    print("Note: Key path can be relative")
    print("Note 2: If issues arise with bad key security error from ssh command, use windows cmd commands:")
    print("icacls <private_key_path> /inheritance:r\n icacls <private_key_path> /grant:r \"%username%\":\"(R)\"")


def main():
    logging.basicConfig(filename="test.log", level=logging.INFO)
    # Define necessary connection information
    ip_addr = ["192.168.0.105"]
    key_path_all = r"C:\Users\batru\Desktop\Keys\private_clean_ubuntu_20_clone"
    c = connect(ip_addr[0], username="root", key_path=key_path_all)
    # execute(c, command="echo $SHELL", sudo=False)
    install_open5gs(c)
    # "transfers/some_folder/amf_realconfig_test.yaml"
    # dest_path = transfer_file(c, "/transfers/all_open5gs/amf.yaml", "/etc/open5gs/amf.yaml", permissions="600")
    # if len(dest_path) == 0:
    #     print("File not transferred. Check log")
    # else:
    #     print("File transferred to {}".format(dest_path))

    # get_file(c, remote_path="/etc/open5gs/amf.yaml", dest_path="/some_folder", folder_mode=False)
    # transfer_configs(c, "/all_UERANSIM/", "UERANSIM")


if __name__ == "__main__":
    main()
