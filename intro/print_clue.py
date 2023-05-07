import random
FLAG = open("./message.txt", "r").read()
CLUE = "*" * len(FLAG)
SECRET_LENGHT = 16


flag_blocks = [FLAG[i:i+SECRET_LENGHT] for i in range(0, len(FLAG), SECRET_LENGHT)]

for i in range(SECRET_LENGHT):
    randomBlock = random.randint(0, len(flag_blocks)-2)
    while(flag_blocks[randomBlock][i] == ' '):
        randomBlock = random.randint(0, len(flag_blocks)-2)
    CLUE =  CLUE[:randomBlock*SECRET_LENGHT+i] + flag_blocks[randomBlock][i] + CLUE[randomBlock*SECRET_LENGHT+1 + i:]

print(CLUE)