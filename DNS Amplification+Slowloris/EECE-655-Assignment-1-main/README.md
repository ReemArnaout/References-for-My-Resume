Since it is a 20% assignment, I felt like it was only appropriate to do another popular form of DDoS.

DNS AMPLIFICATION:

DNS amplification is a type of distributed denial of service (DDoS) attack that exploits the open nature of 
DNS servers to overwhelm a target with traffic. By sending DNS queries with a spoofed IP address (pretending to be the 
victim's address), attackers can trick DNS servers into sending large responses to the victim. This method is particularly 
dangerous because it uses amplification; the attacker sends small queries but receives much larger responses, 
overwhelming the victim’s resources. Amplification attacks became prominent in the early 2010s, with major incidents in 
2013 targeting banks and governments. Unlike DNS reflection attacks, which simply forward DNS queries to a victim, 
DNS amplification multiplies the attack's power by exploiting DNS servers’ ability to return much larger responses, 
making it significantly more damaging.

SLOWLORIS:

Slowloris is a type of denial-of-service attack designed to keep many connections to the target web server open and hold them open as long as possible. 
By sending partial HTTP requests to the server and never completing them, Slowloris can exhaust the server's available connections, 
preventing legitimate users from establishing new connections. Developed by hacker RSnake in 2009, 
Slowloris gained attention for its ability to perform a DDoS attack with minimal bandwidth usage, 
making it particularly effective against servers that maintain a limited number of concurrent connections. T
he threat posed by Slowloris is particularly acute because it requires fewer resources compared to traditional DDoS attacks, 
allowing attackers to disrupt services even from a home internet connection,
potentially leading to significant downtime and financial losses for targeted organizations.

Hope you enjoy them as much as I did :) Thank you!
