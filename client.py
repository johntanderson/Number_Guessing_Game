import socket
import os

HEADER = 64
SERVER = "127.0.0.1"
PORT = 12007
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))


def get_message():
    while 1:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length and len(msg_length) == HEADER and msg_length.strip().isdigit():
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            return msg.strip()


def send_message(msg):
    message = msg.encode(FORMAT)
    msg_length = str(len(message)).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    client.send(msg_length)
    client.send(message)


def play_game():
    send_message("PlayGame \n")
    get_message()
    while 1:
        guess = input("Input your guess of a number between 1 and 99: ")
        send_message(guess)
        response = get_message()
        if response[0:7] == "CORRECT":
            print("Congrats! You guessed the the number!")
            print(f"Score: {response[8:]}")
            input("Press enter to continue...")
            return
        elif response == "HIGH":
            print("You guessed too high, guess lower")
        else:
            print("You guessed too low, guess higher")


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def check_history():
    ip = input("Enter the IP of the user to search: ")
    clear_console()
    send_message(f"CheckHistory\t{ip}\n")
    response = get_message()
    print(f"History for {ip}:\n")
    print(f"{response}\n\n")
    input("Press enter to continue...")


def check_ind_best_record():
    ip = input("Enter the IP of the user to search: ")
    clear_console()
    send_message(f"CheckIndBestRecord\t{ip}\n")
    response = get_message()
    print(f"Personal Best for {ip}:\n")
    print(f"{response}\n\n")
    input("Press enter to continue...")


def check_best_record():
    send_message(f"CheckBestRecord\n")
    response = get_message()
    print(f"Best Record Ever:\n")
    print(f"{response}\n\n")
    input("Press enter to continue...")


def start():
    while 1:
        clear_console()
        print("1. Play Game")
        print("2. Search History")
        print("3. Search Personal Bests")
        print("4. Best Record Ever")
        print("5. Exit")
        print('\n')

        choice = int(input("Enter your choice: "))
        clear_console()

        if choice == 1:
            play_game()
        elif choice == 2:
            check_history()
        elif choice == 3:
            check_ind_best_record()
        elif choice == 4:
            check_best_record()
        elif choice == 5:
            send_message(DISCONNECT_MSG)
            client.close()
            break
        else:
            print("Invalid Selection!\n\n")
            input("Press enter to continue...")


start()
