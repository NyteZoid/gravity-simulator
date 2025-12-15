#start


import math


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
        
body1 = Body(x=-50, y=0, vx=0, vy=0.5, mass=10) 
body2 = Body(x=50, y=0, vx=0, vy=-0.5, mass=10) 
body3 = Body(x=0, y=100, vx=0, vy=-0.5, mass=1000) 
bodies = [body1, body2, body3]
        
dt = 0.1
steps = 200

for step in range(steps):
    update(bodies, dt)
    
    print(f"Step {step+1}")
    for i in range(len(bodies)):
        print(f"Body {i+1}: x={bodies[i].x:.2f}, y={bodies[i].y:.2f}, vx={bodies[i].vx:.2f}, vy={bodies[i].vy:.2f}")
    print()
    
    
#end
