#!/usr/bin/env python3

"""
Data processing module. Return static HTML file after processing external JSON file.
Has been created for pilot prototyping the project

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vfilippo'

"""

import datetime
import jinja2
import json
import logging
import pprint
import re
import traceback

import sys
import yaml

modules = {}
debug = False

# to account for cooling ("~40% of the energy consumption in the DC is cooling")
cool_coeff = 1.67
kw_per_slice = .2  # .2 kW per slice
# kW to k$/year, with 10.5c per kWh (https://www.chooseenergy.com/electricity-rates-by-state/), 8766 hrs/year
kw_to_dpy = cool_coeff * 10.5/100 * 8.766 
kw_to_co2 = cool_coeff * 0.28307 * 8.766 # kW to tonns of CO2


def normalize(a, b):
    if b == 0:
        return 0, 0
    while b < 15:
        a *= 10
        b *= 10
    r = 55 + (b%15 + 1)
    k = b/r
    return round(a/k, 2), round(r, 2)


def process_totals(totals):
    num_slices_admindown = totals["admin down"]
    num_slices_down = totals["down"]
    
    ps_total = num_slices_admindown * kw_per_slice
    ps_total_down = num_slices_down * kw_per_slice
    pst = ps_total
    pstd = ps_total_down
    dpy = round(ps_total * kw_to_dpy, 1)
    co2 = round(ps_total * kw_to_co2, 1)
    ps_total = round(8766 * ps_total * cool_coeff, 2)

    dpy_down = round(ps_total_down * kw_to_dpy, 1)
    co2_down = round(ps_total_down * kw_to_co2, 1)
    ps_total_down = round(8766 * ps_total_down * cool_coeff, 2)

    wh = "kWh"
    if ps_total > 1000 or ps_total_down > 1000:
        wh = "MWh"
        ps_total = round(ps_total / 1000, 1)
        ps_total_down = round(ps_total_down / 1000, 1)
    p1,p2 = normalize(ps_total, ps_total_down)
    m1,m2 = normalize(dpy, dpy_down)
    c1,c2 = normalize(co2, co2_down)
    wh2 = "kW"
    if pst > 1000 or pstd > 1000:
        wh2 = "MW"
    values = ps_total, ps_total_down, dpy, dpy_down, co2, co2_down, p1, p2, m1, m2, c1, c2, wh, num_slices_admindown, num_slices_down, pst, pstd, wh2

    return values


def save_html(values=None):
    '''
    values: 6 numbers for admindown/down of power, money, co2 savings
    cards: list of lists with family name, # of devs, # of LCs, # of admindown ports,
        # of down ports, # of admindown slices, # of down slices, powersave kW for admindown
    '''
    with open("template.html") as f:
        HTML = f.read()
    template =  jinja2.Template(HTML) #_TEMPLATE)
    out = template.render(values=values)
    return out


def parse_device_output(seed, dev, ci):
    global debug

    lc_type_pattern = re.compile("(A9.+?-[^ \t\r\n\f].*GE)|(A9.+?-MOD.*-)")
    try:
        total_slices = {"admin down": 0, "down": 0, "full down": 0, "full admin down": 0}
        ifs = {}
        for intf in ci['interfaces']:
            # WARN! Assumption that interface name always starts with two letters!
            iname = intf[0][2:]
            spl = iname.split("/")
            lc_slot = "/".join(spl[:3]) + "/"
            intf_idx = int(spl[3])
            subif = spl[4] if len(spl) > 4 else '*'
            intf_state = intf[1]
            if not lc_slot in ifs:
                ifs[lc_slot] = {}
            if not intf_idx in ifs[lc_slot]:
                ifs[lc_slot][intf_idx] = {}
            ifs[lc_slot][intf_idx][subif] = intf_state
        if debug:
            print("-"*48,"\nInterfaces\n")
            pprint.pprint(ifs)
            print("="*48)

        for lc in ci['line_cards']:
            if debug:
                print("LC: %s" % lc)
            lc_slot = lc[0][:lc[0].rfind("/")]+"/0/"
            lc_type = lc[2]
            slices = seed[lc_type]
            slice_state = {}
            for sk, sv in slices.items():
                state = "admin down"
                for intf_idx in sv:
                    if lc_slot in ifs:
                        if intf_idx in ifs[lc_slot]:
                            for intf_state in ifs[lc_slot][intf_idx].values():
                                if intf_state == "up":
                                    state = "up"
                                    break
                                if intf_state == "down":
                                    state = "down"
                    if state == "up":
                        break
                if debug:
                    print("\tLC %s slice %s state: %s" % (lc_slot, sk, state))
                slice_state[sk] = state
            # Here a bit of logic to not count on slice 0 unless everything is (admin) down
            slsv = [sls for sk, sls in slice_state.items() if sk != 0]
            total_slices["admin down"] += slsv.count("admin down")
            tsd = slsv.count('down')
            total_slices["down"] += tsd
            tsu = slsv.count("up")
            if not tsu:
                # no slices up, slice 0 can potentially be shut
                if not tsd:
                    # all other slices are in 'admin down'
                    # we can add 1 to total_slices 'admin down' or 'down' depends on state of slice 0
                    if slice_state[0] != "up":
                        total_slices[slice_state[0]] += 1
                        total_slices["full %s" % slice_state[0]] += 1
                elif slice_state[0] != "up":
                    # at least one slice in 'down', we can at most count slice 0 for 'down'
                    total_slices["down"] += 1
                    total_slices["full down"] += 1
        return False, total_slices
        
    except Exception as e:
        return True, "Error with parsing device data for %s... (%s)" % (dev, e)


def parse_output(seed, outcome_fname):
    global debug

    try:
        with open(outcome_fname, "r") as f:
            outcome = json.load(f)
    except Exception as e:
        return True, "Failed to load json: %s" % e, None
    try:
        errors = []
        results = {}
        for dev, ci in outcome.items():
            err, result = parse_device_output(seed, dev, ci)
            if err:
                errors.append("Error with device %s outcome. (%s)" % (dev, result))
                continue
            results[dev] = result
            
    except Exception as e:
        return True, "Failed to parse outcome: %s" % e

    return False, results, errors


def read_seed(fname):
    global debug

    with open(fname, "r") as f:
        seed = yaml.safe_load(f)
    try:
        # need to make some substitutions 
        for lc_id, vlist in seed.items():
            vdict = {}
            if vlist:
                for kk in vlist:
                    for kkk,vvv in kk.items():
                        if type(vvv) is int:
                            vvv = [vvv]
                        elif ".." in vvv:
                            s,e = vvv.split("..")
                            vvv = range(int(s),int(e))
                        elif "," in vvv:
                            vvv = [int(x) for x in vvv.split(",")]
                        kk[kkk] = vvv
                    vdict[kkk] = vvv
            seed[lc_id] = vdict
    except Exception as e:
        return True, "Problem with parsing seed file... %s" % e
    return False, seed 


def main():
    global debug
    """
    Takes the file and calculate possible power saving.
    """
    if len(sys.argv) < 3:
        print("Usage: %s <seed_file> <VZ_output> [debug]" % sys.argv[0])
        quit
    if len(sys.argv) > 3 and sys.argv[3] == 'debug':
        debug = True
        
    err, seed = read_seed(sys.argv[1])
    if err:
        print("Error: %s" % seed)
        quit
    if debug:
        print("-"*48)
        pprint.pprint(seed)

    err, values, errors = parse_output(seed, sys.argv[2])
    if err:
        print("Error: %s" % values)
        quit
    if errors:
        print("Hit some erros in parse_output:\n\t%s" % "\n\t".join(errors))

    totals = {"admin down": 0, "down": 0, "full down": 0, "full admin down": 0}
    for dev, res in values.items():
        # total_slices = {"admin down": 0, "down": 0, "full down": 0, "full admin down": 0}
        for k, v in res.items():
            totals[k] += v
    if debug:
        print("-"*48)
        print("Totals:", totals)

    values = process_totals(totals)
    
    html_report = save_html(values)
    
    filename = "report.html"
    with open(filename, "w") as f:
        f.write(html_report)

    print("Job completed...")


if __name__ == '__main__':
    main()
