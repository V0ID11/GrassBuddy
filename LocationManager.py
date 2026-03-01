import requests
import json
from random import randint
from Location import Location


class LocationManager:
    __API_KEY: str = "AIzaSyB081Lo5w2AP6Hngs5OJ6j5_2Pk3c7ohuA"
    user_location: Location = Location()
    nearest_grass: Location = Location()

    def __init__(self):
        self.set_user_location()
        self.set_grass_location()

    def get_user_location(self) -> Location: return self.user_location

    def get_grass_location(self) -> Location: return self.nearest_grass
    
    # Finds the nearest park to the user
    def set_grass_location(self) -> tuple[float, float]:
        # Prequisites
        if not self.user_location.is_initialised():
            self.set_user_location()

        # Setup POST request
        url = "https://places.googleapis.com/v1/places:searchText"
        u_lat, u_lng = self.user_location.get_coords()
        search_text = "Parks"
        included_type = "park"
        page_size = 10
        radius = 500

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.__API_KEY,
            'X-Goog-FieldMask': 'places.displayName.text,places.location'
        }

        data = {
            "textQuery": search_text,
            "includedType": included_type,
            "pageSize": page_size,
            "rankPreference": "DISTANCE",
            "locationBias": {
                "circle": {
                    "center": {"latitude": u_lat, "longitude": u_lng},
                    "radius": radius
                }
            }
        }

        # Get the data
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status() # Catch HTTP errors
            data = response.json()
            # print(json.dumps(data, indent=2))
            
            data = data['places']
            
            random = True
            if random:
                data = data[randint(0, page_size-1)]
            else:
                data = data[0]

            # Extract name, lat and long
            if 'location' in data:
                lat = data['location']['latitude']
                lng = data['location']['longitude']
            else:
                print("Location data not found in response.")
                pass

            if 'displayName' in data:
                name = data['displayName']['text']
            else:
                print("Name data not found in response.")
                pass
            
            self.nearest_grass.set_location(lat, lng)
            self.nearest_grass.set_name(name)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            # Print the specific error message from Google if available
            if 'response' in locals() and response.text:
                print(f"API Details: {response.text}")
            return None

    # Finds user location (~1km accuracy)
    def set_user_location(self) -> tuple[float, float]:
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.__API_KEY}"
        payload = {} 

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Catch HTTP errors
            
            data = response.json()
            # print(json.dumps(data, indent=2))
            
            if 'location' in data:
                lat = data['location']['lat']
                lng = data['location']['lng']
                accuracy = data['accuracy']
            else:
                print("Location data not found in response.")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            # Print the specific error message from Google if available
            if 'response' in locals() and response.text:
                print(f"API Details: {response.text}")
            return None

        # self.user_location.set_location(lat, lng)
        # self.user_location.set_location(50.9377215432145, -1.3980270473247782)
        self.user_location.set_location(lat,lng)
        return self.user_location.get_coords()
    
    # Gets an image of the route to the nearest grass
    def route_to_grass(self) -> bool:
        # Setup
        filename = "route_map.png"
        u_lat, u_lng = self.get_user_location().get_coords()
        g_lat, g_lng = self.get_grass_location().get_coords()
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        scale = 2

        #Directions
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        directions_params = {
            "origin": f"{u_lat},{u_lng}",
            "destination": f"{g_lat},{g_lng}",
            "mode": "walking", # Options: driving, walking, bicycling, transit
            "key": self.__API_KEY
        }

        try:
            dir_response = requests.get(directions_url, params=directions_params)
            dir_response.raise_for_status()
            route_data = dir_response.json()
            
            if route_data['status'] == 'OK':
                # This is the "magic" string that follows the roads
                polyline = route_data['routes'][0]['overview_polyline']['points']
                path = f"color:0xff0000ff|weight:3|enc:{polyline}"
            else:
                print(f"Directions failed: {route_data['status']}. Falling back to straight line.")
                path = f"color:0xff0000ff|weight:3|{u_lat},{u_lng}|{g_lat},{g_lng}"
                
        except Exception as e:
            print(f"Error fetching directions: {e}. Falling back to straight line.")
            path = f"color:0xff0000ff|weight:3|{u_lat},{u_lng}|{g_lat},{g_lng}"




        # Get pins
        user = f"{u_lat},{u_lng}"
        grass = f"{g_lat},{g_lng}"
        marker_u = f"color:red|label:User|{user}"
        marker_g = f"color:green|label:Grass|{grass}"

        # Get path
        # path = f"color:0xff0000ff|weight:3|{user}|{grass}"

        # Set parameters
        params = {
            "size": "640x480",       # Image dimensions
            "maptype": "satellite",  # Satellite view
            "markers": [marker_u, marker_g],
            "path": path,
            "key": self.__API_KEY,
            "scale": scale           # High resolution for better detail
        }

        # Make request
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Successfully saved image to {filename}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False


if __name__ == "__main__":
    l = LocationManager()
    print(l.get_grass_location().get_name())
    print(l.get_grass_location().get_coords())
    l.route_to_grass()
    