#!/usr/bin/env python3.13

import socket
import sys
import argparse
from colorama import Fore, Style

# Function to display a banner with tool information
def banner():
    print(Fore.GREEN + r"""
 ▗▄▄▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖     ▗▄▄▄▖▗▖  ▗▖▗▖ ▗▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖  ▗▄▖▗▄▄▄▖▗▄▄▄▖ ▗▄▖ ▗▖  ▗▖
▐▌   ▐▛▚▞▜▌  █  ▐▌ ▐▌    ▐▌   ▐▛▚▖▐▌▐▌ ▐▌▐▛▚▞▜▌▐▌   ▐▌ ▐▌▐▌ ▐▌ █    █  ▐▌ ▐▌▐▛▚▖▐▌
 ▝▀▚▖▐▌  ▐▌  █  ▐▛▀▘     ▐▛▀▀▘▐▌ ▝▜▌▐▌ ▐▌▐▌  ▐▌▐▛▀▀▘▐▛▀▚▖▐▛▀▜▌ █    █  ▐▌ ▐▌▐▌ ▝▜▌
▗▄▄▞▘▐▌  ▐▌  █  ▐▌       ▐▙▄▄▖▐▌  ▐▌▝▚▄▞▘▐▌  ▐▌▐▙▄▄▖▐▌ ▐▌▐▌ ▐▌ █  ▗▄█▄▖▝▚▄▞▘▐▌  ▐
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + "SMTP Enumeration Tool" + Style.RESET_ALL)
    print(Fore.YELLOW + "Author: renegade_hacker" + Style.RESET_ALL)
    print(Fore.YELLOW + "Version: 1.0" + Style.RESET_ALL + "\n")

# Function to test usernames using SMTP VRFY command
def smtp_vrfy(ip, port, username):
    try:
        # Create socket and connect to SMTP server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.recv(1024)  # Read banner

        # Send VRFY command
        s.send(f'VRFY {username}\r\n'.encode())
        result = s.recv(1024).decode()
        s.close()

        # Check for success codes (252 or 250)
        if "252" in result or "250" in result:
            return True, result.strip()
        return False, result.strip()
    except Exception as e:
        return False, f"Error: {str(e)}"

# Function to test usernames using SMTP RCPT command
def smtp_rcpt(ip, port, mail_from, rcpt_to):
    try:
        # Create socket and connect to SMTP server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.recv(1024)  # Read banner

        # SMTP protocol steps
        s.send(b'HELO example.com\r\n')
        s.recv(1024)

        s.send(f'MAIL FROM: <{mail_from}>\r\n'.encode())
        s.recv(1024)

        # Send RCPT command to test user
        s.send(f'RCPT TO: <{rcpt_to}>\r\n'.encode())
        result = s.recv(1024).decode()

        s.send(b'QUIT\r\n')
        s.close()

        # Check for success code (250)
        if "250" in result:
            return True, result.strip()
        return False, result.strip()
    except Exception as e:
        return False, f"Error: {str(e)}"

# Function to test usernames using SMTP EXPN command
def smtp_expn(ip, port, username):
    try:
        # Create socket and connect to SMTP server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.recv(1024)  # Read banner

        # Send EXPN command
        s.send(f'EXPN {username}\r\n'.encode())
        result = s.recv(1024).decode()
        s.close()

        # Check for success code (250)
        if "250" in result:
            return True, result.strip()
        return False, result.strip()
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    # Display banner
    banner()
    
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='SMTP Enumeration Tool')
    parser.add_argument('-t', '--target', required=True, help='Target SMTP server IP')
    parser.add_argument('-p', '--port', type=int, default=25, help='SMTP server port (default: 25)')
    parser.add_argument('-u', '--user', help='Single username to test')
    parser.add_argument('-U', '--userlist', help='File containing list of usernames')
    parser.add_argument('-m', '--method', choices=['vrfy', 'expn', 'rcpt'], default='vrfy',
                        help='Enumeration method (vrfy, expn, rcpt)')
    parser.add_argument('--mail-from', default='test@example.com',
                        help='MAIL FROM address for RCPT method (default: test@example.com)')
    
    args = parser.parse_args()

    # Validate that either single user or userlist is provided
    if not args.user and not args.userlist:
        print(Fore.RED + "[-] Error: You must specify either a single username (-u) or a userlist (-U)" + Style.RESET_ALL)
        sys.exit(1)

    # Read usernames from file or single user
    if args.userlist:
        try:
            with open(args.userlist, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(Fore.RED + f"[-] Error: File {args.userlist} not found" + Style.RESET_ALL)
            sys.exit(1)
    else:
        usernames = [args.user]

    # Print enumeration information
    print(Fore.CYAN + f"[*] Starting SMTP enumeration on {args.target}:{args.port}" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Using method: {args.method.upper()}" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Testing {len(usernames)} users\n" + Style.RESET_ALL)

    valid_users = []

    # Test each username with selected method
    for username in usernames:
        if args.method == 'vrfy':
            success, result = smtp_vrfy(args.target, args.port, username)
        elif args.method == 'expn':
            success, result = smtp_expn(args.target, args.port, username)
        elif args.method == 'rcpt':
            success, result = smtp_rcpt(args.target, args.port, args.mail_from, username)

        # Print results with color coding
        if success:
            print(Fore.GREEN + f"[+] Valid user: {username} - Response: {result}" + Style.RESET_ALL)
            valid_users.append(username)
        else:
            print(Fore.RED + f"[-] Invalid user: {username} - Response: {result}" + Style.RESET_ALL)

    # Print summary of valid users found
    print(Fore.CYAN + f"\n[*] Enumeration completed. Found {len(valid_users)} valid users." + Style.RESET_ALL)
    if valid_users:
        print(Fore.CYAN + "[*] Valid users:" + Style.RESET_ALL)
        for user in valid_users:
            print(Fore.GREEN + f"    {user}" + Style.RESET_ALL)

if __name__ == '__main__':
    main()
