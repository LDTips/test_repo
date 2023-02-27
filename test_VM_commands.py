import fabric
import sys
import logging
import invoke


def connect(ip_addr: str, username: str, key_path: str) -> fabric.Connection:
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
        print("Connection to {} not established. Reason: timed out.".format(ip_addr), file=sys.stderr)
        exit(1)
        # TODO - Is exit really the best behavior here?
    return c


def execute(machine_con: fabric.Connection, command: str, sudo: bool) -> fabric.Result:
    """
    Performs a command on a machine specified in the connection.
    If sudo is true, the command will be executed as an elevated user.
    invoke.Unexpected exit is thrown by fabric.Connection.sudo or fabric.Connection.run
    if command execution returns an error code (if return_code is not 0)
    :param machine_con: fabric.Connection
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
            result = machine_con.sudo(command, hide=True)
            result.command = result.command[31:]  # Removes redundant "sudo -S -p [...]" before the actual command
        else:
            result = machine_con.run(command, hide=True)

        logging.info(out.format(result))
    except invoke.UnexpectedExit as e:  # Details of the failed command execution are in the exception
        if sudo:
            e.result.command = e.result.command[31:]
        logging.exception(out_err.format(e.result))
        exit(1)
        # TODO - Is exiting really the best behavior here?
    else:
        return result


def main():
    logging.basicConfig(filename="test.log", level=logging.INFO)
    # Define necessary connection information
    ip_addr = "192.168.0.169"
    key_path = "C:\\Users\\batru\\Desktop\\autorun_test1_RSA.pub"
    c = connect(ip_addr, "open5gs", key_path)
    execute(c, "echo $SHELL", False)


if __name__ == "__main__":
    main()
