import fabric
import test_VM_commands as vm
import yaml_processing as config
import logging
from datetime import datetime
import copy


def update_configs(ip_addr):
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
    ue_diff0 = {'supi': 'imsi-001010000000000', 'mcc': '001', 'mnc': '01', 'gnbSearchList': ip_addr[3]}  # apn internet
    ue_diff1 = {'supi': 'imsi-001010000000001', 'mcc': '001', 'mnc': '01', 'gnbSearchList': ip_addr[3],
                'sessions0-apn': "internet2"}
    ue_diff2 = copy.deepcopy(ue_diff1)
    ue_diff2.update({'supi': 'imsi-001010000000002'})
    ue_diff3 = copy.deepcopy(ue_diff1)
    ue_diff3.update({'supi': 'imsi-001010000000003', 'sessions0-apn': 'ims'})
    ue_diff4 = copy.deepcopy(ue_diff1)
    ue_diff4.update({'supi': 'imsi-001010000000004', 'sessions0-apn': 'ims'})
    dict_arr = [ue_diff0, ue_diff1, ue_diff2, ue_diff3, ue_diff4]
    for i in range(5):
        config.modify_helper('ue', f'semi_adv/ue/ue{i}.yaml', dict_arr[i], overwrite=True)


def transfer_configs(c: [fabric.Connection]) -> None:
    """
    Transfers configs to the machines in the connection array
    This function is only for the semi advanced case
    :param c: [fabric.Connection]
    :return: None
    """
    # VM1: Control Plane 5G c[0]
    # VM2: User Plane 5G (1) c[1]
    # VM3: User Plane 5G (2) c[2]
    # VM4: gNodeB RAN c[3]
    # VM5: UE RAN (in total 5 UEs on one machine) c[4]

    # Control plane configs
    vm.put_file(c[0], "./transfers/semi_adv/Cplane/amf.yaml", "/etc/open5gs/amf.yaml", overwrite=True, sudo=True)
    vm.put_file(c[0], "./transfers/semi_adv/Cplane/smf.yaml", "/etc/open5gs/smf.yaml", overwrite=True, sudo=True)

    # User plane 1 configs
    vm.put_file(c[1], "./transfers/semi_adv/Uplane1/upf.yaml", "/etc/open5gs/upf.yaml", overwrite=True, sudo=True)

    # User plane 2 configs
    vm.put_file(c[2], "./transfers/semi_adv/Uplane2/upf.yaml", "/etc/open5gs/upf.yaml", overwrite=True, sudo=True)

    # gNodeB configs
    vm.put_file(c[3], "./transfers/semi_adv/gnb/gnb.yaml", f"/home/{c[3].user}/UERANSIM/config/gnb.yaml",
                overwrite=True, sudo=True)

    # UE configs
    for i in range(5):
        vm.put_file(c[4], f"./transfers/semi_adv/ue/ue{i}.yaml", f"/home/{c[4].user}/UERANSIM/config/ue{i}.yaml",
                    overwrite=True, sudo=True)


def put_launch_configs(c: [fabric.Connection]) -> None:
    """
    Prepares and transfers configs related to launch scripts
    :param c: [fabric.Connection]
    :return: None
    """
    created_file = vm.write_launch_config({"smf": "", "amf": "/some/path/to/config"})
    print(created_file)


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
    # try:
    #     c = vm.init_connections(conn_dict, username="open5gs")
    # except ConnectionError:
    #     logging.error("Received timeout error from init_connections. Driver script aborted!")
    #     exit(1)

    # vm.install_sim(c[0], "open5gs")
    # vm.install_sim(c[1], "open5gs")
    # vm.install_sim(c[2], "open5gs")
    # vm.install_sim(c[3], "ueransim")
    # vm.install_sim(c[4], "ueransim")
    update_configs(ip_addr)
    put_launch_configs(c)


if __name__ == "__main__":
    main()
