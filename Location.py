class Location:
    initialised: bool = False
    name: str = ""

    lat: float = 0
    lng: float = 0

    def __init__(self):
        pass
    
    def set_location(self, lat: float, lng: float) -> bool:
        self.initialised = True

        self.lat = lat
        self.lng = lng

    def get_coords(self) -> tuple[float, float]:
        return (self.lat,self.lng)

    def reset_location(self) -> None:
        self.initialised = False
        self.lat = 0
        self.lng = 0
    
    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name
    
    def is_initialised(self) -> bool:
        return self.initialised
    
    def has_name(self) -> bool:
        return not (self.name == "")