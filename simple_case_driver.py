import test_VM_commands as vm
import yaml_processing as config
import logging


def main():
    logging.basicConfig(filename="driver_script.log", level=logging.INFO)
    # Define connection information
    ip_addr = ["192.168.111.105", "192.168.111.110"]
    key_path_all = r"C:\Users\batru\Desktop\Keys\private_clean_ubuntu_20_clone"
    conn_dict = {ip_addr[0]: key_path_all, ip_addr[1]: key_path_all}
    # Initialise connections to the machines
    c = vm.init_connections(conn_dict)
    if len(c) == 0:
        print("Connections were not initialised properly!")
        exit(1)
    # Run install scripts
    # vm.install_sim(c[0], "open5gs")
    # vm.install_sim(c[1], "ueransim")


if __name__ == "__main__":
    main()
