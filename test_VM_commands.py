import fabric
import logging
import invoke
import os

def connect(ip_addr: str, *, username: str, key_path: str) -> fabric.Connection:
    """
    Establishes and checks the possibility of an SSH connection with specified parameters.
    If connection is not possible, a message informing about that is written to stderr
    :param ip_addr:
    :param username:
    :param key_path:
    :return:
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
        exit(1)
        # TODO - Is exiting really the best behavior here?
    else:
        return result


def transfer_file(target_con: fabric.Connection, *, local_path: str, permissions: str) -> str:
    """
    Transfers a file found at file_path to the machine specified in target_con.
    Due to harder implementation, sudo version of the method might not be implemented in the future
    Permissions determines the permission on the target system. Should be of Linux format e.g. "700"
    Returns the remote path of the file that was put. Returns empty string if transfer failed
    :param target_con: fabric.Connection
    :param local_path: str
    :param permissions: str
    :return: str
    """

    # TODO - Is checking the correctness of permissions really necessary?
    # Extract the file name
    local_abspath = os.path.abspath(local_path)  # Get absolute path
    dest_file_name = os.path.basename(local_abspath)
    dest_file_name = dest_file_name.split(".")[0]
    # Determine the target absolute path. Root has different home folder than other users
    if target_con.user == "root":
        dest_path = "/root/{file_name}".format(file_name=dest_file_name)
    else:
        dest_path = "/home/{user}/{file_name}".format(user=target_con.user, file_name=dest_file_name)

    try:
        # Transfer the file with put
        target_con.put(local_path, dest_path)
        target_con.run('chmod {perm} {path}'.format(perm=permissions, path=dest_path))
    except (OSError, FileNotFoundError) as e:  # General error raised if transfer fails
        logging.exception("Error occurred while transferring {}\nReason: {}".format(dest_file_name, e))
        return ""
    else:
        return dest_path


def install_open5gs(target_con: fabric.Connection):
    """
    Executes necessary scripts and operations to install
    Open5gs on the machine specified in the target_con
    :param target_con: fabric.Connection
    :return:
    """
    pass


def main():
    logging.basicConfig(filename="test.log", level=logging.INFO)
    # Define necessary connection information
    ip_addr = "192.168.0.105"
    key_path = "C:\\Users\\batru\\Desktop\\Keys\\private_clean_ubuntu_20_clone"
    c = connect(ip_addr, username="open5gs", key_path=key_path)
    print(c.user)
    # execute(c, command="echo $SHELL", sudo=False)
    dest_path = transfer_file(c, local_path="scripts/install_open5gs.sh", permissions="700")
    if len(dest_path) == 0:
        print("File not transferred. Check log")
    else:
        print("File transferred to {}".format(dest_path))


if __name__ == "__main__":
    main()
