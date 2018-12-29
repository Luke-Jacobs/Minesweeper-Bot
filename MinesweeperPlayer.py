import cv2
import PIL.ImageGrab as ImageGrab
import pyautogui
import numpy as np, time
from constraint import *
from ast import literal_eval as make_tuple
import random

#20 x 20 board
#30 x 29 squares
#180, 102 = start

start = (1140, 103)
mid = (1140+14, 103+14)
jumpX = 30
jumpY = 30
#boardDims = []
dims = (1140, 103, 1140+20*30, 103+20*30)

lookup = {
    (244.0, 244.0, 244.0): -3, #flag
    (0, 0, 0): -2, #bomb
    (220, 220, 220): -1,  #unknown
    (233, 233, 233): 0, #known
    (100, 124, 248): 1,
    (230, 232, 230): 2,
    (208, 18, 18): 3,
    (238, 238, 238): 4,
    (249.0, 210.0, 247.0): 5
}

def saveSnapshot(file):
    screen = ImageGrab.grab(dims)
    screen.save(file)

def getBoard():
    global dims
    return ImageGrab.grab(dims)

def coordToScreen(place):
    global mid, jumpX, jumpY
    x = mid[0]+jumpX*place[0]
    y = mid[1]+jumpY*place[1]
    return x, y

def getPixels(board):
    boardArray = np.zeros([20, 20, 3])
    for x in range(20):
        for y in range(20):
            xloc = mid[0]+jumpX*x
            yloc = mid[1]+jumpY*y
            pix = (xloc, yloc)
            boardArray[x, y] = board.getpixel(pix)
            board.putpixel(pix, (0, 0, 0))
    board.save("ndjfn.png")
    return boardArray

def getNums():
    pixelArray = getPixels(ImageGrab.grab())
    nArray = np.zeros([20, 20], dtype=np.int8)
    for x in range(20):
        for y in range(20):
            nArray[x, y] = lookup[tuple(pixelArray[x, y])]
    return nArray

def getNearSquares(loc): #returns tuple array
    near = []
    ok = [0, 0, 0, 0]
    if loc[0] > 0: #left
        near.append((loc[0]-1, loc[1]))
        ok[0] = 1
    if loc[1] > 0: #up
        near.append((loc[0], loc[1]-1))
        ok[1] = 1
    if loc[0] < 19: #right
        near.append((loc[0]+1, loc[1]))
        ok[2] = 1
    if loc[1] < 19: #down
        near.append((loc[0], loc[1]+1))
        ok[3] = 1
    if ok[0] and ok[1]:
        near.append((loc[0] - 1, loc[1] - 1)) #upper left
    if ok[0] and ok[3]:
        near.append((loc[0] - 1, loc[1] + 1)) #lower left
    if ok[2] and ok[1]:
        near.append((loc[0] + 1, loc[1] - 1)) #upper right
    if ok[2] and ok[3]:
        near.append((loc[0] + 1, loc[1] + 1)) #lower right

    return near

def getNumbered(board): #returns tuple array
    locs = np.where(board > 0)
    out = []
    for i in range(len(locs[0])):
        out.append((locs[0][i], locs[1][i]))
    return out

def getUnknowns(tileArray, board): #returns tuple array
    #feed w/ [(), (), ...]
    unknowns = []
    for tile in tileArray:
        if board[tile] == -1 or board[tile] == -3:
            unknowns.append(tile)
    return unknowns

def setConstraints(board, problem):
    hints = getNumbered(board)
    for hint in hints:
        unknown = getUnknowns(getNearSquares(hint), board)
        unknownVars = [str(item) for item in unknown]
        problem.addConstraint(ExactSumConstraint(board[hint]), unknownVars)
    return problem

def addVars(board, problem):
    varArray = []
    hints = getNumbered(board)
    for hint in hints:
        unknown = getUnknowns(getNearSquares(hint), board)
        varArray += [str(item) for item in unknown]
    varArray = list(set(varArray))
    problem.addVariables(varArray, [0, 1])
    return problem

def parseAnswers(answers):
    if not answers:
        return None
    if len(answers) == 1:
        keywords = answers[0].keys()
        mineProbs = []
        for word in keywords:
            mineProbs.append([word, answers[0][word]])
        return mineProbs
    keywords = answers[0].keys()
    mineProbs = []
    for word in keywords:
        total = 0.0
        for i in range(len(answers)):
            total += answers[i][word]
        total /= len(answers)
        mineProbs.append([word, total])
    return mineProbs

def clickOnSpace(clickType, place):
    #place is simple coord
    pyautogui.moveTo(coordToScreen(place))
    if clickType == "left":
        pyautogui.click()
    else:
        pyautogui.click(button="right")

def execProbArray(mineProbs):
    didSomething = False
    detected = 0
    for tile in mineProbs:
        if tile[1] == 1.0: #100% a bomb
            detected += 1
        #    clickOnSpace("right", make_tuple(tile[0]))
        if tile[1] == 0.0: #0% a bomb
            clickOnSpace("left", make_tuple(tile[0]))
            didSomething = True
    return didSomething, detected

def flagAll(board):
    bombs = np.where(board == -1)
    locs = []
    for i in range(len(bombs[0])):
        x = bombs[0][i]
        y = bombs[1][i]
        clickOnSpace("right", (x, y))

def restartGame():
    pyautogui.moveTo(1438, 64)
    pyautogui.click()
    time.sleep(.5)
    pyautogui.moveTo(1389, 389)
    pyautogui.click()
    time.sleep(.5)

def clickRandom():
    x = random.randint(0, 19)
    y = random.randint(0, 19)
    loc = coordToScreen((x, y))
    pyautogui.moveTo(loc)
    pyautogui.click()
    time.sleep(.5)

def playGame():
    global lookup
    clickRandom()
    mines = 50
    while True:
        data = getNums() #get array of tiles
        problem = Problem() #initialize
        problem = addVars(data, problem)
        problem = setConstraints(data, problem)

        answers = problem.getSolutions() #solve
        print("Possibilities:", len(answers)) #debug
        if answers: #if there is a solution
            mineProbs = parseAnswers(answers) #get prob for each tile
            ok, detected = execProbArray(mineProbs) #if nothing done, quit
            if not ok:
                if detected != 50:
                    clickRandom()
                else:
                    break
        else:
            return -1
    flagAll(data)
    print("Done!")

def snap():
    ImageGrab.grab().save("test2.png")

restartGame()
playGame()

