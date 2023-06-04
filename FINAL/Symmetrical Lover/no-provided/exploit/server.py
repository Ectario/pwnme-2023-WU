from utils import *
import random
from dataclasses import dataclass
from time import sleep
from Crypto.Cipher import AES


def debug(obj, title=""):
    print(
        f"\033[92m{'('+title+')' if title != '' else ''} DEBUG : ",
        str(obj),
        "\033[0m",
    )


@dataclass
class Order:
    materials_mapping = {}  # name      : signature
    materials_quantity = {}  # signature : quantity
    article_counter = 0
    MAX_ARTICLE_NUMBER = 5


class EncSystem:
    def __init__(self, key):
        self.key = key
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, pt, iv):
        pt = padding(pt)
        blocks = blockify(pt)
        xor_block = iv
        ct = []
        for block in blocks:
            ct_block = self.cipher.encrypt(xor(block, xor_block))
            xor_block = xor(block, ct_block)
            ct.append(ct_block)
        return b"".join(ct).hex()

    def decrypt(self, ct, iv):
        ct = bytes.fromhex(ct)
        blocks = blockify(ct)
        xor_block = iv
        pt = []
        for block in blocks:
            pt_block = xor(self.cipher.decrypt(block), xor_block)
            xor_block = xor(block, pt_block)
            pt.append(pt_block)
        return b"".join(pt)

    def sign(self, pt, iv=os.urandom(16)):
        blocks = blockify(bytes.fromhex(self.encrypt(pt, iv)))
        blocks = blocks[len(blocks) // 2 :]
        random.shuffle(blocks)
        ct = blocks[0]
        for i in range(1, len(blocks)):
            ct = xor(blocks[i], ct)
        return ct.hex()


class Session:
    AUTHCODE = os.urandom(16)

    def __init__(self, pseudo: str, encsystem: EncSystem):
        self.encsystem = encsystem
        self.token = self.createToken(True, False, pseudo)
        print(f"\nHi {pseudo}!")
        print(
            f"I'm giving you this authentification code, keep it (you can't regenerate it) : {self.AUTHCODE.hex()}\n"
        )

    def createToken(self, logged, debug, pseudo):
        pseudo = pad(b"pseudo=" + pseudo.encode(), BLOCK_SIZE)[7:].decode()
        session_token = f"{debug=};{pseudo=};{logged=};".encode()
        return self.encsystem.encrypt(session_token, self.AUTHCODE)


def order_materials(order: Order):
    expected = [("needle", 2), ("battery", 1), ("watch-strap", 1), ("watch-dial", 1)]
    for item in expected:
        try:
            item_quantity = order.materials_quantity[
                order.materials_mapping[padding(item[0].encode())]
            ]
            if item[1] != item_quantity:
                print(
                    f"{str(item[0])} doesn't have the right quantity to build the beautiful watch wanted :("
                )
                exit(1)
        except KeyError:
            print(f"A '{str(item[0])}' is needed to build your beautiful watch. You must add it to your basket before ordering.")
            exit(1)
        except Exception as e:
            print("Oh no! We received an error:", e)
            exit(1)
    print(
        "OMG didn't expect such a good order, you deserve the watch, but until the order comes, take this:",
        FLAG,
    )
    exit(0)


def add_item(order: Order, session: Session, debug_mode: bool):
    if order.article_counter < order.MAX_ARTICLE_NUMBER:
        print("What items would you like to add to the watch material list?")
        message = "Material: "
        material = ""
        while material == "":
            material = input(message)
        material = bytes.fromhex(material)
        material_padded = padding(material)
        if material_padded not in order.materials_mapping.keys():
            material_signature = session.encsystem.sign(material, session.AUTHCODE)
            if debug_mode:
                debug(session.encsystem.encrypt(material, session.AUTHCODE), "cipher")
            if material_signature not in order.materials_quantity.keys():
                order.materials_mapping[material_padded] = material_signature
                order.materials_quantity[material_signature] = 1
            else:
                order.materials_quantity[material_signature] += 1
            order.article_counter += 1
        else:
            print("Only different materials are allowed! Leave material for others!")
            exit(1)
    else:
        print("You have already filled the basket.")


def changeInfra():
    global actual_infra
    print(f"Migration from {actual_infra} to {infras[actual_infra]}...", flush=True)
    sleep(2600)
    actual_infra = infras[actual_infra]
    print("Migration done!")


def verify(session: Session) -> dict:
    authcode = bytes.fromhex(
        input("Submit your auth code to prove you're the right person: ")
    )
    session_token = session.encsystem.decrypt(session.token, authcode)
    session_infos = session_token.split(b";")
    checking = {}
    try:
        checking = {
            "logged": session_infos[2].split(b"=")[1].decode(),
            "pseudo": session_infos[1].split(b"=")[1].decode(),
            "debug": session_infos[0].split(b"=")[1].decode(),
        }
    except IndexError:
        checking = {
            "logged": "False",
            "pseudo": "N/A",
            "debug": "False",
        }
    return checking


def listBasket(order: Order):
    print()
    if len(order.materials_mapping.keys()) < 1:
        print("Nothing in your basket!")
        return
    for item in order.materials_mapping.keys():
        print(
            f"- {unpadding(item)} : {order.materials_quantity[order.materials_mapping[item]]}"
        )
    print()


def main():
    encsystem = EncSystem(KEY)
    order = Order()
    pseudo = ""
    while pseudo == "":
        pseudo = input("pseudo : ")
    session = Session(pseudo, encsystem)
    is_session_up = True
    while is_session_up:
        print("Choose an action provided by our service:\n")
        print("1. List your basket")
        print("2. Add an item to the cart")
        print("3. Take order")
        print("4. Leave")
        print("5. Change infra")
        print("-" * len("Choose an action provided by our service:\n"))
        choice = input("Choice: ")
        if choice == "1":
            listBasket(order)
        elif choice == "2":
            session_checking = verify(session)
            if session_checking["logged"] == "True":
                add_item(order, session, session_checking["debug"].strip() == "True")
            else:
                print("Wrong authentification!")
        elif choice == "3":
            order_materials(order)
        elif choice == "4":
            is_session_up = False
        elif choice == "5":
            changeInfra()

    print("Bye bye!")


if __name__ == "__main__":
    main()
