#!/usr/bin/python
from lxml import etree
import sys

def run():
    print "[*] NETXML to CSV Converter by Meatballs"
    
    if len(sys.argv) != 3:
        print "[*] Usage: %s input output" % sys.argv[0]
    else:
        output_file_name = sys.argv[2]
        input_file_name = sys.argv[1]
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
            output.write("Item,BSSID,Channel,Privacy,Cipher,Auth,Power,ESSID,Manuf\n")
            result = parse_net_xml(doc)
            output.write(result)
            output.write("\n")
            sys.stdout.write(" Complete.\r\n")
            
def parse_net_xml(doc):
    result = ""

    total = len(list(doc.getiterator("wireless-network")))
    tenth = total/10
    count = 0
    myItem = 1

    for network in doc.getiterator("wireless-network"):
        count += 1
        if (count % tenth) == 0:
            sys.stdout.write(".")
        type = network.attrib["type"]
        channel = network.find('channel').text
        bssid = network.find('BSSID').text
        manuf = network.find('manuf').text

        if network_type == "probe" or channel == "0":
            continue 
        
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
        
                
        power = network.find('snr-info')
        dbm = ""
        if power is not None:
            dbm = power.find('max_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('last_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('min_signal_dbm').text

        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
            essid_text = network.find('SSID').find('essid').text
            
        # print "%s,%s,%s,%s,%s,%s,%s,%s\n" % (bssid, channel, privacy, cipher, auth, dbm, essid_text, manuf)
        result += "%d,%s,%s,%s,%s,%s,%s,%s,%s\n" % (myItem, bssid, channel, privacy, cipher, auth, dbm, essid_text, manuf)
        myItem+=1
        
    return result

if __name__ == "__main__":
    run()          
