import socket
import threading
import random
import math

HEADER = 64
SERVER = "127.0.0.1"
PORT = 12007
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    while 1:
        msg = get_message(conn)
        if msg == DISCONNECT_MSG:
            conn.close()
            print(f"[DISCONNECTED] {addr}")
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
            return
        elif msg == "PlayGame":
            play_game(conn, addr)
        elif msg[0:12] == "CheckHistory":
            msg = msg.split("\t")
            get_history(conn, msg[1])
        elif msg[0:18] == "CheckIndBestRecord":
            msg = msg.split('\t')
            get_personal_best(conn, msg[1])
        elif msg == "CheckBestRecord":
            get_best_record(conn)


def get_message(conn):
    while 1:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length and len(msg_length) == HEADER and msg_length.strip().isdigit():
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            return msg.strip()


def send_message(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = str(len(message)).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    conn.send(msg_length)
    conn.send(message)


def play_game(conn, addr):
    random_number = random.randint(1, 99)
    number_attempts = 0
    send_message(conn, 'Reminder message: "Input your guess of a number between 1 and 99 \n"')
    while 1:
        guess = int(get_message(conn))
        number_attempts += 1
        if guess == random_number:
            score = round(((math.log(random_number, 2))/number_attempts)*100)
            send_message(conn, "CORRECT " + str(score))
            save_game(addr, random_number, number_attempts, score)
            return
        elif guess > random_number:
            send_message(conn, "HIGH")
        else:
            send_message(conn, "LOW")


def get_history(conn, addr):
    result = ""
    count = 0
    for line in open("gameRecord.txt").readlines():
        data = line.strip().split('\t')
        if data[0] == addr:
            count += 1
            result += f"{count}. {data[0]} - {data[3]}\n"
    send_message(conn, result)


def get_personal_best(conn, addr):
    result = 0
    for line in open("gameRecord.txt").readlines():
        data = line.strip().split('\t')
        if data[0] == addr:
            result = int(data[3]) if int(data[3]) > result else result
    send_message(conn, f"1. {addr} - {result}")


def get_best_record(conn):
    result = ["", 0]
    for line in open("gameRecord.txt").readlines():
        data = line.strip().split('\t')
        result[0] = data[0] if int(data[3]) > result[1] else result[0]
        result[1] = int(data[3]) if int(data[3]) > result[1] else result[1]
    send_message(conn, f"1. {result[0]} - {result[1]}")


def save_game(addr, random_number, number_attempts, score):
    db = open("gameRecord.txt", "a")
    db.write(f"{addr[0]}\t{random_number}\t{number_attempts}\t{score}\n")
    db.close()


def start():
    server.listen()
    print(f"[LISTENING] {SERVER}:{PORT}")
    while 1:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[START] server is starting...")
start()
