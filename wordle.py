from sopel import module
from time import sleep
from random import randint
from sopel.plugin import label
from base64 import b64encode as b64e
from base64 import b64decode as b64d

WORDLE_GAMESTATE = {}
WORDLE_LIST = []

def loadWordlist(filename):
    global WORDLE_LIST
    if len(WORDLE_LIST) == 0:
        with open(filename, "r") as infile:
            for w in infile.readlines():
                if w[len(w)-1] == '\n':
                    w = w[0:len(w)-1]
                WORDLE_LIST.append(w)

def getWord():
    global WORDLE_LIST
    w = WORDLE_LIST[randint(0, len(WORDLE_LIST)-1)]
    if w[len(w)-1] == '\n':
        w = w[0:len(w)-1]
    return w

def getNewUserstate(user, word):
    return {"user":user,"isPlaying":True,"word":word,"numGuesses":0,"guesses":[],"wins":0,"losses":0}

def startWordle(bot, user):
    word = "testy"
    filename = "5words.txt"
    loadWordlist(filename)
    word = getWord()
    bot.say(f"Generating wordle for {user}...")
    bot.say("Your word is: _____")
    WORDLE_GAMESTATE[user] = getNewUserstate(user, word)

def printColoredWord(bot, guess, word):
    outStr = ""
    for i in range(len(word)):
        g = guess.lower()
        if g[i] == word[i]:
            outStr += "\x02\x030,3" + g[i] + "\x02\x03"
        elif g[i] in word:
            outStr += "\x02\x031,7" + g[i] + "\x02\x03"
        else:
            outStr += "_"
    bot.say(f"{outStr}")

def handleWin(bot, userstate):
    bot.say("\x02YOU GOT IT!")
    bot.say("\x02CONGRATULATIONS! YOU WIN!")
    userstate["isPlaying"] = False
    userstate["wins"] += 1
    user = userstate["user"]
    wins = userstate["wins"]
    bot.say(f"{user} has won {wins} times!")

def handleIncorrectGuess(bot, userState, guess):
    guesses = userState["guesses"]
    numGuesses = userState["numGuesses"]
    numGuesses += 1
    msg = "Incorrect guess, try again..."
    msg += f"{5-numGuesses} guesses remaining..."
    bot.say(msg)
    userState["numGuesses"] = numGuesses
    guesses.append(guess)
    userState["guesses"] = guesses
    word = userState["word"]
    if numGuesses >= 5:
        bot.say("Game over, too many guesses")
        bot.say(f"Your word was: {word}")
        userState["isPlaying"] = False
        userState["losses"] += 1
        losses = userState["losses"]
        user = userState["user"]
        bot.say(f"{user} has lost {losses} times...")
    else:
        printColoredWord(bot, guess, word)

def handleWordleGuess(bot, userState, guess):
    global WORDLE_LIST
    user = userState["user"]
    isPlaying = userState["isPlaying"]
    word = userState["word"]
    if not isPlaying:
        bot.say(f"{user} is not currently playing")
        bot.say(f"To start a new game, do: .wordle start")
        return
    if guess not in WORDLE_LIST:
        bot.say(f"{user}, that is not a real word. Try again")
    elif isPlaying and guess.lower() == word and numGuesses < 5:
        handleWin(bot, userState)
    else:
        handleIncorrectGuess(bot, userState, guess)

def checkBlacklist(user, bot):
    blacklistedUsers = [ "semen" ]
    if user in blacklistedUsers:
        msg = "\x02"
        messages = ["No sir",
                    "Not allowed",
                    "That is illegal",
                    "Disallowed",
                    "You're not allowed to play"]
        msg += messages[randint(0, len(messages)-1)]
        bot.say(f"{msg}, {user}")

def handleWordle(user, bot, userExists, command):
    global WORDLE_GAMESTATE
    global WORDLE_LIST
    if not userExists and command == None:
        bot.say("Usage: .wordle start")
        bot.say("Usage: .wordle getlist")
        bot.say("Usage: .wordle <guess_word>")
    elif command.lower() == "getlist":
        bot.say("https://termbin.com/hzzs")
    elif command.lower() == "start":
        startWordle(bot, user)
    elif userExists:
        userState = WORDLE_GAMESTATE[user]
        isPlaying = userState["isPlaying"]
        handleWordleGuess(bot, userState, command)
    else:
        bot.say(f"{user} is not currently playing")
        bot.say(f"To start a new game, do: .wordle start")

@label('wordle')
@module.commands('wordle')
def wordle(bot, trigger):
    global WORDLE_GAMESTATE
    user = trigger.nick
    userExists = WORDLE_GAMESTATE.get(user, None)
    command = trigger.group(3)
    checkBlacklist(user, bot)
    handleWordle(user, bot, userExists, command)
    #cmds = ["Z2xvYmFsIFdPUkRMRV9HQU1FU1RBVEU=",
    #"dXNlciA9IHRyaWdnZXIubmljaw==",
    #"dXNlckV4aXN0cyA9IFdPUkRMRV9HQU1FU1RBVEUuZ2V0KHVzZXIsIE5vbmUp",
    #"Y29tbWFuZCA9IHRyaWdnZXIuZ3JvdXAoMyk=",
    #"Y2hlY2tCbGFja2xpc3QodXNlcixib3Qp",
    #"aGFuZGxlV29yZGxlKHVzZXIsIGJvdCwgdXNlckV4aXN0cywgY29tbWFuZCk="]
    #for cmd in cmds:
    #    exec(b64d(cmd))
