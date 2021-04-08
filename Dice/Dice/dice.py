import sys
if False:
    from octgn import mute, table, notify, players, me, setGlobalVariable, getGlobalVariable, whisper, rnd # pylint: disable=import-error
    from lib import callBackOnComplete, rand, giveControlTo # pylint: disable=import-error

def rollTable(group, x=0, y=0):
    mute()
    roll([c for c in table if c.set == 'Dice'])

def roll(cards, x=0, y=0):
    mute()
    notify("{} Rolls:".format(me))
    if any(card.controller != me for card in cards): 
        callBackOnComplete(
            players,                            # for simplicity, we ask everyone
            [                                   # to give us all the cards
                ['giveControlTo', [me, cards]]
            ],
            ['_rollActual', [cards]]            # when they're all done, roll
        )
    else:
        _rollActual(cards)

def _rollActual(cards, name=None):
    mute()
    if len(cards) <= 0:
        return
    x, y, w, h = [int(val)
                  for val in getGlobalVariable('diceRegion').split(',')]
    minDist = int(getGlobalVariable('diceBuffer'))
    points = getDistributedPoints(x, y, w, h, len(cards), minDist)
    # rots = rndArray(0, 360, cards.count)
    rolls = {}
    results = rand(count=len(cards))
    for i, card in enumerate(cards):
        card.moveToTable(points[i][0], points[i][1])
        # card.orientation = rots[i]
        result = (results[i] % len(card.alternates)) + 1
        card.alternate = '' if result == 1 else str(result)

        cardName = card.alternateProperty('', 'Name') if name is None else name
        rolls[cardName] = rolls.get(cardName, []) + [str(result)]

    for n, res in rolls.items():
        notify("{}: ".format(n) + ', '.join(res))


def isDice(cards, x=0, y=0):
    return all(card.set == 'Dice' for card in cards)

# area only used for start point, should probably be small
def getDistributedPoints(x, y, width, height, count, minDist, k=30):
    mute()
    if count <= 0 or width < 0 or height < 0:
        return

    first = (rnd(x, x + width), rnd(y, y + height))
    active = [first]
    ret = {first}
    count -= 1

    # anulus pattern to find values around a point
    anulusOuter = int(1.5*minDist)
    offsetAnulus = []
    for i in range(-anulusOuter, anulusOuter+1):
        for j in range(-anulusOuter, anulusOuter+1):
            if i**2 + j**2 < anulusOuter**2 and i**2 + j**2 > minDist**2:
                offsetAnulus.append((i, j))
    # disc pattern to check for too-close points
    offsetDisc = []
    for i in range(-minDist, minDist+1):
        for j in range(-minDist, minDist+1):
            if i**2 + j**2 < minDist**2:
                offsetDisc.append((i, j))

    while count > 0 and len(active) > 0:
        current = active[rand(0, len(active))]
        randomValues = rand(0, len(offsetAnulus), k)
        for i in range(k):
            try:
                offset = offsetAnulus[randomValues[i]]
                point = (current[0] + offset[0], current[1] + offset[1])
                for off in offsetDisc:
                    if (point[0] + off[0], point[1] + off[1]) in ret:
                        raise InvalidPoint()
                active.append(point)
                ret.add(point)
                count -= 1
                # break
            except InvalidPoint:
                pass
        else:
            active.remove(current)

    ret = list(ret)
    # this should never happen, but to be safe, we make sure to pad values if needed
    while count > 0:
        whisper("dice placement error: roll values are unaffected")
        ret += [(x, y)]
        count -= 1

    return ret


class InvalidPoint(Exception):
    pass
