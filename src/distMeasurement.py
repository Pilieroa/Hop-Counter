#!/usr/bin/python3
import sys
import socket
import select
import struct
import time

def main():
    sites = open("targets.txt", "r").read() #Takes target list and makes it a string
    output = ""
    for server in sites.split(): #turns the targets into a list and probes each
        output = output + probe(server)
    print(output) #prints responses from probes

def probe(hostname, rtt = 2):
    address = socket.gethostbyname(hostname)#gets IP address of hostname
    ttlMax = 255
    payloadStr = 'Packet for measurement purposes. Contact me at afp20@case.edu'
    payload = bytes(payloadStr + 'L'*(1472-len(payloadStr)),'ascii') #creates a padded payload
    
    udp = socket.getprotobyname('udp')#Protoent for UDP format

    recvsock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recvsock.bind(("",0))#Creates a raw socket to recieve ICMP packets and binds it to the default

    #Creates a udp socket to send probe to hostname with specified TTL and payload
    sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
    sendsock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttlMax)
    sendsock.sendto(payload , (address, 33434))

    startTime = time.time()#saves time the packet was sent
    #checks to see if any ICMP packets are recieved to be read
    r, w, x = select.select([recvsock],[],[], rtt)

    sendsock.close()
    
    if recvsock in r:
        #takes data and address tuple of the recieved ICMP packet
        recvPacket, recvAddress = recvsock.recvfrom(540)
        recvsock.close()
        #breaks up the recieved packet into its headers and the payload
        ipHeader = recvPacket[:20]
        icmpHeader = recvPacket[20:28]
        icmpData = recvPacket[28:len(recvPacket)]
        #ensures error message corresponds to the packet I sent
        packetVerification = struct.unpack("!HH", icmpData[22:26])
        if packetVerification[0] == 33434 and packetVerification[1] == 1480:
            #takes the TTL of the packet once it reached the destination and calulates the number of hops taken
            residualTTL, = struct.unpack("!B",icmpData[8:9])
            hops = ttlMax - residualTTL
            #compares current time to start time to compute RTT
            finalRTT = time.time() - startTime
            #checks how many bytes are returned from the original packet
            numBytesKept = len(icmpData)
            return formatOutput(hops, finalRTT, numBytesKept, hostname)
    else:
        recvsock.close()
    #if either checks earlier are false this error message is output
    return "Unable to Probe Host: {} \n \n".format(hostname)

    #Formats all the values that are printed
def formatOutput(hops, rtt, numBytesKept, hostname):
    output1 = "Results for: {} \n".format(hostname)
    output2 = "Number of Hops: {} \n".format(hops)
    output3 = "Round Trip Time: {} \n".format(rtt)
    output4 = "Number of bytes kept: {} \n \n".format(numBytesKept)
    return output1 + output2 + output3 + output4


if __name__ == "__main__":
    main()