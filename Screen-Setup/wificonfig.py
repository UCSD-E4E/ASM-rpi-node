import yaml

def wifi_config():
    with open(r'/boot/config.yaml') as configfile: 
        #file1 = yaml.load(configfile, Loader=yaml.FullLoader)
        file1 = yaml.full_load(configfile) #dict type 
        #for key in file1:
            #print(key)
        #print(file1["wifi-setup"]["ssid"])
        ssid = file1["wifi-setup"]["ssid"]
        psk = file1["wifi-setup"]["psw"]
        #print(ssid + ": " + psk)

    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a+") as wpafile:
        wpafile.write("\n")
        wpafile.write("network={")
        wpafile.write("\n")
        wpafile.write("\t" + "ssid=" + r'"'+ ssid + r'"')
        wpafile.write("\n")
        wpafile.write("\t"  + "psk=" + r'"' + psk + r'"') 
        wpafile.write("\n")
        wpafile.write("\t" + "key_mgmt=WPA-PSK")
        wpafile.write("\n")
        wpafile.write("}")
        
wifi_config()
