import pygame
import math
import time
import random
from pygame.math import Vector2 as vec
from PIL import Image
import os
import GIFImage as gif
runningDirectory = os.path.dirname(__file__)

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([1500, 1000])
w, h = screen.get_size()
friction = 0.99
turningRate = 5
accRate = 0.07
maxSpeed = 4
backRate = 0.1
minAsteroidSize = 30


class Player:
    def __init__(self):
        self.pos = vec(w/2, h/2)
        self.vel = 0
        self.dir = vec(0, -1)
        self.acc = 0

        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def update(self):
        multiplier = 1
        if abs(self.vel) < 5:
            multiplier = abs(self.vel) / 5
        if self.vel < 0:
            multiplier *= -1

        if self.left:
            self.dir = self.dir.rotate(turningRate * multiplier)

        elif self.right:
            self.dir = self.dir.rotate(-turningRate * multiplier)

        self.acc = 0
        if self.up:
            if self.vel < 0:
                self.acc = 3 * accRate
            else:
                self.acc = accRate
        """elif self.down:
            if self.vel > 0:
                self.acc = -3 * backRate
            else:
                self.acc = -1 * backRate"""

        self.vel += self.acc
        self.vel *= friction
        if self.vel < 0:
            if self.vel < -3:
                self.vel = -3
        else:
            if self.vel > maxSpeed:
                self.vel = maxSpeed

        addVector = vec(0, 0)
        addVector += self.vel * self.dir

        addVector *= abs(self.vel)

        self.pos += addVector

        if self.pos.x > w:
            self.pos.x = w
        elif self.pos.x < 0:
            self.pos.x = 0

        if self.pos.y > h:
            self.pos.y = h
        elif self.pos.y < 0:
            self.pos.y = 0


class Strela:
    def __init__(self, pos, dir):
        self.dir = vec(dir) * 20
        self.pos = vec(pos)
        self.dead = False

    def update(self):
        self.pos += self.dir
        self.dead = self.pos.x < 0 or self.pos.y < 0 or self.pos.x > w or self.pos.y > h
        return self.dead


class Asteroid:
    def __init__(self, pos, dir, spped, size, texture):
        self.dir = vec(dir) * spped
        self.pos = vec(pos)
        self.size = size
        self.dead = False
        self.rotation = 0
        self.texture = gif.pilImageToSurface(texture.resize((size*2, size*2)))
        self.rotationSpeed = random.randint(-20, 20)/10
        self.removed = False
        self.hit = vec(0, 0)

    def update(self, strely):
        self.pos += self.dir
        self.dead = self.pos.x < -self.size or self.pos.y < -self.size or self.pos.x > w + self.size or self.pos.y > h + self.size
        self.rotation += self.rotationSpeed
        if not self.dead:
            for strela in strely:
                if (strela.pos - self.pos).magnitude_squared() < self.size ** 2:
                    self.size -= 5
                    self.texture = pygame.transform.scale(self.texture, (self.size*2, self.size*2))
                    strela.dead = True
                    self.hit = strela.pos
                    if self.size < minAsteroidSize:
                        self.dead = True
                        break
        else:
            self.removed = True
        return self.dead



def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


def isPointInTriangle(point, trianglePoint1, trianglePoint2, trianglePoint3):
    d1 = sign(point, trianglePoint1, trianglePoint2)
    d2 = sign(point, trianglePoint2, trianglePoint3)
    d3 = sign(point, trianglePoint3, trianglePoint1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def createAsteroidPos(size):
    heightMulti = random.randint(0, 1)
    widthMulti = 1 - heightMulti
    side = random.randint(0, 1)

    x = random.randint(0, w) * widthMulti + side * heightMulti * w
    y = random.randint(0, h) * heightMulti + side * widthMulti * h

    x -= (-1 if side == 0 else side) * -1 * size * heightMulti
    y -= (-1 if side == 0 else side) * -1 * size * widthMulti

    return pygame.math.Vector2(x, y)

def main():
    explosionGif = gif.GIFImage(os.path.join(runningDirectory, "assets\\animations\\explosionSpedUp.gif"))
    asteroidExplosionGif = gif.GIFImage(os.path.join(runningDirectory, "assets\\animations\\asteroid_explode_best.gif"))
    asteroidHitGif = gif.GIFImage(os.path.join(runningDirectory, "assets\\animations\\asteroid_hit.gif"))
    shipSurface = pygame.Surface((37, 49), pygame.SRCALPHA)
    pointTop = (18, 0)
    pointLeft = (0, 48)
    pointRight = (36, 48)
    pointMiddle = (18, 40)
    pygame.draw.polygon(shipSurface, (194, 235, 252), (pointTop, pointLeft, pointMiddle, pointRight))
    pygame.draw.polygon(shipSurface, (0, 0, 0), (pointTop, pointLeft, pointMiddle, pointRight), 3)
    asteroidTextures = []
    texturesPath = os.path.join(runningDirectory, "assets\\asteroids")
    for file in os.listdir(texturesPath):
        asteroidTextures.append(Image.open(os.path.join(texturesPath, file)))
    while True:
        player = Player()
        clock = pygame.time.Clock()
        alive = True
        strely = []
        asteroidy = []
        explosions = []
        counter = 0
        explosionGif.reset()

        while True:
            clock.tick(60)
            counter += 1
            if counter % 6 == 0 and alive:
                strely.append(Strela(player.pos, player.dir))
            if counter % 40 == 0:
                size = random.randint(minAsteroidSize, 75)
                pos = createAsteroidPos(size)
                dir = vec(w / 2 - pos.x, h / 2 - pos.y)
                asteroidy.append(Asteroid(pos, dir.normalize().rotate(random.randint(-20, 20)), 200 / size, size, random.choice(asteroidTextures)))
            start = time.time()
            # Fill the background with white
            screen.fill((255, 255, 255))

            # Did the user click the window close button?
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP) and alive:
                    if event.key == pygame.K_w:
                        player.up = event.type == pygame.KEYDOWN
                    elif event.key == pygame.K_s:
                        player.down = event.type == pygame.KEYDOWN
                    elif event.key == pygame.K_d:
                        player.left = event.type == pygame.KEYDOWN
                    elif event.key == pygame.K_a:
                        player.right = event.type == pygame.KEYDOWN

                if event.type == pygame.QUIT:
                    return

            def updateAsteriod(asteroid: Asteroid, strely):
                if asteroid.dead:
                    return False
                s = asteroid.size
                if not asteroid.update(strely):
                    t = pygame.transform.rotate(asteroid.texture, asteroid.rotation)
                    screen.blit(t, asteroid.pos - vec(t.get_size()) / 2)
                    if asteroid.size != s:
                        a = asteroidHitGif.copy()
                        a.rotation = random.randint(-180, 180)
                        explosions.append((a, asteroid.hit))
                    return True
                else:
                    if not asteroid.removed:
                        a = asteroidExplosionGif.copy()
                        a.rotation = random.randint(-180, 180)
                        explosions.append((a, asteroid.pos))
                    return False

            def updateExplosion(explosion: gif.GIFImage, pos):
                explosion.render(screen, pos - vec(explosion.get_size()) / 2)
                return explosion.cur != explosion.breakpoint

            strely = [strela for strela in strely if not (strela.dead or strela.update())]
            asteroidy = [asteroid for asteroid in asteroidy if updateAsteriod(asteroid, strely)]

            for strela in strely:
                pygame.draw.circle(screen, (0, 0, 0), strela.pos, 5)

            explosions = [(explosion, pos) for explosion, pos in explosions if updateExplosion(explosion, pos)]

            player.update()
            direction = -(math.degrees(math.atan2(player.dir.y, player.dir.x))) - 90
            rotatedShip = pygame.transform.rotate(shipSurface, direction)
            blitCoords = (player.pos - pygame.math.Vector2(rotatedShip.get_size()) / 2) - player.dir * 25
            point1 = player.pos
            point2 = vec(-18, 48).rotate(-direction) + player.pos
            point3 = vec(18, 48).rotate(-direction) + player.pos
            stred = player.pos - player.dir * 25
            if alive:
                for asteroid in asteroidy:
                    closestPoint = ((stred - asteroid.pos).normalize() * asteroid.size) + asteroid.pos
                    if isPointInTriangle(closestPoint, point1, point2, point3):
                        alive = False
                        player.vel /= 2
                        player.left = False
                        player.right = False
                        player.up = False
                        player.down = False
            if explosionGif.cur < 7:
                screen.blit(rotatedShip, blitCoords)
            if not alive:
                explosionGif.render(screen, stred - vec(explosionGif.get_size())/2)
                if explosionGif.cur == explosionGif.breakpoint:
                    break
            pygame.display.flip()
            #print((time.time()-start)*1000)


main()
# Done! Time to quit.
pygame.quit()
