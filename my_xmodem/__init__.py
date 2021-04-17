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
#   fillPkt              - Fill the packet with '#' character
#   getPacketChecksum    - Get the checksum value of a file
#   verifyPacket - Verify the checksum value of a file is correct
# 
# Desenvelopers: Gustavo Bacagine <gustavo.bacagine@protonmail.com>
#                José Eduardo     <joseeduardoolimpios@gmail.com>
#                Fabricio Freitas <fabricio.gomes4@fatec.sp.gov.br>
# 
# Date: 29/03/2021
# Date of last modification: 17/04/2021

from os import path
from sys import stdout, stderr
from serial import Serial

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
# a packet         #
#####################
MIN_LEN_PKT = 128

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
        
        init = xmodemSend.read(1)

        if init != NAK:
            stderr.write('\033[m1;31E:\033[m NAK not received!\n')
            return 1
        print(f'{init}')

        # Quantity of packets to send
        print('Getting the quantity of packets to send...')
        qtyPkts = int((path.getsize(this.fileName) * 10) / MIN_LEN_PKT)
        print(f'Quantity of packets = {qtyPkts}\n')

        # Open the archive to send
        archive = open(this.fileName, 'rb')
        
        # Sending the packets
        count = 0
        while count < qtyPkts:
            # Byte 1
            print('Sending the SOH byte...')
            xmodemSend.write(SOH)
            print('SOH sended\n')
            
            print(f'Getting {MIN_LEN_PKT} bytes of the file to send')
            pkt = archive.read(MIN_LEN_PKT)
            
            # Complementing the packet
            # with '#'
            print('Verify the length of packet...')
            while len(pkt) < MIN_LEN_PKT:
                #print('Complementing the packet with \'#\' character')
                pkt += bytes('#', 'ascii')
                
            # Number of packet
            pktNumber = count+1
            pktNumber = str(pktNumber)

            # Byte 2 and 3
            print('Send the number of packet...')
            xmodemSend.write(pktNumber.encode())
            '''
            pktNumber = int(pktNumber)
            notPktNumber = ~pktNumber
            notPktNumber = str(notPktNumber)
            xmodemSend.write(notPktNumber.encode(2))
            '''
            print('Send the number of packet again...')
            xmodemSend.write(pktNumber.encode())

            # Byte 4-131
            print('Sending the packet nº {pktNumber}')
            xmodemSend.write(pkt)
            print(f'Packet nº {pktNumber} sended')
            
            # Getting checksum code
            print('Getting the checksum of packet...')
            chsumCode = this.getPacketChecksum(pkt)
            print(f'Checksum: {chsumCode}')
            chsumCode = str(chsumCode) + '\n'
            #chsumCode = str(chsumCode)

            # Send checksum code to RX
            print('Sending checksum to RX')
            #xmodemSend.write(chsumCode.encode())
            xmodemSend.write(chsumCode.encode())

            crc = xmodemSend.read(1) # ACK or NAK
            print(f'Value returned: {crc}')
            while crc == NAK:
                xmodemSend.write(pkt)
            
            count += 1
            if count == qtyPkts:
                print('Sending EOT to RX...')
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
        print('Getting the packet number...')
        byte2 = xmodemReceive.read(1)
        print(f'pktNumber = {byte2}')
        
        print('Getting the packet number again...')
        byte3 = xmodemReceive.read()
        print(f'pktNumber = {byte3}')

        archive = open(this.fileName, 'wb')
        
        while True:
            print('Downloading the file...')
            # Byte 4-131
            pkt = xmodemReceive.read(MIN_LEN_PKT)
            
            # Getting checksum code of 
            # the packet
            chsumCode = int(str(xmodemReceive.readline().decode().replace('\n', '')))
            #chsumCode = xmodemReceive.read().decode()
            #chsumCode = ord(chsumCode)
            print(f'Checksum: {chsumCode}')

            print(f'Lenght of packet = {len(pkt)}') 
            
            
            # Verify packet integrity
            while this.verifyPacket(pkt, chsumCode) == 1:
                xmodemReceive.write(NAK)
            xmodemReceive.write(ACK)
            
            
            archive.write(pkt)
            print(f'Packeage getting')
            byte1 = xmodemReceive.read(1)
            print(f'Byte: {byte1}')
            if byte1 == EOT:
                stdout.write('EOT received ')
                break

        print('Download finished ;)')

        archive.close()
        xmodemReceive.close()
    
    #######################
    # Get and return the  #
    # cheksum of a packet #
    #######################
    def getPacketChecksum(this, pkt):
        #chsumCode = md5(pkt)
        #return chsumCode.hexdigest()
        
        chsumCode = 0
        for i in range(0, len(pkt)):
            chsumCode += pkt[i]
        
        return chsumCode % 256
        
    ####################################
    # Verify the integrity of a packet #
    # using the checksum code          #
    ####################################
    def verifyPacket(this, pkt, chsumCode):
        #if this.getPacketChecksum(pkt) != MAX_QTY_PKT:
        if this.getPacketChecksum(pkt) != chsumCode:
            return 1
        return 0
    
    #######################################
    # Fill the content of a file with '#' #
    #######################################
    '''
    def fillPkt(this, archive, qtyBytesMissing):
        i = 0
        for i in range(0, qtyBytesMissing):
            archive.write('#')
    '''

