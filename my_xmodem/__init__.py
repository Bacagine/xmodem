# my_xmodem: this program simulate the XMODEM file transfer 
# protocol developed by Ward Christensen in 1977
# 
# Fonts:
# -------
# 1) Xmodem:
#   * https://www.menie.org/georges/embedded/#xmodem
#   * https://www.menie.org/georges/embedded/xmodem_specification.html
#   * http://web.mit.edu/6.115/www/amulet/xmodem.htm
#   * https://www.geeksforgeeks.org/xmodem-file-transfer-protocol/
#   * Source code of xmodem PyPi: 
#     https://files.pythonhosted.org/packages/29/5d/a20d7957f207fc4c4c143881ca7b9617ab7700c153012372ef0a934c7710/xmodem-0.4.6.tar.gz
# 
# 2) Hash: 
#   * https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file#3431838
#   * https://www.geeksforgeeks.org/md5-hash-python/
# 
# Classes:
# ---------
# Xmodem
#   Methods:
#   ---------
#   send                 - Send a file
#   receive              - Receive a file
#   fillPkt              - Fill the packet with '*' character
#   getPacketChecksum    - Get the checksum value of a file
#   verifyPacket - Verify the checksum value of a file is correct
# 
# Desenvelopers: Gustavo Bacagine <gustavo.bacagine@protonmail.com>
#                José Eduardo     <joseeduardoolimpios@gmail.com>
#                Fabricio Freitas <fabricio.gomes4@fatec.sp.gov.br>
# 
# Date: 29/03/2021
# Date of last modification: 15/04/2021

from os import path
from serial import Serial
from hashlib import md5

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
# packtes to send     #
#######################
MAX_QTY_PKT = 255

class Xmodem:
    def __init__(this, fileName, port):
        this.fileName = fileName
        this.port = port

    #####################
    # Send a file to rx #
    #####################
    def send(this):
        # Instance a object of Serial type
        xmodemSend = Serial(this.port)
        
        if xmodemSend.read(1) != NAK:
            print('\033[m1;31E:\033[m NAK not received!')
            return 1

        # Byte 1
        print('Sending the first SOH byte')
        #xmodemSend.write(SOH)
        
        # Quantity of packets to send
        print('Getting the quantity of packages to send')
        #qtyPkts = len(open(this.fileName, 'rb').readlines()) / MIN_LEN_PKT
        qtyPkts = int((path.getsize(this.fileName) * 10) / MIN_LEN_PKT)
        print(f'Quantity of packets = {qtyPkts}')

        # Open the archive to send
        archive = open(this.fileName, 'rb')
        
        # Sending the packets
        count = 0
        while count < qtyPkts:
            xmodemSend.write(SOH)
            print(f'Getting {MIN_LEN_PKT} bytes of the file to send')
            pkt = archive.read(MIN_LEN_PKT)
            
            # Complementing the package
            # with '#'
            while len(pkt) < MIN_LEN_PKT:
                pkt += bytes('#', 'ascii')

            # Number of packet
            pktNumber = count+1
            pktNumber = str(pktNumber)

            # Byte 2 and 3
            xmodemSend.write(pktNumber.encode())
            xmodemSend.write(pktNumber.encode())

            # Byte 4-131
            xmodemSend.write(pkt)
            print(f'Packet nº {pktNumber} sended')
            
            crc = xmodemSend.read(1) # ACK or NAK
            while crc == NAK:
                xmodemSend.write(pkt.encode())
            
            print(f'Count = {count}')
            count += 1
            print(f'count = {count}')
            if count == qtyPkts:
                print('Send EOT to RX')
                xmodemSend.write(EOT)
        
        archive.close()
        xmodemSend.close()
    
    ##########################
    # Receive a file from tx #
    ##########################
    def receive(this):
        xmodemReceive = Serial(this.port)
        
        xmodemReceive.write(NAK)

        #xmodemReceive.write(C)

        # Getting SOH byte
        print('Getting the first SOH byte')
        byte1 = xmodemReceive.read(1)
        print(f'SOH =  {byte1}')
        
        # getting byte 2 and 3
        print('Getting the package number')
        byte2 = xmodemReceive.read(1)
        print(f'Byte 2 = {byte2}')

        byte3 = xmodemReceive.read(1)
        print(f'Byte 3 = {byte3}')

        archive = open(this.fileName, 'wb')
        
        while True:
            print('Downloading the file...')
            # Byte 4-131
            pkt = xmodemReceive.read(MIN_LEN_PKT)
            
            print(f'Lenght of packet = {len(pkt)}') 
            
            # Getting checksum code of 
            # the packet
            chsumCode = this.getPacketChecksum(pkt)
            print(f'Checksum: {chsumCode}')
            
            # Verify packet integrity
            if this.verifyPacket(pkt, chsumCode) == 1:
                xmodemReceive.write(NAK)
            else:
                xmodemReceive.write(ACK)
            '''
            if len(pkt) < MIN_LEN_PKT:
                qtyBytesMissing = MIN_LEN_PKT - len(pkt)
                print(f'Fill the file with {qtyBytesMissing} \'*\' characters')
                this.fillPkt(archive, qtyBytesMissing)
            '''
            archive.write(pkt)
            print(f'Packeage getting')
            byte1 = xmodemReceive.read(1)
            print(f'Byte: {byte1}')
            if byte1 == EOT:
                break

        print('Download finished ;)')

        archive.close()
        xmodemReceive.close()
    
    #######################
    # Get and return the  #
    # cheksum of a packet #
    #######################
    def getPacketChecksum(this, pkt):
        chsumCode = md5(pkt)
        return chsumCode.hexdigest()
        '''
        chsumCode = 0
        for i in pkt.decode():
            chsumCode += ord(i)
        return chsumCode %= 256
        '''
    ####################################
    # Verify the integrity of a packet #
    # using the checksum code          #
    ####################################
    def verifyPacket(this, pkt, chsumCode):
        if this.getPacketChecksum(pkt) != chsumCode:
            return 1
        return 0
    
    #######################################
    # Fill the content of a file with '*' #
    #######################################
    def fillPkt(this, archive, qtyBytesMissing):
        i = 0
        for i in range(0, qtyBytesMissing):
            archive.write('*')

