import fabric
import logging
import invoke


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
    Performs a command on a machine specified in the connection.
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


def execute_script(target_con: fabric.Connection, *, script_name: str, sudo: bool = False):
    """
    Executes a script on the target machine. If the script does not exist on the target
    The method will attempt to transfer the script from scripts folder to the target machine
    script_name can be with or without .sh extension. Due to windows shenanigans, we need *.sh locally
    :param target_con: fabric.Connection
    :param script_name: str
    :param sudo: bool
    """
    # TODO - rename the method and change it's operation. For now it only transfers the script to the target machine
    # We need .sh to properly address the script file on the local system
    if script_name[-3:] != ".sh":
        script_name += ".sh"

    # Determine the absolute path. Root has different home folder than other users
    if target_con.user == "root":
        dest_path = "/root/" + script_name[:-3]
    else:
        dest_path = "/home/" + target_con.user + "/" + script_name[:-3]
    print(dest_path)
    try:
        # Install the script by transferring it, and then using install command
        target_con.put('C:\\Users\\batru\\Desktop\\system_commands_testing\\scripts\\write_something.sh', dest_path)
        target_con.run('chmod +x ' + dest_path)
    except OSError as e:  # Raised if local file does not exist
        logging.exception("Error occured while transferring {}\nReason: {}".format(script, e))
        return
    return


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
    c = connect(ip_addr, username="root", key_path=key_path)
    print(c.user)
    # execute(c, command="echo $SHELL", sudo=False)
    #execute_script(c, script="write_something")
    execute_script2(c, script="write_something")


if __name__ == "__main__":
    main()
