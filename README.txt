Program counts number of hops taken and also calculates the RTT to a 
givden host.

Reads Hosts off textfile in the directory.

Uses an ICMP packet to trigger an error resposne which contains part of 
the initial packet as payload. This includes the TTL remaining and is 
used to calulate the hops taken from the client to the host.
