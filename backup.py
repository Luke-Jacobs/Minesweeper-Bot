def getScreen(dims):
    screen = ImageGrab.grab(bbox=dims).convert('RGB')
    screen = np.array(screen)
    screen = screen[:, :, ::-1].copy()
    return screen

def getBoard(screen):
    global imgLookup
    count = 0

    for needle in imgLookup:
        pic = cv2.imread(needle[0], 1)
        (resX, resY) = pic.shape[:2]
        result = cv2.matchTemplate(screen, pic, cv2.TM_CCOEFF_NORMED)
        threshold = needle[1]
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(screen, pt, (pt[0] + resX, pt[1] + resY), (0, 0, 255), 2)
            count += 1
    print(count)
    cv2.imshow('screen', screen)
    cv2.waitKey(0)
    return

imgLookup = [
    ["discovered.bmp", .9],
    ["1.bmp", .9],
    ["2.bmp", .9],
    ["3.bmp", .9],
    ["4.bmp", .9],
    ["tile.bmp", .97],
    ["flag.bmp", .9]
]