from fabric import Connection
from sys import stderr


def connect(ip_addr: str, username: str, key_path: str) -> Connection:
    """
    Establishes and checks the possibility of an SSH connection with specified parameters.
    If connection is not possible, a message informing about that is written to stderr
    :param ip_addr:
    :param username:
    :param key_path:
    :return:
    """
    # Initiate connection params
    c = Connection(
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
        print("Connection to {} not established. Reason: timed out.".format(ip_addr), file=stderr)
        exit(1)
        # TODO - Is exit really the best behavior here?
    return c


def main():
    # Define necessary connection information
    ip_addr = "192.168.1.169"
    key_path = "C:\\Users\\batru\\Desktop\\autorun_test1_RSA.pub"
    c = connect(ip_addr, "open5gs", key_path)
    result = c.run('uname -s', hide=True)  # Run a command using the started connection
    output = "Executed {0.command!r} on {0.connection.host}, got output \n{0.stdout}"
    print(output.format(result))


if __name__ == "__main__":
    main()
