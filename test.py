import requests

def get_computer_location(api_key):
    # The endpoint for the Geolocation API
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
    
    # We send an empty JSON payload. 
    # The docs state: "If the request body is not included, the results are 
    # returned based on the IP address of request location."
    payload = {} 
    
    try:
        # Make the POST request
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Catch HTTP errors
        
        data = response.json()
        
        if 'location' in data:
            lat = data['location']['lat']
            lng = data['location']['lng']
            accuracy = data['accuracy']
            return lat, lng, accuracy
        else:
            print("Location data not found in response.")
            return None, None, None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        # Print the specific error message from Google if available
        if 'response' in locals() and response.text:
            print(f"API Details: {response.text}")
        return None, None, None

# --- Example Usage ---
API_KEY = "AIzaSyB081Lo5w2AP6Hngs5OJ6j5_2Pk3c7ohuA"  # Replace with your actual API key

lat, lng, accuracy = get_computer_location(API_KEY)

if lat and lng:
    print(f"{lat},{lng}")
    print(f"Latitude: {lat}")
    print(f"Longitude: {lng}")
    print(f"Accuracy: within {accuracy} meters")