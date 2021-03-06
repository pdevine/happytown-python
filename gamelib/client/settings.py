
class GameSettings:
    """Singleton object for game settings
    """

    class __impl:
        client = None
        board = None
        joinFirstGame = False
        fallingTiles = False

    __instance = None

    def __init__(self):
        if GameSettings.__instance is None:
            GameSettings.__instance = GameSettings.__impl()

            self.__dict__['_GameSettings__instance'] = GameSettings.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


