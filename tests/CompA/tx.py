#!/usr/bin/python3
# 
# tx.py Test of Send method of Xmodem class
# 
# Date: 29/03/2021
# Date of last modification: 10/04/2021

from sys import argv
from my_xmodem import Xmodem

prog_name = argv[0]
argc = len(argv)

FILE_NAME = 'file.txt'

# Main function
# of TX
def main():
    if argc == 1:
        TX_PORT   = '/dev/pts/'
        
        ptNum = str(input('Type the number of the serial port: '))
        TX_PORT += ptNum

        serTX = Xmodem(FILE_NAME, TX_PORT)
        serTX.send()
    elif argc == 2:
        if argv[1] == '-h' or sys.argv[1] == '--help':
            print(HELP)
        elif argv[1] == '-v' or sys.argv[1] == '--version':
            print(VERSION)
        elif argv[1] == '-p' or sys.argv[1] == '--port':
            PORT = argv[2] # Defining the port
            # Instance a object of 
            # Serial class
            serTX = Xmodem(FILE_NAME, PORT)
            serTX.send()
            
        elif argv[1] == '--license':
            print('This program is a free software licensed under terms of GPLv2')
        elif argv[1] == '--developers':
            developers()
    else:
        sys.stderr.write('\033[1;31mE:\033[m Invalid argument!\n')
        sys.stdout.write('Use ' + prog_name + ' -h for see the help\n')

if __name__ == '__main__':
    main()

