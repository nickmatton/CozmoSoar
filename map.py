from tkinter import *
import time
import math

class Object():
    def __init__(self, x, y, object, objID, name):
        self.x = x
        self.y = y
        self.verts = None
        self.object = object
        self.objID = objID
        self.name = name
        self.highlight = None
        self.color = "white"

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    

class Map():
    def __init__(self):
        self.master = Tk()
        self.walls = []
        self.cubes = []
        self.waypoints = []
        self.paths = []
        self.svs_objects = []
        self.Cwidth = 1000
        self.Cheight = 750
        
        self.world = Canvas(self.master, bg="grey", width=self.Cwidth, height=self.Cheight)
        self.world.pack()
        self.cozmo = self.world.create_polygon((self.Cwidth/2)-10,self.Cheight/2-10,(self.Cwidth/2)-10,self.Cheight/2+10, (self.Cwidth/2)+20,self.Cheight/2, fill="blue",outline="black")
        self.CX = self.Cwidth/2
        self.CY = self.Cheight/2
        self.master.update()
    
    def fixCoords(self,x,y):
        return x+(self.Cwidth/2), (self.Cheight/2)-y

    def fixVertices(self, vertices):
        verts = []  # take out z coord and fix x,y
        epsilon = 15
        for vert in vertices:
            add = True
            x, y = self.fixCoords(vert[0], vert[1])
            for (a, b) in verts:
                x_error = abs(x - a)
                y_error = abs(y - b)
                if (x_error < epsilon and y_error < epsilon):
                    add = False
            if add:
                verts.append((x, y))

        return verts
        # verts = []  # take out z coord and fix x,y
    #         # for vert in vertices:
    #         #     x, y = self.fixCoords(vert[0], vert[1])
    #         #     if (x, y) not in verts:
    #         #         verts.append((x, y))
    #         #
    #         # return verts
    
    def updateCozmo(self,x,y,rotation):      #implement with polygon so we can rotate
        self.world.delete(self.cozmo)
        x,y = self.fixCoords(x,y)
        self.CX = x
        self.CY = y

        x1 = x-10
        y1 = y-10
        x2 = x-10
        y2 = y+10
        x3 = x+20
        y3 = y

        x1, y1 = rotate(x, y, x1, y1, -rotation)
        x2, y2 = rotate(x, y, x2, y2, -rotation)
        x3, y3 = rotate(x, y, x3, y3, -rotation)

        self.cozmo = self.world.create_polygon(x1, y1, x2, y2, x3, y3, fill="blue",outline="black")
        
        if(self.paths):
            for p in self.paths:
                self.updatePath(p.objID)
    
        self.master.update()

    # self.world.create_polygon(verticies,color,position)
    #use above if given verticies and postion
    #i think alex already rotated and positioned verticies, but if not will rework
    #position,rotation
    def addSvsObject(self, objID, vertices):
        # fixes coords
        verts = self.fixVertices(vertices)

        sx, sy = findCentroid(verts)


        obj = None
        for o in self.svs_objects:
            if objID == o.objID:
                obj = o

        def angleCompare(point):
            if point[0] > sx and point[1] >= sy:
                angle = math.atan((point[0]-sx)/(point[1]-sy))
            elif point[0] < sx and point[1] >= sy:
                angle = math.pi + math.atan((point[0]-sx)/(point[1]-sy))
            elif point[0] < sx and point[1] < sy:
                angle = math.pi + math.atan((point[0] - sx) / (point[1] - sy))
            elif point[0] > sx and point[1] < sy:
                angle = 2*math.pi + math.atan((point[0] - sx) / (point[1] - sy))
            elif point[0] == sx and point[1] > sy:
                angle = math.pi/2
            elif point[0] == sx and point[1] < sy:
                angle = 3*math.pi/2
            else:
                angle = 404

            return angle

        verts = sorted(verts,key=angleCompare)


        if not obj:
            object = self.world.create_polygon(verts, fill="white",outline="black")
            OBJ = Object(sx,sy,object,objID,"svs")
            OBJ.verts = verts
            self.svs_objects.append(OBJ)

        else:
            self.world.delete(obj.object)
            obj.object = self.world.create_polygon(verts, fill=obj.color,outline="black")
            obj.verts = verts
            obj.x = sx
            obj.y = sy
    
    def addCube(self,verts,objID):
        c = None
        for o in self.cubes:
            if objID == o.objID:
                c = o
        if not c:
            verts = self.fixVertices(verts)
            x, y = findCentroid(verts)
            object = self.world.create_polygon(verts,fill="white",outline="black")
            obj = Object(x,y,object,objID,"cube")
            obj.color = "white"
            obj.verts = verts
            
            self.cubes.append(obj)
            
            self.master.update()
        else:
            self.updateCube(verts,c)
    
    def updateCube(self,verts,cube):
        verts = self.fixVertices(verts)
        x,y = findCentroid(verts)

        if cube:
            self.world.delete(cube.object)
            cube.object = self.world.create_rectangle(x-7,y-7,x+7,y+7,fill=cube.color,outline="black")
            cube.x = x
            cube.y = y
            cube.verts = verts


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
        elif type == "svs":
            x = self.svs_objects
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

    def changeCubeColor(self, objID, color):
        cube = None
        for c in self.cubes:
            if c.objID == objID:
                cube = c

        for s in self.svs_objects:
            if s.objID == objID:
                cube = s

        if cube:
            self.world.delete(cube.object)
            cube.color = color
            cube.object = self.world.create_polygon(cube.verts, fill=color,outline="black")
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

def findCentroid(verts):
    sx = 0
    sy = 0
    for vert in verts:
        sx += vert[0]
        sy += vert[1]

    sx = sx / len(verts)
    sy = sy / len(verts)
    return sx, sy

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

def testSVS():
    verts = ((50,50), (100,50), (100,100), (50,100))

    map = Map()
    map.master.update()
    time.sleep(1)

    map.addSvsObject(1,verts,"blue")
    map.master.update()
    time.sleep(1)

    verts = ((-50, -50), (-100, -50), (-100, -100), (-50, -100))

    map.addSvsObject(1, verts, "blue")
    map.master.update()
    time.sleep(1)

#testSVS()
#goodTest()
