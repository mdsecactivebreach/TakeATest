import datetime
from process_lists import config
from flask import Flask, render_template, request
from mac_vendor_lookup import MacLookup
import re
import json

app = Flask(__name__)

log_file = "take_a_test.log"

protocol = "https"
server_host = "example.com"
port = 443

if port == 80 or port == 443:
    port_specification = ""
else:
    port_specification = ":{}".format(port)


def write_log_line(log_line):
    log_line = "{},{}".format(datetime.datetime.utcnow(), log_line)
    with open(log_file, "a") as fh:
        fh.write("{}\n".format(log_line))
    print(log_line)


@app.route('/')
def index():
    return render_template("index.html", protocol=protocol, server_host=server_host, port_specification=port_specification)


@app.route('/take_test/')
def take_a_test_recon():
    all_processes_temp = []
    for cat, cat_procs in config.items():
        all_processes_temp.extend(cat_procs)
    all_processes = "['" + "','".join(all_processes_temp) + "']"
    return render_template("recon.html", all_processes=all_processes)


@app.route('/mac_address/<string:mac>')
def render_mac_address(mac):
    mac_parts = re.findall('..', mac)
    mac_address = ":".join(mac_parts).upper()
    mac_address_vendor = MacLookup().lookup(mac_address)
    write_log_line("[{}] MAC Address: {}, MAC Address Vendor: {}".format(request.remote_addr, mac_address, mac_address_vendor))
    return render_template("mac_address.html", mac_address=mac_address, mac_address_vendor=mac_address_vendor)


@app.route('/process_list/', methods=["POST"])
def render_process_list():
    found_processes = request.json["found_processes"]
    print(found_processes)
    procs = []

    for key, found_process in found_processes.items():
        for cat, cat_procs in config.items():
            upper_cat_procs = [x.upper() for x in cat_procs]
            if found_process.upper() in upper_cat_procs:
                p = dict()
                p["process"] = found_process
                p["cat"] = cat
                procs.append(p)
                write_log_line("[{}] Process: {} Process Category: {}".format(request.remote_addr, found_process,
                                                                                     cat))
        print(repr(procs))
    return render_template("process_list.html", procs=procs)


@app.route('/os_info/', methods=["POST"])
def render_os_info():
    os_info_temp = request.json["os_info"]
    os_info = json.loads(os_info_temp)
    write_log_line(
        "[{}] OS Info: {}".format(request.remote_addr, os_info))
    return render_template("os_info.html", os_info=os_info)


@app.route('/virtual_machine/<int:is_virtual>')
def virtual_machine(is_virtual):
    if is_virtual == 1:
        write_log_line("[{}] Inside Virtual Machine".format(request.remote_addr))
        return "Inside Virtual Machine"
    else:
        write_log_line("[{}] Not Inside Virtual Machine".format(request.remote_addr))
        return "Not Inside Virtual Machine"


@app.route('/remote_session/<int:is_remote_session>')
def remote_session(is_remote_session):
    if is_remote_session == 1:
        write_log_line("[{}] Inside Remote Session".format(request.remote_addr))
        return "Inside Remote Session"
    else:
        write_log_line("[{}] Not Inside Virtual Machine".format(request.remote_addr))
        return "Not Inside Remote Session"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
