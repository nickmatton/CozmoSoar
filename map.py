from tkinter import *
import time
import math

class Object():
    def __init__(self, x, y, object, objID, name):
        self.x = x
        self.y = y
        self.object = object
        self.objID = objID
        self.name = name
        self.highlight = None

class Map():
    def __init__(self):
        self.master = Tk()
        self.walls = []
        self.cubes = []
        self.waypoints = []
        self.paths = []
        self.Cwidth = 1000
        self.Cheight = 750
        
        self.world = Canvas(self.master, bg="grey", width=self.Cwidth, height=self.Cheight)
        self.world.pack()
        self.cozmo = self.world.create_oval((self.Cwidth/2)-10,self.Cheight/2-10,(self.Cwidth/2)+10,self.Cheight/2+10,fill="blue")
        self.CX = self.Cwidth/2
        self.CY = self.Cheight/2
        self.master.update()
    
    def fixCoords(self,x,y):
        return x+(self.Cwidth/2), y+(self.Cheight/2)
    
    def updateCozmo(self,x,y):      #implement with polygon so we can rotate
        self.world.delete(self.cozmo)
        x,y = self.fixCoords(x,y)
        self.CX = x
        self.CY = y
        self.cozmo = self.world.create_oval(x-10,y-10,x+10,y+10,fill="blue")
        
        if(self.paths):
            for p in self.paths:
                self.updatePath(p.objID)
    
        self.master.update()

    def addCube(self,x,y,objID):
        c = None
        for o in self.cubes:
            if objID == o.objID:
                c = o
        if(not c):
            x,y = self.fixCoords(x,y)
            object = self.world.create_rectangle(x-7,y-7,x+7,y+7,fill="white")
            obj = Object(x,y,object,objID,"cube")
            
            self.cubes.append(obj)
            
            self.master.update()
        else:
            self.updateCube(x,y,c)
    
    def updateCube(self,x,y,cube):
        x,y = self.fixCoords(x,y)
        if (cube):
            self.world.delete(cube.object)
        
            cube.object = self.world.create_rectangle(x-7,y-7,x+7,y+7,fill="white")
            cube.x = x
            cube.y = y

            self.master.update()
        else:
            print("no cube to update")


    def addWaypoint(self,x,y,objID):
        wp = None
        for w in self.waypoints:
            if w.objID == objID:
                wp = w
        if(not wp):
            x,y = self.fixCoords(x,y)
            object = self.world.create_oval(x-2,y-2,x+2,y+2, fill="red")
            obj = Object(x,y,object, objID, "waypoint")
            
            self.waypoints.append(obj)
            
            self.master.update()
        else:
            self.updateWaypoint(x,y,wp)

    def updateWaypoint(self,x,y,wp):
        x,y = self.fixCoords(x,y)
        if(wp):
            self.world.delete(wp.object)
            
            wp.object = self.world.create_oval(x-2,y-2,x+2,y+2, fill="red")
            wp.x = x
            wp.y = y
            
            for p in self.paths:
                if p.objID == wp.objID:
                    self.up(wp,p)
            
            self.master.update()
        else:
            print("no waypoint to update")
    
    def addPath(self, waypointID):
        wp = None
        for w in self.waypoints:
            if w.objID == waypointID:
                wp = w
    
        if(wp):
            path = None
            for p in self.paths:
                if p.objID == waypointID:
                    path = p
        
            if (not path):
                x = wp.x
                y = wp.y
            
                object = self.world.create_line(x,y,self.CX, self.CY, fill="green")
                obj = Object(x,y,object, waypointID,"path")
            
                self.paths.append(obj)
            
            else:
                self.up(wp,path)
                    
        else:
            print("no waypoint to create path to")
        self.master.update()

    
    def updatePath(self, waypointID):
        wp = None
        path = None
        for w in self.waypoints:
            if w.objID == waypointID:
                wp = w
        for p in self.paths:
            if p.objID == waypointID:
                path = p
                
        if(path and wp):
            x = path.x = wp.x
            y = path.y = wp.y

            self.world.delete(path.object)

            path.object = self.world.create_line(x,y,self.CX, self.CY,fill="green")

            self.master.update()


    def up(self,wp,path):
        x = path.x = wp.x
        y = path.y = wp.y
            
        self.world.delete(path.object)
            
        path.object = self.world.create_line(x,y,self.CX, self.CY,fill="green")
            
        self.master.update()



    def addWall(self,x,y,width,depth,angle,objID):
        wall = None
        for w in self.walls:
            if w.objID == objID:
                wall = w
    
        x,y = self.fixCoords(x,y)
        x0 = x-(width/2)
        y0 = y-(depth/2)

        x1 = x+(width/2)
        y1 = y-(depth/2)

        x2 = x+(width/2)
        y2 = y+(depth/2)

        x3 = x-(width/2)
        y3 = y+(depth/2)

        x0,y0 = rotate(x,y,x0,y0,angle)
        x1,y1 = rotate(x,y,x1,y1,angle)
        x2,y2 = rotate(x,y,x2,y2,angle)
        x3,y3 = rotate(x,y,x3,y3,angle)

        if(not wall):
            object = self.world.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,fill="black")
            obj = Object(x,y,object,objID,"wall")
            self.walls.append(obj)
        else:
            self.world.delete(wall.object)
            wall.object = self.world.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,fill="black")
            wall.x = x
            wall.y = y

        
        self.master.update()

    def deleteObject(self, objID, type):
        
        if type == "cube":
            x = self.cubes
        elif type == "wall":
            x = self.walls
        elif type == "waypoint":
            x = self.waypoints
        elif type == "path":
            x = self.paths
        else:
            print("not an object type")
            return

        i=0
        if type == "waypoint":
            for y in self.paths:
                if y.objID == objID:
                    self.world.delete(y.object)
                    self.paths.pop(i)
                else:
                    i=i+1
        i=0
        for y in x:
            if y.objID == objID:
                self.world.delete(y.object)
                x.pop(i)
            else:
                i=i+1

    def changeCubeColor(self, objID,color):
        cube = None
        for c in self.cubes:
            if c.objID == objID:
                cube = c
    
        if (cube):
            self.world.delete(cube.object)
            cube.object = self.world.create_rectangle(cube.x-7,cube.y-7,cube.x+7,cube.y+7,fill=color)
        else:
            print("no cube with objID")

        self.master.update()
        
    def highlightObject(self,objID, type):
        if type == "cube":
            x = self.cubes
        elif type == "wall":
            x = self.walls
        elif type == "waypoint":
            x = self.waypoints
        elif type == "path":
            x = self.paths
        else:
            print("not an object type")
            return

        obj = None
        
        
        for o in x:
            if o.objID == objID:
                obj = o

        if(obj):
            obj.highlight
        return

def rotate(x,y,x0,y0,angle):        #coords must be fixed before entering func
    nx= x + math.cos(angle) *(x0-x) - math.sin(angle) *(y0-y)
    ny= y + math.sin(angle) *(x0-x) + math.cos(angle) *(y0-y)
    return(nx,ny)


def createMap():
    map = Map()
    map.master.update()
    return map


def goodTest():
    map = Map()
    map.master.update()
    time.sleep(1)
    
    map.addCube(100,100,0)
    map.master.update()
    time.sleep(1)
    
    map.addCube(0,-100,1)
    map.master.update()
    time.sleep(1)
    
    map.addCube(0,-10,0)
    map.master.update()
    time.sleep(1)
    
    map.updateCozmo(-50,70)
    map.master.update()
    time.sleep(1)
    
    map.addWall(-80,100,50,5,math.pi/4,100)
    map.master.update()
    time.sleep(1)
    
    map.addWall(-90,90,50,5,math.pi/2,101)
    map.master.update()
    time.sleep(1)
    
    map.addWall(-80,50,50,5,0,100)
    map.master.update()
    time.sleep(1)

    map.addWaypoint(0,0,50)
    map.master.update()
    time.sleep(1)
    
    map.addWaypoint(-30,-30,51)
    map.master.update()
    time.sleep(1)
    
    map.addPath(50)
    map.master.update()
    time.sleep(1)
    
    map.addPath(51)
    map.master.update()
    time.sleep(1)
    
    map.addWaypoint(-100,-100,51)
    map.master.update()
    time.sleep(1)
    
    
    map.updateCozmo(0,-70)
    map.master.update()
    time.sleep(1)
    
    map.deleteObject(51,"waypoint")
    map.master.update()
    time.sleep(1)
    
    map.deleteObject(50,"path")
    map.master.update()
    time.sleep(1)

    map.deleteObject(50,"waypoint")
    map.master.update()
    time.sleep(1)
    
    
    map.deleteObject(100,"wall")
    map.master.update()
    time.sleep(1)
    
    map.deleteObject(101,"wall")
    map.master.update()
    time.sleep(1)
    
    map.deleteObject(0,"cube")
    map.master.update()
    time.sleep(1)
    
    map.deleteObject(1,"cube")
    map.master.update()
    time.sleep(1)
    
    return


goodTest()
