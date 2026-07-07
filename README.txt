USER CONTROL FUNCTIONS

---MAP---


---MINES---
GET -> User may provide a serial number, otherwise requests ALL mines
CREATE -> User provides coordinates and serial number as {X, Y, ABC}
UPDATE -> User provides coordinates and serial number as {X, Y, ABC}
DELETE -> User provides serial number as {ABC}

---ROVER---
GET -> User may provide a serial number, otherwise requests ALL rovers
CREATE -> User may provide instructions as {ABC}, otherwise rover is created without instructions
DELETE -> User provides ID as {X}
SEND -> User provides ID and instructions as {X, ABC}
DISPATCH -> User provides ID as {X}