from .base import InterruptHandler

class MouseEventHandler(InterruptHandler):

    pass

class AssetHandler(InterruptHandler):

    def __init__(self, rate=100):
        super(AssetHandler, self).__init__(rate)

    def save_assets(self):

        pass

    def add_asset(self):

        pass


    def create_asset(self):

        pass

    def click_to_pos(self):

        pass
    
    def parameter_tuning(self):
        
        pass
