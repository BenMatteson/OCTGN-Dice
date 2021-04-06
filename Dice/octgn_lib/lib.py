# Version 0.0.3
import sys
if False:
    from octgn import mute, table, notify, players, me, setGlobalVariable, getGlobalVariable, whisper, rnd, rndArray, remoteCall # pylint: disable=import-error

RANDOM_NAME_SIZE = 20  # size of random unique names


def giveControlTo(player, cards):
    # region docstring
    """
    give control of cards to player

    Parameters
    ----------
    player : player
        The player who should be given the cards.
    cards : list
        A list of cards, not all cards need to be controlled
    """
    # endregion
    mute()
    for card in cards:
        if card.controller == me:
            card.controller = player

# region remoteCall extensions
# region chained calls


def buildCallChain(callList):
    # region docstring
    """
    Takes a list of calls and builds a list for use with chainedCall that executes them 
    in order.

    Parameters
    ----------
    callList : list
        A list of "calls" to be performed in sequence.
        each "call" is a list of player, function name as a string and
        a list of arguments. Essentially the arguments of a remoteCall, as a list
        Example:
        [ 
            [player, 'function', [arg1, arg2, etc.] ],
            [player2, 'otherFunction', [] ]
        ]
    """
    # endregion
    mute()
    return _internalBuildCallChain(callList, me)


def _internalBuildCallChain(callList, prev):
    mute()
    if len(callList) == 0 or len(callList[0]) < 3:
        return []
    current = callList[0]
    if current[0] == prev:  # not a remote call
        return [current[1:]] + _internalBuildCallChain(callList[1:], prev)
    else:  # setup remote call to chain
        prev = current[0]
        return [
            ['remoteCall',
                [current[0], 'chainedCall', [
                        [[current[1], current[2]]] +
                    _internalBuildCallChain(callList[1:], prev)
                ]
                ]
             ]
        ]


def chainedCall(callChain):
    # region docstring
    """
    Executes a callChain constructed by BuildCallChain
    Parameters
    ----------
    callChain : list
        A call chain; must be constructed by BuildCallChain
    """
    # endregion
    mute()
    for func, args in callChain:
        if func == 'remoteCall':
            remoteCall(*args)
            break
        else:
            globals()[func](*args)
# endregion


# region multiple callback
callBacks = {}


def callBackOnComplete(players, callList, callBack):
    # region docstring
    """
    remoteCalls to all players in players list to execute all calls in call List.
    When all players have completed all calls, executes callBack for local player.

    Parameters
    ----------
    players : list
        A list of players who will execute the callls in callList
    callList : list
        A list of "calls" to be performed before the callback.
        each "call" is a list of a function name as a string and
        a list of arguments. Essentially the arguments of a 
        remoteCall minus the player, as a list
        Example:
        [ 
            ['function', [arg1, arg2, etc.] ],
            ['otherFunction', [] ]
        ]
    callBack : list
        A list consisting of a function name as a string and arguments as a list,
        to be called after all players complete callList.
        formatting is identical to a single "call" from the callList
    """
    # endregion
    mute()
    if len(players) <= 0:
        return
    # define random name for function
    name = randomName()
    setGlobalVariable(name, len(players))

    callBacks[name] = callBack

    for player in players:
        chain = buildCallChain(
            [[player] + call for call in callList] +
            [[me, '_finishedCall', [name]]]
        )
        chainedCall(chain)


def _finishedCall(name):
    mute()
    remaining = int(getGlobalVariable(name)) - 1
    if remaining > 0:
        setGlobalVariable(name, remaining)
    else:
        func, args = callBacks.pop(name)
        globals()[func](*args)
# endregion

# endregion


def rand(val1=sys.maxsize, val2=None, count=0):
    # note: sys.maxsize breaks rnd, but we exclude the max value later
    mute()
    if val2 is None:
        min = 0
        max = val1 - 1  # exclude max value like usual
    else:
        min = val1
        max = val2 - 1  # exclude max value like usual
    if count <= 0:
        return rnd(min, max)
    else:
        return rndArray(min, max, count)


def randomName():
    # region docstring
    """
    Generates a random string made of characters which are valid for global variable names
    """
    # endregion
    genName = rndArray(35, 90, RANDOM_NAME_SIZE)
    return ''.join(map(chr, genName))
