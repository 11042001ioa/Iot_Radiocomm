import tkinter as tk
from tkinter import ttk
import webbrowser
import folium
import os
import requests
import json
from datetime import datetime
from tkcalendar import Calendar
from geopy.distance import geodesic
import geocoder


def open_map_in_browser():
    # Save the Folium map to an HTML file
    m.save("map.html")

    # Open the HTML file in the default web browser
    webbrowser.get('chrome').open('file://' + os.path.realpath("map.html"))


# Create a Tkinter window
root = tk.Tk()
root.title("Map in GUI")
root.geometry("1280x720")

# Create a notebook to hold tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create a tab for the map
map_frame = ttk.Frame(notebook, width=800, height=600)
notebook.add(map_frame, text="Statistics of your trip")

# Create a Folium map
response_API = requests.get('https://api.thingspeak.com/channels/2300633/feeds.json?api_key=I2CM4ZQPIFXT4QMQ')
data = response_API.text
parse_json = json.loads(data)

cal = Calendar(map_frame, selectmode="day", date_pattern="yyyy-mm-dd", font="Arial 20")
cal.pack(padx=10, pady=10)

# Create a button to get the selected date


# Create a label to display the selected date
result_label = ttk.Label(root, text="")
result_label.pack()

# iterate through raw data and extract only the needed one
datetime_obj = datetime.fromisoformat(parse_json['feeds'][20]['created_at'])

point1 = ''
point2 = ''


def updateLabel(event):
    text_widget.delete(1.0, tk.END)
    day = cal.get_date()
    points = []
    distance = 0
    start_time = ''
    finish_time = ''
    for record in parse_json['feeds']:
        if str(datetime.fromisoformat(record['created_at']).date()) == str(day) and record['field1'] != '' and record[
            'field1'] != None and record['field2'] != '' and record['field2'] != None:
            points.append((float(record['field1']), float(record['field2'])))
            folium.Marker([float(record['field1']), float(record['field2'])]).add_to(m)
            point2 = (float(record['field1']), float(record['field2']))
            if start_time == '':
                start_time = datetime.fromisoformat(record['created_at'])
                point1 = (float(record['field1']), float(record['field2']))
            finish_time = datetime.fromisoformat(record['created_at'])
            distance = distance + geodesic(point1, point2).kilometers
            point1 = point2
    folium.PolyLine(points).add_to(m)
    trip = finish_time - start_time
    speed = distance*1000/trip.total_seconds()
    #text_widget.delete(1.0, tk.END)  # Clear the existing text
    text_widget.insert(tk.END, f"Trip duration: {trip}\n")
    text_widget.insert(tk.END, f"Distance: {distance*1000} meters\n")
    text_widget.insert(tk.END, f"Avg Speed: {speed} m/s")


cal.bind('<<CalendarSelected>>', updateLabel)

g = geocoder.ip('me')
date = datetime_obj.date()
time = datetime_obj.time()
m = folium.Map(location=g.latlng, zoom_start=12)
text_widget = tk.Text(map_frame, height=5, width=40, font="Arial 15")
text_widget.pack()
# Create a button to open the map in a web browser
open_button = ttk.Button(map_frame, text="See your trip in browser", command=open_map_in_browser)
open_button.pack()

# Start the Tkinter event loop
root.mainloop()
