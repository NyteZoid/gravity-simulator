#start


import math
import pygame
import sys


class Body:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
         
        
G = 1.0

def gforce(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist == 0:
        return 0,0
    
    force = G * b1.mass * b2.mass / (dist * dist)
    
    fx = force * dx / dist
    fy = force * dy / dist
    
    return fx,fy       
 
        
def update(bodies, dt):
    for body in bodies:
        fxtotal = 0
        fytotal = 0
        
        for other in bodies:
            if body is other:
                continue
            
            fx,fy = gforce(body, other)
            fxtotal = fxtotal + fx
            fytotal = fytotal + fy
            
        ax = fxtotal / body.mass
        ay = fytotal / body.mass
        
        body.vx = body.vx + (ax * dt)
        body.vy = body.vy + (ay * dt)
        
        body.x = body.x + (body.vx * dt)
        body.y = body.y + (body.vy * dt)
    
    
pygame.init()

width,height = 800,800
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Gravity Simulator")

clock = pygame.time.Clock()

xcenter = width // 2
ycenter = height // 2
scale = 2

def drawbody(body):
    x = int(xcenter + (body.x * scale))
    y = int(ycenter + (body.y * scale))
    
    radius = max(2, int(math.sqrt(body.mass)))
    pygame.draw.circle(screen, (255,255,255), (x,y), radius)

    
body1 = Body(x=-100, y=0, vx=0, vy=0.5, mass=50) 
body2 = Body(x=100, y=0, vx=0, vy=-0.5, mass=50) 
body3 = Body(x=0, y=0, vx=0, vy=-0.5, mass=500)
bodies = [body1, body2, body3]
        
dt = 0.1


running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    update(bodies, dt)
    
    screen.fill((0,0,0))
    
    for body in bodies:
        drawbody(body)
        
    pygame.display.flip()
    

pygame.quit()
sys.exit()


#end
