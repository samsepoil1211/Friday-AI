import pyttsx3
import speech_recognition as sr
import webbrowser
import json
import os
from datetime import datetime
import requests

# Paths to the files where queries are stored
QUERY_FILE = 'query_record.json'
INTERNAL_SEARCH_FILE = 'internal_search.json'

# WeatherAPI configuration
WEATHERAPI_API_KEY = '63dd7ebad1xxxxxxxxxxxxxxxx' #Your actual weatherAPI key

def listen_to_speech(timeout=5):
    """Listen to speech and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
        print("Ambient noise adjusted.")
        
        try:
            audio = recognizer.listen(source, timeout=timeout)
            print("Audio captured.")
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return "Sorry, I did not understand that."
        except sr.RequestError as e:
            print(f"Sorry, there is an error encountered with the speech recognition service: {e}")
            return "Sorry, there is an error encountered with the speech recognition service."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred."

def speak(text):
    """Speak the given text using pyttsx3."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)  # Speed of speech
        voices = engine.getProperty('voices')
        # Set a female voice, if available
        for voice in voices:
            if 'female' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred while speaking: {e}")

def get_current_time():
    """Return the current time as a string."""
    return datetime.now().strftime("%H:%M:%S")

def get_current_date():
    """Return the current date as a string."""
    return datetime.now().strftime("%Y-%m-%d")

def get_weather(city):
    """Fetch weather data for a given city using WeatherAPI."""
    try:
        params = {
            'key': WEATHERAPI_API_KEY,
            'q': city,
            'aqi': 'no'  # Air quality info not required
        }
        response = requests.get(f'http://api.weatherapi.com/v1/current.json', params=params)
        data = response.json()
        
        if 'current' in data:
            temperature = data['current']['temp_c']
            weather_description = data['current']['condition']['text']
            return f"The current temperature in {city} is {temperature}°C with {weather_description}."
        else:
            return "Sorry, I couldn't fetch the weather information for that location."
    except Exception as e:
        print(f"An error occurred while fetching weather data: {e}")
        return "An error occurred while fetching weather data."

def open_browser(url):
    """Open the default web browser with a specific URL."""
    try:
        webbrowser.open(url)
        return "Opening your web browser now."
    except Exception as e:
        return f"An error occurred while trying to open the browser: {e}"

def search_web(query):
    """Search the web using Google and suggest based on the search."""
    try:
        query_text = query.replace("search", "", 1).strip()  # Remove the word 'search' from the query
        search_url = f"https://www.google.com/search?q={query_text}"
        webbrowser.open(search_url)
        save_query(query_text)
        
        # Ask for confirmation to click the first link
        speak("I have searched for your query. Should I click on the first link?")
        response = listen_to_speech(timeout=10)
        if "yes" in response.lower():
            speak("Clicking the first link now.")
            return f"Opened search results for '{query_text}'. Please click on the first link manually."
        else:
            return "Ok sir, I will not click the link unless you say so."
    except Exception as e:
        print(f"An error occurred while searching the web: {e}")
        return "An error occurred while searching the web."

def save_query(query):
    """Save the query to a JSON file."""
    if os.path.exists(QUERY_FILE):
        with open(QUERY_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = []

    data.append({
        'timestamp': get_current_time(),
        'query': query
    })

    try:
        with open(QUERY_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the query: {e}")

def get_suggestion(query):
    """Provide a suggestion based on the search query."""
    # Example suggestions based on common topics
    suggestions = {
        "python programming": "You might also want to check out some Python tutorials or documentation.",
        "machine learning": "Consider exploring some online courses or articles on machine learning.",
        "latest news": "Check out trending news on major news websites.",
        "movies": "You might enjoy reading reviews or watching trailers of recent movies."
    }

    for key in suggestions:
        if key in query.lower():
            return suggestions[key]
    
    return "I don't have specific suggestions for this topic."

def perform_internal_search(query):
    """Simulate an internal search and provide an immediate response."""
    # Predefined simulated results for internal search
    simulated_results = {
        "python programming": "Python programming involves learning about Python syntax, libraries, and best practices. Consider checking out resources like 'Automate the Boring Stuff with Python' or the official Python documentation.",
        "machine learning": "Machine learning focuses on algorithms and data analysis to predict outcomes. Popular resources include 'Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow' and online courses from Coursera or Udacity.",
        "latest news": "For the latest news, consider checking news aggregators like Google News or BBC News. They provide real-time updates on current events.",
        "movies": "Recent movies you might enjoy include 'Dune', 'No Time to Die', and 'The Matrix Resurrections'. Check out their trailers and reviews online.",
        "iron man actor": "Robert Downey Jr. is the actor who played Iron Man in the Marvel Cinematic Universe. He is well-known for his role as Tony Stark/Iron Man."
    }

    result = simulated_results.get(query.lower(), "I couldn't find specific information on that topic. Would you like me to dig more about it?")
    
    # Save the internal search request
    if os.path.exists(INTERNAL_SEARCH_FILE):
        with open(INTERNAL_SEARCH_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = []

    data.append({
        'timestamp': get_current_time(),
        'query': query,
        'result': result
    })

    try:
        with open(INTERNAL_SEARCH_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the internal search results: {e}")
    
    return f"I have completed the search for '{query}'. Here is what I found: {result}"

def read_internal_search_results():
    """Read out all the results from internal searches."""
    if os.path.exists(INTERNAL_SEARCH_FILE):
        try:
            with open(INTERNAL_SEARCH_FILE, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return "There was an error reading the search results."
        
        if not data:
            return "There are no results to read out at the moment."
        
        results = "Here are the results from the internal searches:"
        for entry in data:
            results += f"\nAt {entry['timestamp']}, you asked about '{entry['query']}' and I found: {entry['result']}"
        
        return results
    else:
        return "No internal search results found."

def introduce_myself():
    """Introduce the chatbot."""
    return (
        "Hello, I am FRIDAY, inspired by the AI from the Iron Man movies. "
        "I am here to assist you with various tasks, such as opening your web browser or performing Google searches. "
        "I can also keep track of your queries and provide suggestions based on your interests. "
        "How can I help you today?"
    )

def ping():
    """Simulate a ping response."""
    import time
    import random
    latency = random.randint(10, 100)  # Simulated latency in milliseconds
    response = f"Sir, this is my delay latency of {latency} milliseconds."
    return response

def help_function():
    """Provide help information."""
    return (
        "Here are the commands you can use:\n"
        "- 'search <query>': To search the web for the specified query.\n"
        "- 'weather <city>': To get the current weather for the specified city.\n"
        "- 'time': To get the current time.\n"
        "- 'date': To get the current date.\n"
        "- 'ping': To simulate a ping response and check latency.\n"
        "- 'help': To get this help information.\n"
        "- 'internal search <query>': To perform an internal search and get results.\n"
        "- 'read internal search results': To read out all the results from internal searches.\n"
        "- 'introduce yourself': To hear an introduction from me."
    )

def execute_command(command):
    """Execute the appropriate command based on user input."""
    if "search" in command.lower():
        return search_web(command)
    elif "weather" in command.lower():
        city = command.replace("weather", "", 1).strip()
        return get_weather(city)
    elif "time" in command.lower():
        return get_current_time()
    elif "date" in command.lower():
        return get_current_date()
    elif "ping" in command.lower():
        return ping()
    elif "help" in command.lower():
        return help_function()
    elif "internal search" in command.lower():
        query = command.replace("internal search", "", 1).strip()
        return perform_internal_search(query)
    elif "read internal search results" in command.lower():
        return read_internal_search_results()
    elif "introduce yourself" in command.lower():
        return introduce_myself()
    else:
        return "Sorry, I didn't understand that command."

def main():
    """Main function to run the assistant."""
    speak("Allow me to introduce myself, I am FRIDAY. How can I assist you today?")
    
    while True:
        command = listen_to_speech()
        if command.lower() in ["stop", "exit", "quit"]:
            speak("Goodbye! Have a great day!")
            break
        response = execute_command(command)
        speak(response)

if __name__ == "__main__":
    
    main()



#Codded By Debjit, share with proper credit

#Any issue mail me at Pauldebjit1211@gmail.com