import re
import folium
import requests
from urllib import parse
import numpy as np
import pandas as pd
from folium import GeoJson
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

colors = {
            "Good": "#3E8AF6",
            "Moderate": "#7CDE6B",
            "Unhealthy": "#FFFF00",
            "Very Unhealthy": "#FFA833",
            "Hazardous": "#FF3823",
        }


def get_data():
    api_url = 'http://apims.doe.gov.my/data/public_v2/CAQM/last24hours.json'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        labels = data['24hour_api_apims'][0][2:]
        states = data['24hour_api_apims'][1:]
        result = []
        for _, state in enumerate(states):
          data = [int(re.sub('[^0-9]', '', value.replace("*", "").replace("&","").replace('N/A', '0'))) for value in state[2:]]
          state_name = state[0].capitalize()
          result.append({
                "state": state_name,
                "location": state[1],
                "value": data[-1],
                "values": data,
                "labels": labels
            })
        return result
    else:
        return None


def show_bar_graph(request):
    referer = request.META.get('HTTP_REFERER')
    state=parse.parse_qs(parse.urlparse(referer).query)['state'][0]
    station=parse.parse_qs(parse.urlparse(referer).query)['station'][0]
    fig = Figure(figsize=(12, 9))
    ax = fig.add_subplot(1, 1, 1)
    data = get_data()
    colorsData = []
    for stateData in data:
        if stateData['state'] == state:
            if stateData['location'] == station:
                values = stateData['values']
                for value in values:
                    if value <= 50:
                        colorsData.append(colors["Good"])
                    if value > 50 and value <= 100:
                        colorsData.append(colors["Moderate"])
                    if value > 100 and value <= 200:
                        colorsData.append(colors["Unhealthy"])
                    if value > 200 and value <= 300:
                        colorsData.append(colors["Very Unhealthy"])
                    if value > 300:
                        colorsData.append(colors["Hazardous"])
                ax.barh(stateData['labels'], values, color=colorsData)
                ax.set_title(stateData['state']+" - "+stateData['location'])
                ax.set_xlabel('AP Index')
                ax.set_ylabel('Time')
                canvas = FigureCanvasAgg(fig)
                response = HttpResponse(content_type='image/png')
                canvas.print_png(response)
                return response

def show_historical_bar_graph(request):
    referer = request.META.get('HTTP_REFERER')
    state=parse.parse_qs(parse.urlparse(referer).query)['state'][0]
    station=parse.parse_qs(parse.urlparse(referer).query)['station'][0]
    fig = Figure(figsize=(12, 9))
    ax = fig.add_subplot(1, 1, 1)
    data = pd.read_csv("map/csvfiles/apims_final_id.csv")
    labels = ['Jan-21', 'Feb-21', 'Mar-21',
       'Apr-21', 'May-21', 'Jun-21', 'Jul-21', 'Aug-21', 'Sep-21', 'Oct-21',
       'Nov-21', 'Dec-21', 'Jan-20', 'Feb-20', 'Mar-20', 'Apr-20', 'May-20',
       'Jun-20', 'Jul-20', 'Aug-20', 'Sep-20', 'Oct-20', 'Nov-20', 'Dec-20',
       'Jan-19', 'Feb-19', 'Mar-19', 'Apr-19', 'May-19', 'Jun-19', 'Jul-19',
       'Aug-19', 'Sep-19', 'Oct-19', 'Nov-19', 'Dec-19']
    colorsData = []
    values = data[labels][data['Station'] == station].values[0]
    for value in values:
        if value <= 50:
            colorsData.append(colors["Good"])
        if value > 50 and value <= 100:
            colorsData.append(colors["Moderate"])
        if value > 100 and value <= 200:
            colorsData.append(colors["Unhealthy"])
        if value > 200 and value <= 300:
            colorsData.append(colors["Very Unhealthy"])
        if value > 300:
            colorsData.append(colors["Hazardous"])
    ax.barh(labels, values, color=colorsData)
    ax.set_title(state+" - "+station)
    ax.set_xlabel('AP Index')
    ax.set_ylabel('Time')
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def home(request):
     #Create map
    m = folium.Map(location=[5.420404, 108.796783], zoom_start=6)

    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(m)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m)

    geo=r"map/csvfiles/malaysia.geojson"
    file = open(geo, encoding="utf8")
    text = file.read()
    GeoJson(text).add_to(m)


    # Get the csv file
    df = pd.read_csv("map/csvfiles/apims_final.csv")


    date_range = '2021-12'
    
    if request.method == "POST":
        date_range = request.POST.get("date_range")
       
    
    color_values = {
        'cornflowerblue': range(0, 51),
        'limegreen': range(51, 101),
        'yellow': range(101, 201),
        'orange': range(201, 301),
        'red': range(301, 9999999)
    }

    for i, row in df.iterrows():
        lat = df.at[i,'lat']
        lng = df.at[i,'lng']
        station = df.at[i,'station']
        value = df.at[i,date_range]
        

        color = 'blue'
        for key, value_range in color_values.items():
            if value in value_range:
                color = key
                break
        html = f'<div style="background-color:{color}; width: 30px; height: 30px; border-radius: 15px; display: flex; align-items: center; justify-content: center;">{value}</div>'
        icon = folium.DivIcon(html=html)
        folium.Marker(location=[lat, lng],tooltip= station,icon=icon).add_to(m)   
        
    folium.LayerControl().add_to(m)


    #Get html representation of map
    m = m._repr_html_()

    context = {
        'm': m,
        'data_range': date_range,
               
    }

    return render(request,'home.html',context)

def index(request):
    #Create map
    m = folium.Map(location=[5.420404, 108.796783], zoom_start=6)

    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(m)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m)
    folium.raster_layers.TileLayer('OpenStreetMap').add_to(m)

    geo=r"map/csvfiles/malaysia.geojson"
    file = open(geo, encoding="utf8")
    text = file.read()
    GeoJson(text).add_to(m)

    
    folium.LayerControl().add_to(m)
    df = pd.read_csv("map/csvfiles/state.csv")

    for i, row in df.iterrows():
        lat = df.at[i,'lat']
        lon = df.at[i,'lng']
        State = df.at[i,'State']
        popup = '<input type="text" value="{}" style="border: 1px solid rgba(0,0,0,0.3); border-radius: 10px; padding: 5px 20px;" id="currentState"><button onclick="window.open(\'http://localhost:8000/graph?state={}\')" style="border: none; background: black; color: white; font-size: 13px; padding: 5px 10px; border-radius: 10px; margin-top: 10px;">Show Stations</button>'.format(State, State)
        marker = folium.Marker(location=[lat, lon],tooltip= State)
        marker.add_to(m)
        folium.Popup(popup).add_to(marker)

    #Get html representation of map
    m = m._repr_html_()


    # Display all of the state
    df = pd.read_csv("map/csvfiles/state.csv")
    # add markers to the map
    for i, row in df.iterrows():
        id = df.at[i,'id']
        name = df.at[i,'State']
        state = id , name
    
    context = {
        'm': m,
        'state': state,
    }
    return render(request,'index.html',context)

def submap(request, *args, **kwargs):
    state = request.GET.get("state")
    station = request.GET.get("station", None)
    y_labels = ["4:00PM", "5:00PM", "6:00PM", "7:00PM", "8:00PM", "9:00PM", "10:00PM", "11:00PM", "12:00AM", "1:00AM", "2:00AM", "3:00AM", "4:00AM", "5:00AM", "6:00AM", "7:00AM", "8:00AM", "9:00AM", "10:00AM", "11:00AM", "12:00PM", "1:00PM", "2:00PM", "3:00PM"]
    data = get_data()
    locations = []
    if data:
        if data:
            for stateData in data:
                if stateData['state'] == state:
                    value = stateData['value']
                    if value <= 50:
                        locations.append({
                            "location": stateData['location'],
                            "color": colors['Good']
                        })
                    if value > 50 and value <= 100:
                        locations.append({
                            "location": stateData['location'],
                            "color": colors['Moderate']
                        })
                    if value > 100 and value <= 200:
                        locations.append({
                            "location": stateData['location'],
                            "color": colors['Unhealthy']
                        })
                    if value > 200 and value <= 300:
                        locations.append({
                            "location": stateData['location'],
                            "color": colors['Very Unhealthy']
                        })
                    if value > 300:
                        locations.append({
                            "location": stateData['location'],
                            "color": colors['Hazardous']
                        })
    if len(locations) > 0:
        if station:
            return render(request,'submap.html', {'locations': locations, 'y_labels': y_labels, "station": True})
        else:
            return render(request,'submap.html', {'locations': locations, 'y_labels': y_labels, "station": False})     
    return render(request,'submap.html', {'locations': False, 'y_labels': y_labels, "station": False})

def compare(request):
    #Create map
    m1 = folium.Map(location=[4.64865,101.10757], zoom_start=6)
    m2 = folium.Map(location=[4.64865,101.10757], zoom_start=6)

    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m1)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(m1)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m1)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m1)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m1)

    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m2)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(m2)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m2)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m2)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m2)

    geo=r"map/csvfiles/malaysia.geojson"
    file = open(geo, encoding="utf8")
    text = file.read()
    GeoJson(text).add_to(m1)

    geo=r"map/csvfiles/malaysia.geojson"
    file = open(geo, encoding="utf8")
    text = file.read()
    GeoJson(text).add_to(m2)


    # Get the csv file
    df = pd.read_csv("map/csvfiles/apims_final.csv")

    date_range1 = '2019-12'
    date_range2 = '2021-12'
    
    if request.method == "POST":
        if 'submit_map1' in request.POST:
            date_range1 = request.POST.get("date_range1")
        elif 'submit_map2' in request.POST:
            date_range2 = request.POST.get("date_range2")

    
    color_values = {
        'cornflowerblue': range(0, 51),
        'limegreen': range(51, 101),
        'yellow': range(101, 201),
        'orange': range(201, 301),
        'red': range(301, 9999999)
    }

    for i, row in df.iterrows():
        lat = df.at[i,'lat']
        lng = df.at[i,'lng']
        station = df.at[i,'station']
        value1 = df.at[i,date_range1]
        
        color = 'blue'
        for key, value_range in color_values.items():
            if value1 in value_range:
                color = key
                break
        html1 = f'<div style="background-color:{color}; width: 30px; height: 30px; border-radius: 15px; display: flex; align-items: center; justify-content: center;">{value1}</div>'
        icon1 = folium.DivIcon(html=html1)
        folium.Marker(location=[lat, lng],tooltip= station,icon=icon1).add_to(m1)   
        
    folium.LayerControl().add_to(m1)


    for i, row in df.iterrows():
        lat = df.at[i,'lat']
        lng = df.at[i,'lng']
        station = df.at[i,'station']
        value2 = df.at[i,date_range2]
        

        color = 'blue'
        for key, value_range in color_values.items():
            if value2 in value_range:
                color = key
                break
        html2 = f'<div style="background-color:{color}; width: 30px; height: 30px; border-radius: 15px; display: flex; align-items: center; justify-content: center;">{value2}</div>'
        icon2 = folium.DivIcon(html=html2)
        folium.Marker(location=[lat, lng],tooltip= station,icon=icon2).add_to(m2)
    folium.LayerControl().add_to(m2)

    #Get html representation of map
    m1 = m1._repr_html_()
    m2 = m2._repr_html_()

    context = {
        'm1':m1,
        'm2': m2,
        'data_range1': date_range1,
        'data_range2': date_range2,
               
    }
    return render(request,'compare.html',context)
