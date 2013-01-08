#!/usr/bin/python
from lxml import etree
import sys
import os

def run():
    print "[*] NETXML to CSV Converter by Meatballs"
    
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        print "[*] Usage: use input file name for output: %s input" % sys.argv[0]
        print "[*] Custom output: %s input output" % sys.argv[0]
    else:
        input_file_name = sys.argv[1]
        
        if len(sys.argv) == 3:
            output_file_name = sys.argv[2]
        else:
            outFileName = os.path.splitext(sys.argv[1])
            output_file_name = outFileName[0] + ".csv"
        
        if input_file_name != output_file_name:
            try:
                output = file(output_file_name, 'w')
            except:
                print "[-] Unable to create output file '%s' for writing." % output_file_name
                exit()

            try:    
                doc = etree.parse(input_file_name)
            except:
                print "[-] Unable to open input file: '%s'." % input_file_name
                exit()

            print "[+] Parsing '%s'." % input_file_name
            sys.stdout.write("[+] Outputting to '%s' " % output_file_name)
            output.write("BSSID,Channel,Privacy,Cipher,Auth,Power,ESSID,Manuf,Longitude,Latitude\n")
            result = parse_net_xml(doc)
            output.write(result)
            output.write("\n")
            sys.stdout.write(" Complete.\r\n")

def net_encryption(network):
    
        encryption = network.getiterator('encryption')

        privacy = ""
        cipher = ""
        auth = ""
        if encryption is not None:
            for item in encryption:
                if item.text.startswith("WEP"):
                    privacy = "WEP"
                    cipher = "WEP"
                    auth = ""
                    break
                elif item.text.startswith("WPA"):
                    if item.text.endswith("PSK"):
                        auth = "PSK"
                    elif item.text.endswith("AES-CCM"):
                        cipher = "CCMP " + cipher
                    elif item.text.endswith("TKIP"):
                        cipher += "TKIP "
                elif item.text == "None":
                    privacy = "OPN"

        cipher = cipher.strip()
        
        if cipher.find("CCMP") > -1:
            privacy = "WPA2"

        if cipher.find("TKIP") > -1:
            privacy += "WPA"

        return (privacy, cipher, auth)
    
def net_singal(network):
    power = network.find('snr-info')
        
    dbm = ""

    if power is not None:
        dbm = power.find('max_signal_dbm').text

    if int(dbm) > 1:
        dbm = power.find('last_signal_dbm').text

    if int(dbm) > 1:
        dbm = power.find('min_signal_dbm').text

    return dbm

def net_gps(network):
    gps = network.find('gps-info')
                
    latitude = "0.0"
    longitude = "0.0"
        
    if gps is not None:
        latitude = gps.find('avg-lat').text
        longitude = gps.find('avg-lon').text
        
    return (latitude, longitude)        

def parse_net_xml(doc):
    result = ""

    total = len(list(doc.getiterator("wireless-network")))
    tenth = total/10
    count = 0

    for network in doc.getiterator("wireless-network"):
        count += 1
        if (count % tenth) == 0:
            sys.stdout.write(".")
        
        network_type = network.attrib["type"]
        channel = network.find('channel').text
        bssid = network.find('BSSID').text
        manuf = network.find('manuf').text
        
        # Get the network lat/lon                    
        latitude, longitude = net_gps(network)
                
        if network_type == "probe" or channel == "0":
            continue 
        
        # Get network encryption
        privacy, cipher, auth = net_encryption(network)
                
        # Get network signal
        dbm = net_singal(network)

        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
            essid_text = network.find('SSID').find('essid').text
            
        result += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (bssid, channel, privacy, cipher, auth, dbm, essid_text, manuf, longitude, latitude)
        
    return result

if __name__ == "__main__":
    run()          
