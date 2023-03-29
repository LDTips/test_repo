import fabric
import test_VM_commands as vm
import yaml_processing as config
import logging
from datetime import datetime


def main():
    # TODO - Finish this driver function. NOT TESTED!!
    # driver function for the case: https://github.com/s5uishida/open5gs_5gc_ueransim_sample_config
    logging.basicConfig(filename="semiadv_driver_script.log", level=logging.INFO)
    logging.info("\n--------------------------------------\n"
                 "Start log {}"
                 "\n--------------------------------------"
                 .format(datetime.now()))
    # 5 VM's will be used (array is sorted in this order):
    # VM1: Control Plane 5G
    # VM2: User Plane 5G (1)
    # VM3: User Plane 5G (2)
    # VM4: gNodeB RAN
    # VM5: UE RAN (in total 5 UEs on one machine)

    ip_addr = ["192.168.111.111", "192.168.111.112", "192.168.111.113",  # Open5gs IPs
               "192.168.111.191", "192.168.111.192"]  # UERANSIM IPs
    key_path = r"C:\Users\batru\Desktop\Keys\private_clean_ubuntu_20_clone"
    conn_dict = {}
    for ip in ip_addr:  # Populate the connection dict. Key is same for all
        conn_dict.update({ip: key_path})

    c = []
    try:
        c = vm.init_connections(conn_dict, username="open5gs")
    except ConnectionError:
        logging.error("Received timeout error from init_connections. Driver script aborted!")
        exit(1)

    vm.install_sim(c[0], "open5gs")
    vm.install_sim(c[1], "open5gs")
    vm.install_sim(c[2], "open5gs")
    vm.install_sim(c[3], "ueransim")
    vm.install_sim(c[4], "ueransim")


if __name__ == "__main__":
    main()
