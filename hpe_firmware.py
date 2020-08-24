#!/usr/bin/python3

from datetime import datetime

import json
import logging
import os
import redfish
import time
import yaml

logfile = os.environ["HOME"] + "/hpe/hpe.log"
logging.basicConfig(
    filename=logfile,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logging.info("------ starting HPE redfish python test ")


"""
http://downloads.linux.hpe.com/project/fwpp/fwget.html
HPE fw repo: 
wget --user=$TOKEN --password= 
https://downloads.linux.hpe.com/SDR/repo/fwpp-gen10/current/fwrepodata/fwrepo.json
"""

machines_file = "machines.yaml"

##############################################################################
# Follow HPE instructions to access
# HPE Firmware Pack for ProLiant online repository
# http://downloads.linux.hpe.com/project/fwpp/fwget.html
# Login with your HPE Passport credentials and generate your token
##############################################################################


def parse_machine_models():
    # this is going to be read from a machines.yaml,
    # this way we can allow more than one machine of the same model!

    # diferent servers (for Gen10): need to add the family: A40, A41, A43...
    # HPE ProLiant DL385 Gen10 (A40) Servers
    # HPE ProLiant DL385 Gen10 Plus (A42) Servers

    with open("machines.yaml", "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    print("\nmachines yaml data: ", yaml_data)
    models = []
    for machine in yaml_data:
        model = yaml_data[machine]["model"]
        print("\nmachine model: ", yaml_data[machine]["model"])
        if model not in models:
            models.append(yaml_data[machine]["model"])
    print("\n\nModel(s): ", models)
    return models, yaml_data


def get_hpe_fwrepo(models):

    # models = ['DL385 Gen10 (A40)', 'DL325 Gen10 (A41)']
    machine = {}

    # hardcoding json file (DO NOT upload this file!
    # from 2020 Jun 23
    # fwrepo.json     2020-06-23 19:12   72K

    with open("fwrepo.json") as json_file:
        data = json.load(json_file)

    # date yyyymmdd

    for model in models:
        logging.info("Model: " + str(model))
        modeldict = {}
        for fw in data:
            if model in (data[fw]["description"]):
                logging.info(" fw: " + str(fw) + " " + str(data[fw]["description"]))
                print("\nFW desc: ", data[fw]["description"])
                print("FW date: ", data[fw]["date"])
                logging.info("  date: " + str(data[fw]["date"]))
                modeldict.update(
                    {fw: {"desc": data[fw]["description"], "date": data[fw]["date"]}}
                )
                machine.update({model: modeldict})
    del modeldict
    print("\n\n --> machine model - firmware info: ", machine)
    return machine


def get_machines_info(ilo_host, login_account, login_password):
    REST_OBJ = redfish.RedfishClient(
        base_url=ilo_host, username=login_account, password=login_password
    )

    REST_OBJ.login(auth="session")
    REST_OBJ.logout

    response = REST_OBJ.get("/redfish/v1/systems/1")

    print("\n\n response.status = 200? ", response.status)

    machine = response.dict

    logging.info("get_lab_machines")
    logging.info(
        "machine: "
        + str(machine["SerialNumber"])
        + " firmware_version: "
        + str(machine["BiosVersion"])
    )
    date = machine["Oem"]["Hpe"]["Bios"]["Current"]["Date"]
    date_obj = datetime.strptime(date, "%m/%d/%Y")
    print(
        "\n Current firmware info: {} (date: {})".format(
            machine["Oem"]["Hpe"]["Bios"], date_obj
        )
    )
    logging.info("Current firmware info: " + str(machine["Oem"]["Hpe"]["Bios"]))

    return date_obj


if __name__ == "__main__":

    models, lab_machines = parse_machine_models()
    fw_info = get_hpe_fwrepo(models)
    for x in lab_machines:
        model = lab_machines[x]["model"]
        logging.info(
            "-----------------------------------------------------------------------------------------"
        )
        logging.info(
            " > checking firmware update for this model: "
            + str(model)
            + " machine: "
            + str(x)
        )
        print(
            "\n\n checking firmware update for '{}' - machine model: {}".format(
                x, model
            )
        )
        hpe_ilo_host = lab_machines[x]["bmc"]["address"]
        hpe_login_account = lab_machines[x]["bmc"]["user"]
        hpe_login_password = lab_machines[x]["bmc"]["password"]
        current_date = get_machines_info(
            hpe_ilo_host, hpe_login_account, hpe_login_password
        )
        for fw in fw_info[model]:
            fw_date = fw_info[model][fw]["date"]
            fw_date = datetime.strptime(fw_date, "%Y%m%d")
            if fw_date > current_date:
                print("--- New FW available '{}':{} ".format(fw, fw_info[model][fw]))
                logging.info(
                    "--- New FW available: " + str(fw) + ": " + str(fw_info[model][fw])
                )

    print("\n\nDetailed LOG informations: ", logfile)

    logging.debug(" --- end --- ")
