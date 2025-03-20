################################################################################
# Darren Zhang
# Section P
# darrenz
# DINO RUN
################################################################################

import pygame 
import pyaudio
import wave
import sys
import random
import time
import aubio
import numpy as num
import numpy as np
import os.path
import math

################################################################################

#IMAGE CITATIONS

# power-up images from google images
# dino game images from https://github.com/wayou/t-rex-runner

################################################################################
# basic file io from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)
        
################################################################################
# modified beat detecction algorithm from https://github.com/aubio/aubio/blob/master/python/demos/demo_tapthebeat.py#L18

def beatDetection(song):
    win_s = 1024                # fft size
    hop_s = win_s // 2          # hop size
    
    beatList = []
    # create aubio source
    a_source = aubio.source("music" + os.sep + song)
    samplerate = a_source.samplerate
    
    # create aubio tempo detection
    a_tempo = aubio.tempo("default", win_s, hop_s, samplerate) #changle sample rate here
    
    while True:
        samples, read = a_source()
        is_beat = a_tempo(samples)
        if is_beat:
            beatList.append(1)
        else:
            beatList.append(0)
            
        if read < hop_s:
            return beatList, hop_s/samplerate
    
################################################################################
# sorts the scoreboard

def sortScoreboard():
    scores = readFile("scoreboard.txt")
    entrylist = []
    scorelist = []
    allNames = []
    top5 = []
    result = ""
    
    for entry in scores.splitlines():
        name = entry[:entry.find(":")]
        allNames.append(name)
        score = entry[entry.find(":")+1:]
        score = int(score)
        entrylist.append((name, score))
        
    for tup in entrylist:
        scorelist.append(tup[1])
    sortedScores = reversed(sorted(scorelist))
    
    for score in sortedScores:
        for name in allNames:
            if (name, score) in entrylist:
                result = name + ":" + str(score)
                top5.append(result)
                entrylist.remove((name, score))
    top5 = top5[:5]
    result = "\n".join(top5)
    writeFile("scoreboard.txt", result)
    
################################################################################
#draws text
#from https://www.youtube.com/watch?v=dX57H9qecCU&list=PLQVvvaa0QuDdLkP8MrOXLe_rKuf6r80KO&index=5

def textbox(text, font, color):
    textSurf = font.render(text, True, color)
    return textSurf, textSurf.get_rect()
    
################################################################################    
# INITIALIZE GAME STUFF
#font from https://fonts.google.com/specimen/Press+Start+2P?selection.family=Press+Start+2P
gameFont = "gameFont.ttf"

pygame.init()
pygame.display.set_caption('Dino Run')

black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
gray = (211, 211, 211)
green = (0, 200, 0)

width = 1200
height = 500

screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()

inGameSong = None
beat = []
dist = None

background = pygame.image.load("images" + os.sep + "bg.jpeg").convert()
bg = pygame.transform.scale(background, (width, height))

ground = pygame.image.load("images" + os.sep + "ground.png").convert()
grnd = pygame.transform.scale(ground, (width, 100))

score = 0
seconds = 0

oldscores = readFile("scoreboard.txt")
songList = readFile("songlibrary.txt")

class Dino(pygame.sprite.Sprite):
    def __init__(self, x = 10, y = 350, startY = 350): 
        self.x = x
        self.y = y
        self.startY = startY
        
        self.isJump = False
        self.jumpBoost = 0
        self.vel = 0
        self.newvel = 0
        
        self.isDuck = False
        self.invincibility = False
        self.multiplier = 1
        
        self.scaleX = 50
        self.scaleY = 50

        self.dinoUp = pygame.image.load("images" + os.sep + "dinoUp.png").convert_alpha()
        self.dinoDown = pygame.image.load("images" + os.sep + "dinoDown.png").convert_alpha()
        self.dinoUpResize = pygame.transform.scale(self.dinoUp, (self.scaleX, self.scaleY))
        self.dinoDownResize = pygame.transform.scale(self.dinoDown, (self.scaleX, self.scaleY))
        
        self.dinoDuckUp = pygame.image.load("images" + os.sep + "dinoDuckUp.png").convert_alpha()
        self.dinoDuckDown = pygame.image.load("images" + os.sep + "dinoDuckDown.png").convert_alpha()
        self.dinoDuckUpResize = pygame.transform.scale(self.dinoDuckUp, (self.scaleX, self.scaleY))
        self.dinoDuckDownResize = pygame.transform.scale(self.dinoDuckDown, (self.scaleX, self.scaleY))
        
        self.volume = 0
        self.pitch = 0
        
        self.bot = False
        self.rect = pygame.Rect(self.x, self.y, self.scaleX, self.scaleY)
        
    def drawUp(self):
        screen.blit(self.dinoUpResize, (self.x, self.y))
        
        dinoText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitch), dinoText, black)
        textRect1.center = ((self.x + self.scaleX/2), (self.y-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volume), dinoText, black)
        textRect2.center = ((self.x + self.scaleX/2), (self.y-10))
        
        textSurf3, textRect3 = textbox("!!!", dinoText, black)
        textRect3.center = ((self.x + self.scaleX/2), (self.y-30))
        
        textSurf4, textRect4 = textbox("2x", dinoText, black)
        textRect4.center = ((self.x + self.scaleX/2), (self.y-30))
        
        if self.multiplier == 2:
            screen.blit(textSurf4, textRect4)
            
        if self.invincibility:
            screen.blit(textSurf3, textRect3)
            
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        
    def drawDown(self):
        screen.blit(self.dinoDownResize, (self.x, self.y))
        
        dinoText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitch), dinoText, black)
        textRect1.center = ((self.x + self.scaleX/2), (self.y-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volume), dinoText, black)
        textRect2.center = ((self.x + self.scaleX/2), (self.y-10))
        
        textSurf3, textRect3 = textbox("!!!", dinoText, black)
        textRect3.center = ((self.x + self.scaleX/2), (self.y-30))
        
        textSurf4, textRect4 = textbox("2x", dinoText, black)
        textRect4.center = ((self.x + self.scaleX/2), (self.y-30))
        
        if self.multiplier == 2:
            screen.blit(textSurf4, textRect4)
        
        if self.invincibility:
            screen.blit(textSurf3, textRect3)
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        
    def drawDuckUp(self):
        screen.blit(self.dinoDuckUpResize, (self.x, self.y + (50-self.scaleY)))
        
        dinoText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitch), dinoText, black)
        textRect1.center = ((self.x + self.scaleX/2), (self.y-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volume), dinoText, black)
        textRect2.center = ((self.x + self.scaleX/2), (self.y-10))
        
        textSurf3, textRect3 = textbox("!!!", dinoText, black)
        textRect3.center = ((self.x + self.scaleX/2), (self.y-30))
        
        textSurf4, textRect4 = textbox("2x", dinoText, black)
        textRect4.center = ((self.x + self.scaleX/2), (self.y-30))
        
        if self.multiplier == 2:
            screen.blit(textSurf4, textRect4)
        
        if self.invincibility:
            screen.blit(textSurf3, textRect3)
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        
    def drawDuckDown(self):
        screen.blit(self.dinoDuckDownResize, (self.x, self.y + (50-self.scaleY)))
        
        dinoText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitch), dinoText, black)
        textRect1.center = ((self.x + self.scaleX/2), (self.y-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volume), dinoText, black)
        textRect2.center = ((self.x + self.scaleX/2), (self.y-10))
        
        textSurf3, textRect3 = textbox("!!!", dinoText, black)
        textRect3.center = ((self.x + self.scaleX/2), (self.y-30))
        
        textSurf4, textRect4 = textbox("2x", dinoText, black)
        textRect4.center = ((self.x + self.scaleX/2), (self.y-30))
        
        if self.multiplier == 2:
            screen.blit(textSurf4, textRect4)
        
        if self.invincibility:
            screen.blit(textSurf3, textRect3)
            
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
 
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, startX, startY, speed, obsWidth, obsHeight):
        self.startX = startX
        self.startY = startY
        self.speed = speed
        self.obsWidth = obsWidth
        self.obsHeight = obsHeight
        self.pitchNeeded = 400
        self.volumeNeeded = ((((-1+math.sqrt(1-4*(-2*self.obsHeight))/2)//1)/0.3)//1) + 1
        self.rect = pygame.Rect(self.startX, self.startY, self.obsWidth, self.obsHeight)
        self.collidedBefore = False
        
        self.cac = pygame.image.load("images" + os.sep + "cactus1.png").convert_alpha()
        self.cacResize = pygame.transform.scale(self.cac, (self.obsWidth, self.obsHeight))
        
    def draw(self):
        screen.blit(self.cacResize, (self.startX, self.startY))
        
        obsText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitchNeeded), obsText, black)
        textRect1.center = ((self.startX + self.obsWidth/2), (self.startY-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volumeNeeded), obsText, black)
        textRect2.center = ((self.startX + self.obsWidth/2), (self.startY-10))
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        
    def update(self):
        self.startX -= self.speed
      
class Cactus(Obstacle):
    def __init__(self, startX, startY, speed, obsWidth, obsHeight):
        super().__init__(startX, startY, speed, obsWidth, obsHeight)
        
class Bird(Obstacle):
    def __init__(self, startX, startY, speed):
        super().__init__(startX, startY, speed, obsWidth = 50, obsHeight = 50)
        self.birdUp = pygame.image.load("images" + os.sep + "birdUp.png").convert_alpha()
        self.birdDown = pygame.image.load("images" + os.sep + "birdDown.png").convert_alpha()
        self.birdUpResize = pygame.transform.scale(self.birdUp, (self.obsWidth, self.obsHeight))
        self.birdDownResize = pygame.transform.scale(self.birdDown, (self.obsWidth, self.obsHeight))
        
        self.pitchNeeded = 400
        self.volumeNeeded = ((((-1 + math.sqrt(1-4*(2*self.startY - 700))/2) // 1) / 0.3) // 1) + 1
        self.duckPitchNeeded = 200
        
        self.collidedBefore = False
        
    def drawUp(self):
        screen.blit(self.birdUpResize, (self.startX, self.startY))
        obsText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitchNeeded), obsText, black)
        textRect1.center = ((self.startX + self.obsWidth/2), (self.startY-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volumeNeeded), obsText, black)
        textRect2.center = ((self.startX + self.obsWidth/2), (self.startY-10))
        
        textSurf3, textRect3 = textbox("%d" % (self.duckPitchNeeded), obsText, black)
        textRect3.center = ((self.startX + self.obsWidth/2), (self.startY+60))
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        screen.blit(textSurf3, textRect3)
        
    def drawDown(self):
        screen.blit(self.birdDownResize, (self.startX, self.startY))
        obsText = pygame.font.Font(gameFont, 10)
        textSurf1, textRect1 = textbox("%d" % (self.pitchNeeded), obsText, black)
        textRect1.center = ((self.startX + self.obsWidth/2), (self.startY-20))
        
        textSurf2, textRect2 = textbox("%d" % (self.volumeNeeded), obsText, black)
        textRect2.center = ((self.startX + self.obsWidth/2), (self.startY-10))
        
        textSurf3, textRect3 = textbox("%d" % (self.duckPitchNeeded), obsText, black)
        textRect3.center = ((self.startX + self.obsWidth/2), (self.startY+60))
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        screen.blit(textSurf3, textRect3)
        
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, startX, startY, speed, powerWidth, powerHeight):
        self.startX = startX
        self.startY = startY
        self.speed = speed
        self.powerWidth = powerWidth
        self.powerHeight = powerHeight

    def update(self):
        self.startX -= self.speed
        
class ScoreMultiplier(PowerUp):
    def __init__(self, startX, startY, speed):
        super().__init__(startX, startY, speed, powerWidth = 30, powerHeight = 30)
        self.multiplier = 2
        self.multiplierImg = pygame.image.load("images" + os.sep + "2x.png").convert_alpha()
        self.multiplierResize = pygame.transform.scale(self.multiplierImg, (self.powerWidth, self.powerHeight))
        
    def draw(self):
        screen.blit(self.multiplierResize, (self.startX, self.startY))
    
class HealthUp(PowerUp):
    def __init__(self, startX, startY, speed):
        super().__init__(startX, startY, speed, powerWidth = 30, powerHeight = 30)
        self.healthIncrease = 50
        self.healthImg = pygame.image.load("images" + os.sep + "healthup.jpg").convert_alpha()
        self.healthResize = pygame.transform.scale(self.healthImg, (self.powerWidth, self.powerHeight))
        
    def draw(self):
        screen.blit(self.healthResize, (self.startX, self.startY))
        
class Invincibility(PowerUp):
    def __init__(self, startX, startY, speed):
        super().__init__(startX, startY, speed, powerWidth = 30, powerHeight = 30)
        self.invImg = pygame.image.load("images" + os.sep + "inv.png").convert_alpha()
        self.invResize = pygame.transform.scale(self.invImg, (self.powerWidth, self.powerHeight))
        
    def draw(self):
        screen.blit(self.invResize, (self.startX, self.startY))
        
################################################################################
# RUNS SCOREBOARD

def scoreboard():
    inScoreboard = True
    sortScoreboard()
    currScoreboard = readFile("scoreboard.txt")
    while inScoreboard:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        screen.fill(white)
        
        scoresText = pygame.font.Font(gameFont, 50)
        menuText = pygame.font.Font(gameFont, 25)
        
        textSurf1, textRect1 = textbox("Name", scoresText, black)
        namePos = (width*.05, height*.05)
        screen.blit(textSurf1, namePos)
        
        textSurf2, textRect2 = textbox("Score", scoresText, black)
        scorePos = (width*.7, height*.05)
        screen.blit(textSurf2, scorePos)
        
        for i in range(len(currScoreboard.splitlines())):
            name = currScoreboard.splitlines()[i][:currScoreboard.splitlines()[i].find(":")]
            score = currScoreboard.splitlines()[i][currScoreboard.splitlines()[i].find(":")+1:]
            
            textSurf3, textRect3 = textbox(name, scoresText, black)
            Pos1 = (width*.05, height*(.2 + .15*i))
            screen.blit(textSurf3, Pos1)
            
            textSurf4, textRect4 = textbox(score, scoresText, black)
            Pos2 = (width*.7, height*(.2 + .15*i))
            screen.blit(textSurf4, Pos2)
            
        if 995<mouse[0]<1190 and 450<mouse[1]<500:
            textSurf5, textRect5 = textbox("Menu", scoresText, red)
            if click[0] == 1:
                inScoreboard = False
                menu()
        else:
            textSurf5, textRect5 = textbox("Menu", scoresText, black)
        menuPos = (width*.83, height*.9)
        screen.blit(textSurf5, menuPos)
        
        if 10<mouse[0]<260 and 450<mouse[1]<500:
            textSurf6, textRect6 = textbox("Clear", scoresText, red)
            if click[0] == 1:
                writeFile("scoreboard.txt", "")
                currScoreboard = readFile("scoreboard.txt")
        else:
            textSurf6, textRect6 = textbox("Clear", scoresText, black)
        clearPos = (width*.01, height*.9)
        screen.blit(textSurf6, clearPos)
    
        pygame.display.update()
        clock.tick(60)
    
################################################################################
# RUNS DEATH SCREEN

def deathScreen():
    global seconds
    global score
    global oldscores
    inDeath = True
    name = ""
    while inDeath:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == 8 and len(name) >= 1:
                    name = name[:-1]
                elif event.key == 13 and len(name) >= 1:
                    if len(oldscores) == 0:
                        entry = name + ":" + str(score)
                        score = 0
                        seconds = 0
                        writeFile("scoreboard.txt", entry)
                        inDeath = False
                        scoreboard()
                    else:
                        entry = "\n" + name + ":" + str(score)
                        score = 0
                        seconds = 0
                        oldscores = readFile("scoreboard.txt")
                        newscores = oldscores + entry
                        writeFile("scoreboard.txt", newscores)
                        inDeath = False
                        scoreboard()
                else:
                    name += event.unicode
                    
        gameOverText = pygame.font.Font(gameFont, 50)
        smallerText = pygame.font.Font(gameFont, 25)
        enterNameText = pygame.font.Font(gameFont, 15)
        
        screen.fill(gray)
        
        textSurf1, textRect1 = textbox("GAME OVER", gameOverText, black)
        textRect1.center = ((width/2), (height/4))
        
        textSurf2, textRect2 = textbox("Seconds Survived: %d" % (seconds), smallerText, black)
        textRect2.center = ((width/2), (height*2/5))
        
        textSurf3, textRect3 = textbox("Score: %d" % (score), smallerText, black)
        textRect3.center = ((width/2), (height*2/5+30))
        
        textSurf4, textRect4 = textbox("Type your name below and press enter to view the scoreboard ", enterNameText, black)
        textRect4.center = ((width/2), (height*2/5+100))
        
        textSurf5, textRect5 = textbox("Name: %s" % (name), smallerText, black)
        textRect5.center = ((width/2), (height*2/5+150))
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        screen.blit(textSurf3, textRect3)
        screen.blit(textSurf4, textRect4)
        screen.blit(textSurf5, textRect5)
        
        pygame.display.update()
        clock.tick(60)

################################################################################
# RUNS MAIN GAME CODE
    
def main():
    gameOver = False
    paused = False
    obstacles = []
    
    if inGameSong != None:
        pygame.mixer.music.load("music" + os.sep + inGameSong)
        pygame.mixer.music.play(-1) #plays music that is loaded
    
    # PyAudio initializing from https://github.com/aubio/aubio/issues/78 
    # PyAudio object.
    p = pyaudio.PyAudio()
    
    # Open stream.
    stream = p.open(format=pyaudio.paFloat32,
        channels=1, rate=44100, input=True,
        frames_per_buffer=1024)
    
    # Aubio's pitch detection.
    pDetection = aubio.pitch("default", 2048,
        2048//2, 44100)
    # Set unit.
    pDetection.set_unit("Hz")
    pDetection.set_silence(-40)
    
    #makes an instance of a dino
    dino = Dino()
    
    health = 200 #200
    healthStartX = width*.01
    healthStartY = height*.1
    healthHeight = 15
    
    if inGameSong == None:
        cactusStartx = width
        cactusStarty = random.randint(350, 390) 
        cactusSpeed = 5
        cactusWidth = random.randint(20, 30)
        cactusHeight = 400 - cactusStarty
        cactus = Cactus(cactusStartx, cactusStarty, cactusSpeed, cactusWidth, cactusHeight)
        obstacles.append(cactus)

    timePassed = 0
    difficulty = 0
    multiTime = 0
    invTime = 0
    detection = 50
    extraHeight = 50
    clickDelay = 0
    pauseTime = 0
    
    global score
    global seconds
    global beat
    global dist
    
    score = 0
    seconds = 0
    index = 0
    shift = 0
    start = time.time()

    while not gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == "p" and not paused:
                    pygame.mixer.music.pause()
                    paused = True
                    pauseStart = time.time()
                elif event.unicode == "p" and paused:
                    pygame.mixer.music.unpause()
                    paused = False
                    pauseEnd = time.time()
                    pauseTime += (pauseEnd - pauseStart)
                elif event.key == 27 and paused:
                    gameOver = False
                    menu()
                    
        if not paused:
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            timePassed += 1
            
            screen.fill(white)
            
            obschance = random.randint(1, 100)
            powerchance = random.randint(1, 100)
            spawnpower = random.randint(1, 3)
            pitchUp = random.randint(1, 10)
            volumeUp = random.randint(1, 10)
            
            if timePassed % 10 == 0:
                score += dino.multiplier
                
            if timePassed % 60 == 0:
                seconds += 1
                
            if timePassed % 1800 == 0: 
                difficulty += 1
                if difficulty < 10:
                    detection += 7
                    extraHeight += 5
                if difficulty >= 10 < 20:
                    detection += 10
                if difficulty >= 20:
                    detection += 15
                    
            if inGameSong == None:
                if timePassed % (240 - difficulty*5) == 0: 
                    if 1 <= obschance <= 70: #create a cactus
                        cactusStartx = width
                        cactusStarty = random.randint(350 - difficulty*5, 390 - difficulty*5) 
                        cactusSpeed = 5 + difficulty
                        cactusWidth = random.randint(20 + difficulty*5, 30 + difficulty*5)
                        cactusHeight = 400 - cactusStarty
                        cactus = Cactus(cactusStartx, cactusStarty, cactusSpeed, cactusWidth, cactusHeight)
                        obstacles.append(cactus)
                    elif 70 < obschance <= 100: #create a bird
                        birdStartx = width
                        birdStarty = random.randint(10 + 5*difficulty, 350 - 2*difficulty) 
                        birdSpeed = 5 + difficulty
                        bird = Bird(birdStartx, birdStarty, birdSpeed)
                        obstacles.append(bird)
                        
            if inGameSong != None:
                now = time.time() - pauseTime
                if now - start >= dist:
                    index += 1
                    if beat[index % len(beat)] == 1:
                        if 1 <= obschance <= 70: #create a cactus
                            cactusStartx = width
                            cactusStarty = random.randint(350 - difficulty*5, 390 - difficulty*5) 
                            cactusSpeed = 5 + difficulty
                            cactusWidth = random.randint(20 + difficulty*5, 30 + difficulty*5)
                            cactusHeight = 400 - cactusStarty
                            cactus = Cactus(cactusStartx, cactusStarty, cactusSpeed, cactusWidth, cactusHeight)
                            obstacles.append(cactus)
                        elif 70 < obschance <= 100: #create a bird
                            birdStartx = width
                            birdStarty = random.randint(10 + 5*difficulty, 350 - 2*difficulty) 
                            birdSpeed = 5 + difficulty
                            bird = Bird(birdStartx, birdStarty, birdSpeed)
                            obstacles.append(bird)
                    start = time.time()  - pauseTime
                    
            if timePassed % 300 == 0:
                if spawnpower == 1:  
                    if 1 <= powerchance <= 30: #create multiplier powerup
                        multiplierStartx = width
                        multiplierStarty = random.randint(10, 350) 
                        multiplierSpeed = 5 + difficulty
                        scoreMultiplier = ScoreMultiplier(multiplierStartx, multiplierStarty, multiplierSpeed)
                        obstacles.append(scoreMultiplier)
                    elif 30 < powerchance <= 70: #create healthup powerup
                        healthupStartx = width
                        healthupStarty = random.randint(10, 350) 
                        healthupSpeed = 5 + difficulty
                        healthup = HealthUp(healthupStartx, healthupStarty, healthupSpeed)
                        obstacles.append(healthup)
                    elif 70 < powerchance <= 100: #create invincibility powerup
                        invStartx = width
                        invStarty = random.randint(10, 350) 
                        invSpeed = 5 + difficulty
                        inv = Invincibility(invStartx, invStarty, invSpeed)
                        obstacles.append(inv)
                    
            if dino.y + 50 < 0 and timePassed % 3 == 0 and not dino.invincibility:
                health -= (1 + difficulty)
            if health <= 0:
                gameOver = True
                pygame.mixer.music.stop()
                deathScreen()
            
            for obs in obstacles[-10:]: 
                dino.rect = pygame.Rect(0, dino.y, dino.scaleX, dino.scaleY)
                if isinstance(obs, Obstacle):
                    obs.rect = pygame.Rect(obs.startX, obs.startY, obs.obsWidth, obs.obsHeight)
                else:
                    obs.rect = pygame.Rect(obs.startX, obs.startY, obs.powerWidth, obs.powerHeight)
                if isinstance(obs, Obstacle) and obs.collidedBefore == False \
                and dino.rect.colliderect(obs.rect) and not dino.invincibility:
                    obs.collidedBefore = True
                    obs.update()
                    health -= (5 + difficulty)
                else:
                    if isinstance(obs, PowerUp) and dino.rect.colliderect(obs.rect):
                        if isinstance(obs, HealthUp):
                            health += obs.healthIncrease
                            obstacles.remove(obs)
                        elif isinstance(obs, ScoreMultiplier):
                            dino.multiplier = 2
                            obstacles.remove(obs)
                        elif isinstance(obs, Invincibility):
                            dino.invincibility = True
                            obstacles.remove(obs)
                    elif isinstance(obs, Bird):
                        if 0 <= timePassed % 30 <= 15:
                            obs.drawUp()
                        else:
                            obs.drawDown()
                    else:
                        obs.draw()
                    obs.update()
                    
            if dino.multiplier == 2:
                multiTime += 1 
                if multiTime % (60*15) == 0:
                    dino.multiplier = 1
                    multiTime = 0
            
            if dino.invincibility:
                invTime += 1
                if invTime % (60*15) == 0:
                    dino.invincibility = False
                    invTime = 0
            
            screen.blit(grnd, (0, height - 100))
            pygame.draw.line(screen, black, (0, height - 100), (width, height - 100))
            
            # from https://github.com/aubio/aubio/issues/78 
            # pitch and volume detection, less laggy when put here
            data = stream.read(1024)
            samples = num.fromstring(data,
                dtype=aubio.float_type)
            pitch = pDetection(samples)[0]//1
            volume = num.sum(samples**2)/len(samples)
            volume = volume*(10**(3.5)) // 1
            if volume > 100:
                volume = 100
            
            dino.jumpBoost = 0.3*volume
            
            if not dino.bot: #not using a bot
                dino.pitch = pitch
                dino.volume = volume
                #JUMP IMPLEMENTATION
                if dino.isJump == False and volume > 0 and pitch > 400:  
                    dino.isJump = True
                    dino.vel = dino.jumpBoost
                    
                if dino.isJump and not dino.isDuck:
                    dino.vel -= 1
                    dino.y -= dino.vel
                    if dino.y >= dino.startY:
                        dino.y = dino.startY
                        dino.isJump = False
                        dino.vel = 0
                
                #DUCK IMPLEMENTATION
                if not dino.isDuck and not dino.isJump and volume > 0 and pitch < 200 :  
                    dino.isDuck = True
                    dino.scaleX = 60
                    dino.scaleY = 30
                    dino.dinoDuckUpResize = pygame.transform.scale(dino.dinoDuckUp, (dino.scaleX, dino.scaleY))
                    dino.dinoDuckDownResize = pygame.transform.scale(dino.dinoDuckDown, (dino.scaleX, dino.scaleY))
                    dino.rect = pygame.Rect(dino.x, dino.y, dino.scaleX, dino.scaleY)
                    
                if dino.isDuck:
                    if volume == 0:
                        dino.isDuck = False
                        dino.scaleX = 50
                        dino.scaleY = 50
            
            if dino.bot: #using bot
                if dino.isDuck:
                    dino.isDuck = False
                if shift < len(obstacles):
                    obs = obstacles[shift]
                    if isinstance(obs, Obstacle):
                        if isinstance(obs, Cactus):
                            if 0 <= obs.startX - dino.x <= detection and not dino.isJump:
                                dino.pitch = obs.pitchNeeded + pitchUp
                                dino.volume = obs.volumeNeeded + volumeUp
                                dino.isJump = True
                                dino.vel = 0
                                while 0.5*(dino.vel**2 + dino.vel) <= (400 - obs.startY) + extraHeight:
                                    dino.vel += 1 
                            if dino.isJump:
                                dino.y -= dino.vel
                                dino.vel -= 1
                                if dino.y >= dino.startY:
                                    dino.y = dino.startY
                                    dino.isJump = False
                                    dino.vel = 0
                                    shift += 1
                            elif obs.startX + obs.obsWidth < dino.x:
                                shift += 1
                        elif isinstance(obs, Bird):
                            if 0 <= obs.startX - dino.x <= detection and not dino.isJump and dino.y <= obs.startY + extraHeight:
                                dino.pitch = obs.pitchNeeded + pitchUp
                                dino.volume = obs.volumeNeeded + volumeUp
                                dino.isJump = True
                                dino.vel = 0
                                while 0.5*(dino.vel**2 + dino.vel) <= (400 - obs.startY) + extraHeight:
                                    dino.vel += 1 
                            if dino.isJump:
                                dino.y -= dino.vel
                                dino.vel -= 1
                                if dino.y >= dino.startY:
                                    dino.y = dino.startY
                                    dino.isJump = False
                                    dino.vel = 0
                                    shift += 1
                            elif obs.startX + obs.obsWidth < dino.x:
                                shift += 1
                    elif isinstance(obs, PowerUp):
                        if obs.startX + obs.powerWidth < dino.x:
                            shift += 1
            
            if 0 <= timePassed % 30 < 15 and dino.isDuck == False:
                dino.drawUp()
            elif 15 <= timePassed % 30 <= 29 and dino.isDuck == False:
                dino.drawDown()
            elif 0 <= timePassed % 30 < 15 and dino.isDuck == True:
                dino.drawDuckUp()
            elif 15 <= timePassed % 30 <= 29 and dino.isDuck == True:
                dino.drawDuckDown()
    
            smallerText = pygame.font.Font(gameFont, 15)
    
            textSurf1, textRect1 = textbox("Time:%d" % (seconds) , smallerText, black)
            timePos = (width*.85, height*.05)
            screen.blit(textSurf1, timePos)
            
            textSurf2, textRect2 = textbox("Score:%d" % (score) , smallerText, black)
            scorePos = (width*.85, height*.1)
            screen.blit(textSurf2, scorePos)
            
            textSurf5, textRect5 = textbox("Health", smallerText, black)
            healthPos = (width*.01, height*.05)
            screen.blit(textSurf5, healthPos)
            
            if 10 < mouse[0] < 145 and 75 <mouse[1] < 90:
                textSurf6, textRect6 = textbox("Bot:%r" % (dino.bot), smallerText, red)
                if click[0] == 1 and clickDelay == 0:
                    clickDelay += 60
                    dino.bot = not dino.bot
            else:
                textSurf6, textRect6 = textbox("Bot:% r" % (dino.bot), smallerText, black)
            activatePos = (width*.01, height*.15)
            screen.blit(textSurf6, activatePos)
            
            if clickDelay > 0:
                clickDelay -= 10
                if clickDelay < 0:
                    clickDelay = 0
    
            pygame.draw.rect(screen, black, [healthStartX, healthStartY, health, healthHeight])
            pygame.display.update()
            
            clock.tick(60)
            
        else:
            pausedText = pygame.font.Font(gameFont, 50)
            textSurf7, textRect7 = textbox("PAUSED", pausedText, black)
            textRect7.center = ((width/2), (height/2-20))
            
            screen.blit(textSurf7, textRect7)
            
            pygame.display.update()
            
            clock.tick(60)
            
################################################################################
# RUNS DIRECTIONS SCREEN

def directions():
    inDirections = True
    while inDirections:
        direcText = pygame.font.Font(gameFont, 15)
        menuText = pygame.font.Font(gameFont, 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        screen.fill(white)

        textSurf2, textRect2 = textbox("This game is entirely controlled by your voice! On top of the dinosaur", direcText, black)
        text2Pos = (width*.01, height*.05)
        textSurf3, textRect3 = textbox("will be 2 numbers. The top number displays your current pitch and the bottom", direcText, black)
        text3Pos = (width*.01, height*.09)
        
        textSurf4, textRect4 = textbox("number displays your current volume. To jump, your pitch needs to be greater", direcText, black)
        text4Pos = (width*.01, height*.13)
        
        textSurf5, textRect5 = textbox("than 400. To duck, your pitch needs to be lower than 200. When you are required", direcText, black)
        text5Pos = (width*.01, height*.17)
        
        textSurf6, textRect6 = textbox("to jump, the volume needed to get over will be displayed on the obstacle. There", direcText, black)
        text6Pos = (width*.01, height*.21)
        
        textSurf7, textRect7 = textbox("are also 3 powerups you can get in this game: health up, invincibility, and 2x", direcText, black)
        text7Pos = (width*.01, height*.25)
        
        textSurf8, textRect8 = textbox("multiplier. The health up gives a flat 50 extra health while the invincibility", direcText, black)
        text8Pos = (width*.01, height*.29)
        
        textSurf9, textRect9 = textbox("and 2x multiplier only last for 15 seconds. You start with 200 health and the", direcText, black)
        text9Pos = (width*.01, height*.33)
        
        textSurf10, textRect10 = textbox("game difficulty gets harder. The obstacles spawn faster and they move faster.", direcText, black)
        text10Pos = (width*.01, height*.37)
        
        textSurf11, textRect11 = textbox("In addition, you will take more damage when you get hit by them. You will also", direcText, black)
        text11Pos = (width*.01, height*.41)
        
        textSurf12, textRect12 = textbox("take damage when the dinosaur goes off the screen.", direcText, black)
        text12Pos = (width*.01, height*.45)
        
        textSurf13, textRect13 = textbox("If you want to listen to music at the same time, you can go to the songs", direcText, black)
        text13Pos = (width*.01, height*.54)
        
        textSurf14, textRect14 = textbox("menu and upload your favorite song. The obstacles will now generate based", direcText, black)
        text14Pos = (width*.01, height*.58)
        
        textSurf15, textRect15 = textbox("on the beat of the song. Press p at anytime to pause the game and", direcText, black)
        text15Pos = (width*.01, height*.62)
        
        textSurf16, textRect16= textbox("escape to go back to the menu.", direcText, black)
        text16Pos = (width*.01, height*.66)
        
        textSurf17, textRect17 = textbox("There is also another cool feature in this game. In the top left corner, you ", direcText, black)
        text17Pos = (width*.01, height*.74)
        
        textSurf18, textRect18 = textbox("will see a button that allows you to turn on a bot. If you decide to turn it", direcText, black)
        text18Pos = (width*.01, height*.78)
        
        textSurf19, textRect19 = textbox("on, it will play the game for you :)", direcText, black)
        text19Pos = (width*.01, height*.82)
        
        screen.blit(textSurf2, text2Pos)
        screen.blit(textSurf3, text3Pos)
        screen.blit(textSurf4, text4Pos)
        screen.blit(textSurf5, text5Pos)
        screen.blit(textSurf6, text6Pos)
        screen.blit(textSurf7, text7Pos)
        screen.blit(textSurf8, text8Pos)
        screen.blit(textSurf9, text9Pos)
        screen.blit(textSurf10, text10Pos)
        screen.blit(textSurf11, text11Pos)
        screen.blit(textSurf12, text12Pos)
        screen.blit(textSurf13, text13Pos)
        screen.blit(textSurf14, text14Pos)
        screen.blit(textSurf15, text15Pos)
        screen.blit(textSurf16, text16Pos)
        screen.blit(textSurf17, text17Pos)
        screen.blit(textSurf18, text18Pos)
        screen.blit(textSurf19, text19Pos)
                
        if 995 < mouse[0] < 1190 and 450 < mouse[1] < 500:
            textSurf1, textRect1 = textbox("Menu", menuText, red)
            if click[0] == 1:
                inSongs = False
                menu()
        else:
            textSurf1, textRect1 = textbox("Menu", menuText, black)
        menuPos = (width*.83, height*.9)
        screen.blit(textSurf1, menuPos)
        
        pygame.display.update()
        clock.tick(60)

################################################################################
# RUNS SONGS SCREEN

def songs():
    inSongs = True
    songname = ''
    validSong = None
    cleared = False
    clearTime = 0
    unload = False
    unloadTime = 0
    loadTime = 0
    global inGameSong
    global beat
    global dist
    global songList
    while inSongs:
        bigText = pygame.font.Font(gameFont, 50)
        songText = pygame.font.Font(gameFont, 15)
        menuText = pygame.font.Font(gameFont, 50)
        smallerText = pygame.font.Font(gameFont, 25)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == 8 and len(songname) >= 1:
                    songname = songname[:-1]
                elif event.key == 13 and len(songname) >= 1:
                    if songname in os.listdir("music"):
                        inGameSong = songname
                        songList = readFile("songlibrary.txt")
                        if len(songList) == 0:
                            beat, dist = beatDetection(songname)
                            newSong = "{'%s':[%s,%d]}" % (songname, str(beat), dist)
                            songList += newSong
                            writeFile("songlibrary.txt", songList)
                        else:
                            songList = eval(songList) 
                            if songname in songList:
                                beat = songList[songname][0]
                                dist = songList[songname][1]
                            else:
                                beat, dist = beatDetection(songname)
                                songList[songname] = [beat, dist]
                                songList = str(songList)
                                writeFile("songlibrary.txt", songList)
                        validSong = True
                    else:
                        validSong = False
                else:
                    songname += event.unicode
                
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        screen.fill(white)
        
        textSurf1, textRect1 = textbox("Songs", bigText, black)
        textRect1.center = ((width/2), (height*.1))
        screen.blit(textSurf1, textRect1)
        
        if 995 < mouse[0] < 1190 and 450 < mouse[1] < 500:
            textSurf2, textRect2 = textbox("Menu", menuText, red)
            if click[0] == 1:
                inSongs = False
                menu()
        else:
            textSurf2, textRect2 = textbox("Menu", menuText, black)
        menuPos = (width*.83, height*.9)
        screen.blit(textSurf2, menuPos)
        
        textSurf3, textRect3 = textbox("%s" % (songname), smallerText, black)
        textRect3.center = ((width/2), (height/2))
        
        textSurf4, textRect4 = textbox("To upload your own song, drag your wav file into the music folder and then", songText, black)
        textRect4.center = ((width/2), (height/4))
        
        textSurf5, textRect5 = textbox("type the name below (remember to include .wav in the name)", songText, black)
        textRect5.center = ((width/2), (height/4+15))
        
        screen.blit(textSurf3, textRect3)
        screen.blit(textSurf4, textRect4)
        screen.blit(textSurf5, textRect5)
        
        textSurf6, textRect6 = textbox("Song Loaded!", smallerText, green)
        textRect6.center = ((width/2), (height/2+30))
        
        textSurf7, textRect7 = textbox("Song Not Found", smallerText, red)
        textRect7.center = ((width/2), (height/2+30))
        
        textSurf9, textRect9 = textbox("Cleared!", smallerText, green)
        textRect9Pos = (width*.01, height*.85)
        
        textSurf11, textRect11 = textbox("Unloaded!", smallerText, green)
        textRect11Pos = (width*.4, height*.85)
        
        if validSong == True:
            loadTime += 1
            screen.blit(textSurf6, textRect6)
            if loadTime == 180:
                loadTime = 0
                validSong = None
            
        if validSong == False:
            screen.blit(textSurf7, textRect7)
            loadTime += 1
            if loadTime == 180:
                loadTime = 0
                validSong = None
            
        if 10<mouse[0]<260 and 450<mouse[1]<500:
            textSurf8, textRect8 = textbox("Clear", bigText, red)
            if click[0] == 1:
                writeFile("songlibrary.txt", "")
                cleared = True
        else:
            textSurf8, textRect8 = textbox("Clear", bigText, black)
        clearPos = (width*.01, height*.9)
        screen.blit(textSurf8, clearPos)
        
        if 475<mouse[0]<775 and 450<mouse[1]<500:
            textSurf10, textRect10= textbox("Unload", bigText, red)
            if click[0] == 1 and inGameSong != None:
                inGameSong = None
                unload = True
        else:
            textSurf10, textRect10 = textbox("Unload", bigText, black)
        unloadPos = (width*.4, height*.9)
        screen.blit(textSurf10, unloadPos)
        
        if cleared:
            clearTime += 1
            screen.blit(textSurf9, textRect9Pos)
            if clearTime == 180:
                clearTime = 0
                cleared = False
                
        if unload:
            unloadTime += 1
            screen.blit(textSurf11, textRect11Pos)
            if unloadTime == 180:
                unloadTime = 0
                unload = False
            
        pygame.display.update()
        clock.tick(60)
    
################################################################################
# RUNS MENU SCREEN

def menu():
    inMenu = True
    while inMenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
    
        screen.blit(bg, (0, 0))
        bigText = pygame.font.Font(gameFont, 35)
        smallText = pygame.font.Font(gameFont, 20)
        textSurf1, textRect1 = textbox("Dino Run", bigText, black)
        textRect1.center = ((width/2), (height*.1))
        
        if 355 < mouse[0] < 440 and 140 < mouse[1] < 160:
            textSurf2, textRect2 = textbox("Play", smallText, red)
            if click[0] == 1:
                inMenu = False
                main()
        else:
            textSurf2, textRect2 = textbox("Play", smallText, black)
        textRect2.center = ((width/3), (height*.3))
        
        if 695 < mouse[0] < 900 and 140 < mouse[1] < 160: 
            textSurf3, textRect3 = textbox("Directions", smallText, red)
            if click[0] == 1:
                inMenu = False
                directions()
        else:
            textSurf3, textRect3 = textbox("Directions", smallText, black)
        textRect3.center = ((width*2/3), (height*.3))
        
        if 295 < mouse[0] < 500 and 190 < mouse[1] < 210:
            textSurf4, textRect4 = textbox("Scoreboard", smallText, red)
            if click[0] == 1:
                inMenu = False
                scoreboard()
        else:
            textSurf4, textRect4 = textbox("Scoreboard", smallText, black)
        textRect4.center = ((width/3), (height*.4))
        
        if 745 < mouse[0] < 850 and 190 < mouse[1] < 210:
            textSurf5, textRect5 = textbox("Songs", smallText, red)
            if click[0] == 1:
                inMenu = False
                songs()
        else:
            textSurf5, textRect5 = textbox("Songs", smallText, black)
        textRect5.center = ((width*2/3), (height*.4))
        
        screen.blit(textSurf1, textRect1)
        screen.blit(textSurf2, textRect2)
        screen.blit(textSurf3, textRect3)
        screen.blit(textSurf4, textRect4)
        screen.blit(textSurf5, textRect5)
        
        pygame.display.update()
        clock.tick(60)
            
menu()

