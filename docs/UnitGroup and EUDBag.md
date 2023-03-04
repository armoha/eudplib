We'll use Python and epScript like pseudocode to simplify the explanation and improve readability. (Avoid `self` keyword and specify class name, etc.)

# Background
StarCraft triggers are singly linked intrusive list.
* Singly linked: prev, next triggers come first on in-memory-trigger. But prev has no usage.
* intrusive list: There's no list Node. Trigger data and prev, next trigger pointers are laid together.

SetDeaths consists of (Destination, Modifier, Value).
* Destination: Combination of Player and Unit. (Ptr = 0x58A364 + 4 * Player + 48 * Unit)\
    We'll fix Unit to 0 to simplify things (Ptr = 0x58A364 + 4 * Player)
* Modifier is one of (SetTo, Add, Subtract). We'll stick to SetTo most of the time.

# UnitGroup
A contiguous array type **kept sorted**, consists of 0 condition 1 action Triggers.\
See https://gameprogrammingpatterns.com/data-locality.html#packed-data

## Kept sorted?
Active objects are adjacent to each other.\
Entry can be active object or empty.

### Plain EUDArray example
```js
const array = EUDArray(capacity);

for(var i = 0 ; i < array.length ; i++) {
    const element = array[i];
    if (element.isActive()) {
        element.doSomething();
    }
}
```
Why this is bad?
* It loops the whole array! Looping active elements only would be much better.

```js
for(var i = 0 ; i < array.numOfActive ; i++) {
    const element = array[i];
    element.doSomething();
}
```
To keep array sorted, without running sort function on every frame, our `add` and `remove` functions can be written like this:
```js
function add(entry) {
    array[array.numOfActive] = entry;
    array.numOfActive += 1;  // one more active entry
}
function remove(index) {
    array.numOfActive -= 1;  // one fewer active entry
    // Move last active element to removed index
    const lastEntry = array[array.numOfActive];
    array[index] = lastEntry;
}
```

### What UnitGroup does
To remove element during loop, we stores element from backward, while keeping loop walks from forward.\
See https://gameprogrammingpatterns.com/update-method.html#be-careful-modifying-the-object-list-while-updating
```js
for(var i = UnitGroup.capacity - UnitGroup.numOfActive ; i < UnitGroup.capacity ; i++) {
    const element = UnitGroup[i];
    element.doSomething();
}
```

`UnitGroup.remove(index)` moves **first** active element to removed index.
```js
function add(entry) {
    UnitGroup[UnitGroup.capacity - UnitGroup.numOfActive] = entry;
    UnitGroup.numOfActive += 1;  // one more active entry
}
function remove(index) {
    // Move FIRST active element to removed index
    const firstEntry = UnitGroup[UnitGroup.capacity - UnitGroup.numOfActive];
    UnitGroup[index] = firstEntry;
    UnitGroup.numOfActive -= 1;  // one fewer active entry
}
```

## In-memory Layout
Internally uses `EUDVArray(capacity)` = array of Triggers with 0 condition 1 SetDeaths action
```py
layout of UnitGroup(capacity=N)
┌───────────┬───────────┬───────────┐
│Trigger 1  │Trigger 2  │Trigger 3  │
│           │           │           │
│           │           │           │
│           │           │           │
└─────┬─────┴─────┬─────┴───────┬───┘
      │           │             │
      │           │             │
      │     ┌─────▼─────┐       │
      └────►│LoopVar    │◄──────┘
            │           │
            │           │
            │           │
            └───────────┘

Trigger1(
    nextptr=LoopVarTrigger,
    actions=loopvar.SetNumber(Value1)
)
Trigger2(
    nextptr=LoopVarTrigger,
    actions=loopvar.SetNumber(Value2)
)
Trigger3(
    nextptr=LoopVarTrigger,
    actions=loopvar.SetNumber(Value3)
)
.......
TriggerN(
    nextptr=LoopVarTrigger,
    actions=loopvar.SetNumber(ValueN)
)
```
The distance between TriggerX and TriggerX+1 are fixed to 72 bytes. (Minimal overlapping distance for 0 condition 1 action Triggers)

All triggers in `UnitGroup` *point* to loopvar (See below): their nextptrs point to Trigger of loopvar, and their SetDeaths actions substitute to value of loopvar.

## loopvar
loopvar is EUDVariable whose value are assigned by triggers of UnitGroup.
```js
LoopVarTrigger(
    nextptr=?,
    actions=SetMemory(destination?, SetTo, value?)
)
```
Its nextptr and destination should be assigned before *use*. Its value is assigned by `UnitGroup`.

Currently, `UnitGroup` only supports `.cploop` so destination of loopvar is initially set to edit `CurrentPlayer` (0x6509B0). (Its destination can be changed temporarily in `unit.epd` and `unit.remove()`)
```py
UnitGroup.loopvar = EUDVariable(EPD(0x6509B0), SetTo, 0)
UnitGroup.varray = EUDVArray(capacity)(
    dest=UnitGroup.loopvar,
    nextptr=UnitGroup.loopvar.GetVTable()
)
```

## UnitGroup.add(unitEPD)
As mentioned above, `UnitGroup` adds entry from backward.

    Empty UnitGroup                           ↓ last empty slot
    | (empty) | (empty) | (empty) | (empty) | (empty) |

    Add 1 Entry                     ↓ last empty slot
    | (empty) | (empty) | (empty) | (empty) | unitEPD |

    Add 2 Entry           ↓ last empty slot
    | (empty) | (empty) | (empty) | unitEPD | unitEPD |

    Add 3 Entry ↓ last empty slot
    | (empty) | (empty) | unitEPD | unitEPD | unitEPD |

To add entry, we need a position where next entry will be put.
```py
UnitGroup.pos = EUDVariable(EPD(UnitGroup.varray) + (348 // 4) + (72 // 4 * capacity))
```
Initially `UnitGroup.pos` points to last entry of `UnitGroup`.\
After every `UnitGroup.add(unitEPD)`, `UnitGroup.pos` decrements by 18 (= 72 // 4).
* 348 = 8 (prev and next) + 320 (20 conditions * 16 bytes sized) + 20 (Value of SetDeaths action)\
    See http://www.staredit.net/wiki/index.php/Scenario.chk#.22TRIG.22_-_Triggers for TRIG layout
* 72 = distance between TriggerX and TriggerX+1 (mininal overlapping distance of 0C 1A triggers)
* // 4 : SetDeaths uses EPD, not plain memory address.
```js
function add(unitEPD) {
    SetMemoryEPD(UnitGroup.pos, SetTo, unitEPD);
    UnitGroup.pos -= 18;
}
```

## foreach(unit: UnitGroup.cploop) { ... }
We need ptr of Trigger to execute it.\
Because nextptr of Trigger is Ptr of next executing trigger: `Trigger(nextptr=Ptr)`.

    Empty UnitGroup                                     ↓ first active entry
    | (empty) | (empty) | (empty) | (empty) | (empty) |

    Add 1 Entry                               ↓ first active entry
    | (empty) | (empty) | (empty) | (empty) | unitEPD |

    Add 2 Entry                     ↓ first active entry
    | (empty) | (empty) | (empty) | unitEPD | unitEPD |

    Add 3 Entry           ↓ first active entry
    | (empty) | (empty) | unitEPD | unitEPD | unitEPD |

Remember `EUDVArray` is array of 0C 1A triggers, and `UnitGroup` internally uses it.
```py
UnitGroup.trg = EUDVariable(UnitGroup.varray + 72 * capacity)
```

After every `UnitGroup.add(unitEPD)`, `UnitGroup.trg` decrements by 72.
```js
function add(unitEPD) {
    SetMemoryEPD(UnitGroup.pos, SetTo, unitEPD);
    UnitGroup.trg -= 72;
    UnitGroup.pos -= 18;
}
```

As mentioned above, all triggers in `UnitGroup` is *always* pointing `loopvar`: their nextptrs point to Trigger of loopvar, and their SetDeaths actions substitute to value of loopvar.

So executing trigger of UnitGroup will feed loopvar with its value, and execute loopvar trigger. Destination of loopvar is initially 0x6509B0 (CurrentPlayer) so it edits CurrentPlayer to **unitEPD**, feeded from UnitGroup trigger just now.

```js
function UnitGroup.cploop() {
    var ActiveEntryPtr = UnitGroup.trg;
    const loopbody = Forward();
    DoActions(SetNextPtr(loopvar.GetVTable(), loopbody));
    while (ActiveEntryPtr < UnitGroup.varray + 72 * capacity) {
        EUDJump(ActiveEntryPtr);
        // ActiveEntry Trigger -> loopvar trigger -> loopbody

        loopbody.__lshift__(NextTrigger());
        yield CpHelper(......);

        EUDSetContinuePoint();
        ActiveEntryPtr += 72
    }
}
```

## unit.remove()
`UnitGroup.remove(index)` moves **first** active element to removed index.\
`UnitGroup.trg` stores first active entry of `UnitGroup`.

To execute first active Trigger and feed loopvar with first unitEPD, we'll run `UnitGroup.trg` and order it to edit nextptr of `UnitGroup.trg` itself(!).
```js
function unit.remove() {
    const SetLoopVarDest = Forward();
    const remove_end = Forward();
    // after loopvar, remove_end will be executed
    DoActions(
        SetNextPtr(UnitGroup.loopvar.GetVTable(), remove_end),
        SetLoopVarDest.__lshift__(loopvar.SetDest(?)),
    );
    // remove_start Trigger -> UnitGroup.trg trigger
    // -> First active trigger in UnitGroup
    // -> loopvar trigger -> remove_end
    EUDJump(UnitGroup.trg);

    remove_end.__lshift__(NextTrigger());
    // one fewer active entry
    UnitGroup.trg += 72;
    UnitGroup.pos += 18;
    // Restore loopvar fields
    DoActions(
        UnitGroup.loopvar.SetDest(EPD(0x6509B0)),
        SetNextPtr(UnitGroup.loopvar.GetVTable(), loopbody),
    );
}
```
### Optimization
`UnitGroup.trg` stores first active entry of `UnitGroup`.

To execute first active Trigger and feed loopvar with first unitEPD, we'll run `UnitGroup.trg` and order it to edit nextptr of `UnitGroup.trg` itself(!).
```js
function unit.remove() {
    const SetLoopVarDest = Forward();
    const remove_end = Forward();
    // remove_start Trigger -> UnitGroup.trg trigger
    // -> First active trigger in UnitGroup
    // -> loopvar trigger -> remove_end
    const remove_start = RawTrigger(
        // Trigger of UnitGroup.trg will be executed next
        nextptr=UnitGroup.trg.GetVTable(),
        actions=list(
            // Set destination of UnitGroup.trg to its nextptr
            UnitGroup.trg.SetDest(EPD(UnitGroup.trg.GetVTable()) + 1),
            // after UnitGroup.trg, First active trigger in UnitGroup will be executed
            // after First active trigger, loopvar will be executed
            // after loopvar, remove_end will be executed
            SetNextPtr(UnitGroup.loopvar.GetVTable(), remove_end),
            SetLoopVarDest.__lshift__(loopvar.SetDest(?)),
        )
    );

    ......
}
```

## unit.epd

## Trigger Control flow

# EUDBag
A contiguous array type **kept sorted**, consists of 0 condition 1\~64 actions Triggers.\
Generalization of UnitGroup to array of 1\~64 action Triggers.
## In-memory Layout
```js
Trigger1(
    nextptr=LoopVarTrigger,
    actions=[
        SetMemory(loopvar.value1.getValueAddr(), SetTo, Object1.member1),
        SetMemory(loopvar.value2.getValueAddr(), SetTo, Object1.member2),
        SetMemory(loopvar.value3.getValueAddr(), SetTo, Object1.member3),
        ......
        SetMemory(loopvar.valueM.getValueAddr(), SetTo, Object1.memberM),
    ]
)
Trigger2(
    nextptr=LoopVarTrigger,
    actions=[
        SetMemory(loopvar.value1.getValueAddr(), SetTo, Object2.member1),
        SetMemory(loopvar.value2.getValueAddr(), SetTo, Object2.member2),
        SetMemory(loopvar.value3.getValueAddr(), SetTo, Object2.member3),
        ......
        SetMemory(loopvar.valueM.getValueAddr(), SetTo, Object2.memberM),
    ]
)
......
TriggerN(
    nextptr=LoopVarTrigger,
    actions=[
        SetMemory(loopvar.value1.getValueAddr(), SetTo, ObjectN.member1),
        SetMemory(loopvar.value2.getValueAddr(), SetTo, ObjectN.member2),
        SetMemory(loopvar.value3.getValueAddr(), SetTo, ObjectN.member3),
        ......
        SetMemory(loopvar.valueM.getValueAddr(), SetTo, ObjectN.memberM),
    ]
)
```
## loopvar
```js
LoopVarTrigger(
    nextptr=?,
    actions=[
        SetMemory(destination1?, SetTo, value1?),
        SetMemory(destination2?, SetTo, value2?),
        SetMemory(destination3?, SetTo, value3?),
        ......
        SetMemory(destinationM?, SetTo, valueM?),
    ]
)
```
## EUDBag.add(value1, value2, ... , valueM)
## foreach(subobject: EUDBag) { ... }
## Subobject
## entry.remove()