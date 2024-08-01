import pyttsx3
import speech_recognition as sr
import webbrowser
import json
import os
from datetime import datetime, timedelta
import requests
import sched
import time
import threading

# Paths to the files where queries and tasks are stored
QUERY_FILE = 'query_record.json'
INTERNAL_SEARCH_FILE = 'internal_search.json'
REMINDER_FILE = 'reminders.json'
MEETING_FILE = 'meetings.json'

# WeatherAPI configuration
WEATHERAPI_API_KEY = '63dd7ebadxxxxxxxxxxxxxxx' #Replace it with your weatherAPI key

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level

def speak(text):
    """Speak the given text using pyttsx3."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred while speaking: {e}")

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
            return f"Opened search results for '{query_text}'. Please click the first link manually."
        else:
            return "Okay, I will not click the link unless you ask me to."
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
    import random
    latency = random.randint(10, 100)  # Simulated latency in milliseconds
    response = f"Sir, my current delay latency is {latency} milliseconds."
    return response

def help_function():
    """Provide help information."""
    return (
        "Here are the commands you can use:\n"
        "- 'search <query>': To perform a web search and suggest results.\n"
        "- 'weather <city>': To get the current weather information for a given city.\n"
        "- 'time': To get the current time.\n"
        "- 'date': To get the current date.\n"
        "- 'ping': To simulate a ping response and check latency.\n"
        "- 'help': To get this help information.\n"
        "- 'internal search <query>': To perform an internal search and get results.\n"
        "- 'read internal search results': To read out all the results from internal searches.\n"
        "- 'introduce yourself': To hear an introduction from me.\n"
        "- 'set reminder <task> at <time>': To set a reminder for a specific task at a given time.\n"
        "- 'schedule meeting <description> at <datetime>': To schedule a meeting with a description and time."
    )

# Scheduler for handling reminders and meetings
scheduler = sched.scheduler(time.time, time.sleep)

def add_reminder(task, time_str):
    """Add a reminder to be triggered at a given time of day."""
    try:
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time)
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)  # Schedule for the next day if time is already passed today
        
        time_in_seconds = (reminder_datetime - now).total_seconds()
        scheduler.enter(time_in_seconds, 1, lambda: speak(f"Reminder: {task}"))
        
        reminders = load_json(REMINDER_FILE)
        reminders.append({
            'timestamp': get_current_time(),
            'task': task,
            'trigger_time': reminder_datetime.strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(REMINDER_FILE, reminders)
        return f"Reminder set for '{task}' at {time_str}"
    except ValueError as e:
        return f"Error in setting reminder: {e}"

def add_meeting(description, date_time_str):
    """Add a meeting with a description and scheduled time."""
    try:
        meeting_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        time_in_seconds = (meeting_time - datetime.now()).total_seconds()
        
        if time_in_seconds < 0:
            return "The meeting time is in the past. Please provide a future time."
        
        scheduler.enter(time_in_seconds, 1, lambda: speak(f"Meeting Reminder: {description}"))
        
        meetings = load_json(MEETING_FILE)
        meetings.append({
            'timestamp': get_current_time(),
            'description': description,
            'scheduled_time': date_time_str
        })
        save_json(MEETING_FILE, meetings)
        return f"Meeting scheduled for '{description}' at {date_time_str}"
    except ValueError as e:
        return f"Error in scheduling meeting: {e}"

def load_json(file_path):
    """Load JSON data from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_json(file_path, data):
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def execute_command(command):
    """Execute the appropriate command based on user input."""
    command = command.lower()
    if "search" in command:
        return search_web(command)
    elif "weather" in command:
        city = command.replace("weather", "", 1).strip()
        return get_weather(city)
    elif "time" in command:
        return get_current_time()
    elif "date" in command:
        return get_current_date()
    elif "ping" in command:
        return ping()
    elif "help" in command:
        return help_function()
    elif "internal search" in command:
        query = command.replace("internal search", "", 1).strip()
        return perform_internal_search(query)
    elif "read internal search results" in command:
        return read_internal_search_results()
    elif "introduce yourself" in command:
        return introduce_myself()
    elif "set reminder" in command:
        parts = command.replace("set reminder", "", 1).strip().split(" at ")
        if len(parts) == 2:
            task = parts[0].strip()
            time_str = parts[1].strip()
            return add_reminder(task, time_str)
        else:
            return "Please provide a task and a time in the format 'HH:MM'."
    elif "schedule meeting" in command:
        parts = command.replace("schedule meeting", "", 1).strip().split(" at ")
        if len(parts) == 2:
            description = parts[0].strip()
            date_time_str = parts[1].strip()
            return add_meeting(description, date_time_str)
        else:
            return "Please provide a description and a datetime in the format 'YYYY-MM-DD HH:MM:SS'."
    else:
        return "Sorry, I didn't understand that command."

def main():
    """Main function to run the assistant."""
    speak("Hello! I am FRIDAY, your personal assistant. How can I assist you today?")
    
    def scheduler_thread():
        while True:
            scheduler.run(blocking=False)
            time.sleep(1)
    
    # Start scheduler thread
    threading.Thread(target=scheduler_thread, daemon=True).start()

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
