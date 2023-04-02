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
    # VM1: Control Plane 5G ip_addr[0]
    # VM2: User Plane 5G (1) ip_addr[1]
    # VM3: User Plane 5G (2) ip_addr[2]
    # VM4: gNodeB RAN ip_addr[3]
    # VM5: UE RAN (in total 5 UEs on one machine) ip_addr[4]

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

    # Change configs - C-Plane
    amf_diff = {'amf-ngap0-addr': ip_addr[0], 'amf-guami-plmn_mcc': '001', 'amf-guami-plmn_mnc': '01',
                'amf-tai-plmn_id-mcc': '001', 'amf-tai-plmn_id-mnc': '01',
                'amf-plmn_support-plmn_id-mcc': '001', 'amf-plmn_support-plmn_id-mnc': '01'}
    config.modify_helper('amf', 'semi_adv/Cplane/amf.yaml', amf_diff, overwrite=True)

    smf_diff = {'smf-pfcp0-addr': ip_addr[0], 'smf-gtpu0-addr': ip_addr[0],
                'smf-subnet0-addr': "10.45.0.1/16", 'smf-subnet0-dnn': "internet",
                'smf-subnet1-addr': "10.46.0.1/16", 'smf-subnet1-dnn': "internet2",
                'smf-subnet2-addr': "10.47.0.1/16", 'smf-subnet2-dnn': "ims",
                'upf-pfcp0-addr': ip_addr[1], 'upf-pfcp0-dnn': ["internet", "internet2"],
                'upf-pfcp1-addr': ip_addr[2], 'upf-pfcp1-dnn': "ims"}
    config.modify_helper('smf', 'semi_adv/Cplane/smf.yaml', smf_diff, overwrite=True)

    # Change configs - U-Plane1
    upf_diff1 = {'upf-pfcp0-addr': ip_addr[1], 'upf-gtpu0-addr': ip_addr[1],
                 'upf-subnet0-addr': "10.45.0.1/16", 'upf-subnet0-dnn': "internet", 'upf-subnet0-dev': "ogstun",
                 'upf-subnet1-addr': "10.46.0.1/16", 'upf-subnet1-dnn': "internet2", 'upf-subnet1-dev': "ogstun2"}
    config.modify_helper('upf', 'semi_adv/Uplane1/upf.yaml', upf_diff1, overwrite=True)

    # Change configs - U-Plane2
    upf_diff2 = {'upf-pfcp0-addr': ip_addr[2], 'upf-gtpu0-addr': ip_addr[2],
                 'upf-subnet0-addr': "10.47.0.1/16", 'upf-subnet0-dnn': "ims", 'upf-subnet0-dev': "ogstun3"}
    config.modify_helper('upf', 'semi_adv/Uplane2/upf.yaml', upf_diff2, overwrite=True)

    # Change configs - gNB
    gnb_diff = {'mcc': "001", 'mnc': "01", 'linkIp': ip_addr[3], 'ngapIp': ip_addr[3], 'gtpIp': ip_addr[3],
                'amfConfigs0-address': ip_addr[0]}
    config.modify_helper('gnb', 'semi_adv/gnb/gnb.yaml', gnb_diff, overwrite=True)
    # Change configs - UE
    # TODO

if __name__ == "__main__":
    main()
