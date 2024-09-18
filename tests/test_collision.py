import os
import sys

sys.path.insert(0, os.path.abspath("..\\"))

from eudplib import *


class Vector2D(EUDStruct):
    _fields_ = ["x", "y"]

    def constructor(self, x=None, y=None):
        self.x = x
        if y is not None:
            self.y = y

    def lengthsq(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return f_sqrt(self.lengthsq())

    def dot(self, rhs):
        return self.x * rhs.x + self.y * rhs.y

    # Operator support

    def add(self, rhs):
        t = self.copy()
        t += rhs
        return t

    def sub(self, rhs):
        t = self.copy()
        t -= rhs
        return t

    def mul(self, rhs):
        t = self.copy()
        t *= rhs
        return t

    def div(self, rhs):
        t = self.copy()
        t //= rhs
        return t

    def __iadd__(self, rhs):
        self.x += rhs.x
        self.y += rhs.y
        return self

    def __isub__(self, rhs):
        self.x -= rhs.x
        self.y -= rhs.y
        return self

    def __imul__(self, rhs):
        self.x *= rhs
        self.y *= rhs
        return self

    def __ifloordiv__(self, rhs):
        if EUDIf()(self.x >= 0x80000000):
            self.x = -(-self.x // rhs)
        if EUDElse()():
            self.x //= rhs
        EUDEndIf()

        if EUDIf()(self.y >= 0x80000000):
            self.y = -(-self.y // rhs)
        if EUDElse()():
            self.y //= rhs
        EUDEndIf()

        return self


radius = 100


class CircleObj(EUDStruct):
    _fields_ = [("pos", Vector2D), ("velocity", Vector2D)]

    def constructor(self, pos, velocity):
        self.pos = pos
        self.velocity = velocity

    def __init__(self, copyobj=None, *, pos=None, velocity=None):
        if copyobj is not None:
            super().__init__(_from=copyobj)

        else:
            if pos is None:
                pos = Vector2D()
            if velocity is None:
                velocity = Vector2D()
            super().__init__(pos, velocity)

    @EUDMethod
    def collides(self, rhs):
        self = CircleObj(self)
        rhs = CircleObj(rhs)

        distsq = rhs.pos.sub(self.pos).lengthsq()
        rsum = radius + radius
        rsumsq = rsum * rsum
        if EUDIf()(distsq <= rsumsq):
            EUDReturn(1)
        if EUDElse()():
            EUDReturn(0)
        EUDEndIf()

    def step(self):
        self.pos += self.velocity

    @EUDMethod
    def applyCollision(self, rhs):
        self = CircleObj(self)
        rhs = CircleObj(rhs)
        if EUDIf()(self.collides(rhs)):
            posdiff = rhs.pos.sub(self.pos)
            velavg = rhs.velocity.add(self.velocity).div(2)
            veldiff = rhs.velocity.sub(self.velocity)

            # Check if posdiff is in align with veldiff with dot
            aligning = posdiff.dot(veldiff)
            if EUDIf()(aligning >= 0x80000000):
                # Veldiff and posdiff are in opposite direction.
                # Meaning that they are doing collision

                # We create normal vector perpendicular with posdiff.
                posdiff_perpend = Vector2D()
                posdiff_perpend.setall([-posdiff.y, posdiff.x])
                posdiff_length = posdiff.length()

                # Divide velavg to perpendicular segment and parallel segment
                para_length = aligning
                perp_length = posdiff_perpend.dot(veldiff)

                # Invert para_length : collision
                para_length = -para_length

                # calculate veldiff back
                new_veldiff = (
                    posdiff.mul(para_length).add(posdiff_perpend.mul(perp_length))
                ).div(posdiff_length * posdiff_length)
                new_veldiff.copyto(veldiff)

                veldiff_d2 = veldiff.div(2)

                # Calculate self & rhs's velocity
                velavg.sub(veldiff_d2).copyto(self.velocity)
                velavg.add(veldiff_d2).copyto(rhs.velocity)
            EUDEndIf()
        EUDEndIf()


@EUDFunc
def main():
    a = CircleObj(pos=Vector2D(0, 0), velocity=Vector2D(10, 0))
    b = CircleObj(pos=Vector2D(1000, 0), velocity=Vector2D(-10, 0))

    if EUDInfLoop()():
        a.applyCollision(b)
        a.step()
        b.step()
        f_simpleprint(a.pos.x, a.pos.y, b.pos.x, b.pos.y)
        DoActions(SetMemory(0x6509A0, SetTo, 0))
        EUDDoEvents()
    EUDEndInfLoop()


LoadMap("outputmap/basemap/basemap.scx")
SaveMap("outputmap/collision.scx", main)
