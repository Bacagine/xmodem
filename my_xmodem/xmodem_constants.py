# xmodem_constants.py: Constants useds in xmodem implementation
# 
# Developed by Gustavo Bacagine <gustavo.bacagine@protonmail.com>
# 
# Date: 16/04/2021

##################
# Protocol bytes #
##################
SOH   = b'\x01' # Start of Heading
EOT   = b'\x04' # End of Transmission
ACK   = b'\x06' # Acknowledge
NAK   = b'\x15' # Not Acknowledge
ETB   = b'\x17' # End of Transmission Block (Return to Amulet OS mode)
CAN   = b'\x18' # Cancel
C     = b'\x43' # ASCII "C"

#####################
# Minimal length of #
# a package         #
#####################
MIN_LEN_PKT    = 128

#######################
# Maximal quantity of #
# sends               #
#######################
MAX_SEND_VALUE = 255

