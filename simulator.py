#start


#imports
import math
import pygame
import sys


#body definition
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
         

#constants     
G = 1.0
soft = 5.0


#gravity force calculation
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
 

#acceleration calculation
def acceleration(bodies):
    for body in bodies:
        body.ax = 0.0
        body.ay = 0.0
        
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]

            fx,fy = gforce(b1,b2)
            
            #update accelerations based on force
            b1.ax = b1.ax + fx / b1.mass
            b1.ay = b1.ay + fy / b1.mass
            b2.ax = b2.ax - fx / b2.mass
            b2.ay = b2.ay - fy / b2.mass
            

#update positions and velocities      
def update(bodies, dt):
    for body in bodies:
        #update positions
        body.x = body.x + body.vx * dt + 0.5 * body.ax * dt * dt
        body.y = body.y + body.vy * dt + 0.5 * body.ay * dt * dt
    
    #store old accelerations
    oldax = [body.ax for body in bodies]
    olday = [body.ay for body in bodies]
    
    acceleration(bodies)
    
    #update velocities
    for i in range(len(bodies)):
        bodies[i].vx = bodies[i].vx + 0.5 * (oldax[i] + bodies[i].ax) * dt
        bodies[i].vy = bodies[i].vy + 0.5 * (olday[i] + bodies[i].ay) * dt


#collision detection and merging
def collision(bodies):
    #list to hold merged bodies
    merged = []
    #set to hold indices of bodies to skip
    skip = set()
    
    for i in range(len(bodies)):
        #skip bodies that have already been merged
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
            
            #check for collision
            if dist < (r1 + r2):
                totalmass = b1.mass + b2.mass
                
                newx = (b1.x * b1.mass + b2.x * b2.mass) / totalmass
                newy = (b1.y * b1.mass + b2.y * b2.mass) / totalmass
                
                newvx = (b1.vx * b1.mass + b2.vx * b2.mass) / totalmass
                newvy = (b1.vy * b1.mass + b2.vy * b2.mass) / totalmass
                
                #create merged body
                mergedbody = Body(x=newx, y=newy, vx=newvx, vy=newvy, mass=totalmass)
                
                #add to merged list and mark indices to skip
                merged.append(mergedbody)
                skip.add(i)
                skip.add(j)
                break
    
    #create new list of bodies excluding merged ones
    newbodies = []
    for i in range(len(bodies)):
        if i not in skip:
            newbodies.append(bodies[i])
            
    newbodies.extend(merged)
    return newbodies
    

#energy calculation
def energy(bodies):
    kinetic = 0.0
    potential = 0.0
    
    #kinetic energy
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
            
            #potential energy
            if dist != 0:
                potential = potential - G * b1.mass * b2.mass / dist
                
    return kinetic, potential, kinetic + potential
   

#create a body in circular orbit
def circularorbit(x, y, mass, central):
    dx = x - central.x
    dy = y - central.y
    r = math.sqrt(dx * dx + dy * dy)
    
    if r == 0:
        return None
    
    v = math.sqrt(G * central.mass / r)
    
    #velocity components perpendicular to radius vector
    vx = -v * dy / r
    vy = v * dx / r
    
    return Body(x=x, y=y, vx=vx, vy=vy, mass=mass)
       

#pygame setup
pygame.init()

width,height = 800,800
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Gravity Simulator")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 14)

xcenter = width // 2
ycenter = height // 2
scale = 2

zoom = 1.0
panx = 0.0
pany = 0.0
drag = False
lastmousepos = None


#coordinate conversion functions
def screentoworld(mx, my):
    x = (mx - xcenter) / (scale * zoom) + panx
    y = (ycenter - my) / (scale * zoom) + pany
    return x,y


#speed to colour mapping
def speedtocolour(speed, maxspeed = 5):
    s = min(speed / maxspeed, 1.0)
    
    r = int(255 * s)
    g = int(255 * (1 - abs((2 * s) - 1)))
    b = int(255 * (1 - s))
    
    return (r,g,b)


#draw a body
def drawbody(body):
    x = int(xcenter + ((body.x - panx) * scale * zoom))
    y = int(ycenter - ((body.y - pany) * scale * zoom))
    
    radius = max(2, int(math.sqrt(body.mass) * scale * zoom))
    pygame.draw.circle(screen, (255,255,255), (x,y), radius)
    
    
#draw trail of a body
def drawtrail(body):
    if len(body.trail) < 2:
        return
    
    for i in range(len(body.trail) - 1):
        x1,y1,vx1,vy1 = body.trail[i]
        x2,y2,vx2,vy2 = body.trail[i+1]
        
        sx1 = int(xcenter + (x1 - panx) * scale * zoom)
        sy1 = int(ycenter - (y1 - pany) * scale * zoom)
        sx2 = int(xcenter + (x2 - panx) * scale * zoom)
        sy2 = int(ycenter - (y2 - pany) * scale * zoom)
        
        speed = math.sqrt(vx1 ** 2 + vy1 ** 2)
        colour = speedtocolour(speed)
        
        pygame.draw.line(screen, colour, (sx1,sy1), (sx2,sy2), 2)


#draw simulation statistics
def drawstats(bodies):
    ke,pe,total = energy(bodies)
    lines = [
        f"Body Count       : {len(bodies)}",
        f"Kinetic Energy   : {ke:.2f}",
        f"Potential Energy : {pe:.2f}",
        f"Total Energy     : {total:.2f}"   
    ]
    
    y = 10
    for line in lines:
        text = font.render(line, True, (200,200,200))
        screen.blit(text, (10,y))
        y = y + 20
        

#initial bodies setup
'''
body1 = Body(x=-100, y=0, vx=0, vy=0.5, mass=50) 
body2 = Body(x=100, y=0, vx=0, vy=-0.5, mass=50) 
body3 = Body(x=0, y=0, vx=0, vy=-0.5, mass=500)
bodies = [body1, body2, body3]
'''
star = Body(0,0,0,0,1000)
planet1 = circularorbit(75,0,10,star)
planet2 = circularorbit(-125,0,50,star)
bodies = [star, planet1, planet2]

acceleration(bodies)
   
#simulation parameters   
selectedmass = 20     
dt = 0.2

#pause button setup
paused = False
pausebutton = pygame.Rect(width - 140,10,120,30)

#main simulation loop
running = True
while running:
    #limit to 60 FPS
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pausebutton.collidepoint(event.pos):
                paused = not paused
       
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drag = True
                lastmousepos = event.pos
                
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drag = False
                lastmousepos = None
                
        if event.type == pygame.MOUSEMOTION and drag:
            mx,my = event.pos
            lx,ly = lastmousepos
            
            dxpix = mx - lx
            dypix = my - ly
            
            panx = panx - dxpix / (scale * zoom)
            pany = pany + dypix / (scale * zoom)
            
            lastmousepos = (mx,my)
                
        if event.type == pygame.MOUSEWHEEL:
            mx,my = pygame.mouse.get_pos()
            
            wxbef = (mx - xcenter) / (scale * zoom) + panx
            wybef = (ycenter - my) / (scale * zoom) + pany
            
            if event.y > 0:
                zoom = zoom * 1.1
            elif event.y < 0:
                zoom = zoom / 1.1
                
            zoom = max(0.1, min(zoom,10))
            
            wxaft = (mx - xcenter) / (scale * zoom) + panx
            wyaft = (ycenter - my) / (scale * zoom) + pany
            
            panx = panx + wxbef - wxaft
            pany = pany + wybef - wyaft
            
    if not paused:        
        update(bodies, dt)
        bodies = collision(bodies)
        acceleration(bodies)
    
    if not paused:
        #update trails
        for body in bodies:
            body.trail.append((body.x, body.y, body.vx, body.vy))
            if len(body.trail) > 300:
                body.trail.pop(0)
    
    screen.fill((0,0,0))
    
    #draw trails and bodies
    for body in bodies:
        drawtrail(body)
    for body in bodies:
        drawbody(body)
    
    #draw statistics
    drawstats(bodies)    
    
    #draw pause button
    pygame.draw.rect(screen, (80,80,80), pausebutton)
    label = "Resume" if paused else "Pause"
    text = font.render(label, True, (255,255,255))
    textrect = text.get_rect(center = pausebutton.center)
    screen.blit(text, textrect)
    
    #update display
    pygame.display.flip()


#quit Pygame
pygame.quit()
sys.exit()


#end
