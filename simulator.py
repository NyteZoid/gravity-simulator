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
        self.ax = 0.0
        self.ay = 0.0
        self.trail = []
         
        
G = 1.0
soft = 5.0

def gforce(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist == 0:
        return 0,0
    
    force = G * b1.mass * b2.mass / ((dist * dist) + (soft * soft))
    
    fx = force * dx / dist
    fy = force * dy / dist
    
    return fx,fy       
 
 
def acceleration(bodies):
    for body in bodies:
        body.ax = 0.0
        body.ay = 0.0
        
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]

            fx,fy = gforce(b1,b2)
            
            b1.ax = b1.ax + fx / b1.mass
            b1.ay = b1.ay + fy / b1.mass
            b2.ax = b2.ax - fx / b2.mass
            b2.ay = b2.ay - fy / b2.mass
            
        
def update(bodies, dt):
    for body in bodies:
        body.x = body.x + body.vx * dt + 0.5 * body.ax * dt * dt
        body.y = body.y + body.vy * dt + 0.5 * body.ay * dt * dt
        
    oldax = [body.ax for body in bodies]
    olday = [body.ay for body in bodies]
    
    acceleration(bodies)
    
    for i in range(len(bodies)):
        bodies[i].vx = bodies[i].vx + 0.5 * (oldax[i] + bodies[i].ax) * dt
        bodies[i].vy = bodies[i].vy + 0.5 * (olday[i] + bodies[i].ay) * dt

    
def collision(bodies):
    merged = []
    skip = set()
    
    for i in range(len(bodies)):
        if i in skip:
            continue
        
        for j in range(i+1, len(bodies)):
            if j in skip:
                continue
            
            b1 = bodies[i]
            b2 = bodies[j]
            
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            r1 = 0.5 * math.sqrt(b1.mass)
            r2 = 0.5 * math.sqrt(b2.mass)
            
            if dist < (r1 + r2):
                totalmass = b1.mass + b2.mass
                
                newx = (b1.x * b1.mass + b2.x * b2.mass) / totalmass
                newy = (b1.y * b1.mass + b2.y * b2.mass) / totalmass
                
                newvx = (b1.vx * b1.mass + b2.vx * b2.mass) / totalmass
                newvy = (b1.vy * b1.mass + b2.vy * b2.mass) / totalmass
                
                mergedbody = Body(x=newx, y=newy, vx=newvx, vy=newvy, mass=totalmass)
                
                merged.append(mergedbody)
                skip.add(i)
                skip.add(j)
                break
    
    newbodies = []
    for i in range(len(bodies)):
        if i not in skip:
            newbodies.append(bodies[i])
            
    newbodies.extend(merged)
    return newbodies
    
   
def energy(bodies):
    kinetic = 0.0
    potential = 0.0
    
    for body in bodies:
        v2 = body.vx ** 2 + body.vy ** 2
        kinetic = kinetic + 0.5 * body.mass * v2
        
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]
            
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist != 0:
                potential = potential - G * b1.mass * b2.mass / dist
                
    return kinetic, potential, kinetic + potential
   
   
def centerofmass(bodies):
    totalmass = sum(b.mass for b in bodies)
    cx = sum((b.x * b.mass) for b in bodies) / totalmass
    cy = sum((b.y * b.mass) for b in bodies) / totalmass
    return cx,cy
   

def angularmomentum(bodies):
    cx,cy = centerofmass(bodies)
    L = 0.0  
    
    for b in bodies:
        rx = b.x - cx
        ry = b.y - cy
        L = L + b.mass * (rx * b.vy - ry * b.vx)
        
    return L 
   
   
def drawstats(bodies):
    ke,pe,total = energy(bodies)
    L = angularmomentum(bodies)
    lines = [
        f"Body Count       : {len(bodies)}",
        f"Kinetic Energy   : {ke:.2f}",
        f"Potential Energy : {pe:.2f}",
        f"Total Energy     : {total:.2f}",
        f"Angular Momentum : {L:.2f}"    
    ]
    
    y = 10
    for line in lines:
        text = font.render(line, True, (200,200,200))
        screen.blit(text, (10,y))
        y = y + 20
    
pygame.init()

width,height = 800,800
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Gravity Simulator")

clock = pygame.time.Clock()

xcenter = width // 2
ycenter = height // 2
scale = 2

font = pygame.font.SysFont("consolas", 14)


def speedtocolour(speed, maxspeed = 5):
    s = min(speed / maxspeed, 1.0)
    
    r = int(255 * s)
    g = int(255 * (1 - abs((2 * s) - 1)))
    b = int(255 * (1 - s))
    
    return (r,g,b)


def drawtrail(body):
    if len(body.trail) < 2:
        return
    
    for i in range(len(body.trail) - 1):
        x1,y1,vx1,vy1 = body.trail[i]
        x2,y2,vx2,vy2 = body.trail[i+1]
        
        sx1 = int(xcenter + x1 * scale)
        sy1 = int(ycenter - y1 * scale)
        sx2 = int(xcenter + x2 * scale)
        sy2 = int(ycenter - y2 * scale)
        
        speed = math.sqrt(vx1 ** 2 + vy1 ** 2)
        colour = speedtocolour(speed)
        
        pygame.draw.line(screen, colour, (sx1,sy1), (sx2,sy2), 2)


def drawbody(body):
    x = int(xcenter + (body.x * scale))
    y = int(ycenter - (body.y * scale))
    
    radius = max(2, int(math.sqrt(body.mass) * scale))
    pygame.draw.circle(screen, (255,255,255), (x,y), radius)

    
body1 = Body(x=-100, y=0, vx=0, vy=0.5, mass=50) 
body2 = Body(x=100, y=0, vx=0, vy=-0.5, mass=50) 
body3 = Body(x=0, y=0, vx=0, vy=-0.5, mass=500)
bodies = [body1, body2, body3]

acceleration(bodies)
        
dt = 0.2


running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    update(bodies, dt)
    bodies = collision(bodies)
    acceleration(bodies)
    
    for body in bodies:
        body.trail.append((body.x, body.y, body.vx, body.vy))
        if len(body.trail) > 300:
            body.trail.pop(0)
            
    screen.fill((0,0,0))
    
    for body in bodies:
        drawtrail(body)
    for body in bodies:
        drawbody(body)
        
    drawstats(bodies)    
    
    pygame.display.flip()
    

pygame.quit()
sys.exit()


#end
