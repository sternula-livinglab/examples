# LivingLab examples
This repo contains a minimal implementation in Python3 of a ship side client and a shore side service callback.

Before using this example, you need to have started the VPN connection to the LivingLab server. The two Python scripts needs the username and password you've received from Sternula to work.

## ship_side_client.py
MMS: python3 ship_side_client.py --user=username --pass=password
VDES: python3 ship_side_client.py --user=username --pass=password --vdes=true

## shore_side_service_callback.py
python3 shore_side_service_callback.py --user=username --pass=password
