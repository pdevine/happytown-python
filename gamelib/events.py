
__listeners = {}
__validEvents = []
__eventQueue = []

def addListener(listener):
    __listeners[listener] = True

def removeListener(listener):
    global __listeners

    try:
        del __listeners[listener]
    except KeyError:
        print "Tried to remove non-existent listener %s" % str(listener)
        pass

def reset():
    global __listeners
    __listeners = {}

def addEvent(event):
    __validEvents.append(event)

def fireEvent(eventName, *args, **kwargs):
    global __eventQueue
    #if eventName not in __validEvents:
    #    raise Exception("Could not fire non-existent event %s" % eventName)

    event = (eventName, args, kwargs)

    __eventQueue.append(event)

def consumeEvents(*args):
    global __eventQueue

    for count in range(len(__eventQueue)):
        print '<<' + str(__eventQueue[count]) + '>>'
        eventName, args, kwargs = __eventQueue[count]
        eventKeys = __listeners.keys()

        print eventKeys

        for listener in eventKeys:
            try:
                eventMethod = getattr(listener, eventName)
            except AttributeError, ex:
                #print "Listener had no event %s" % eventName
                pass
            else:
                eventMethod(*args, **kwargs)
        
    __eventQueue = []

