from django.shortcuts import render
import folium
import pandas as pd
from folium import GeoJson
import json

# Create your views here.

def index(request):
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


    # DLoad the csv file
    df = pd.read_csv("map/csvfiles/apims_final_id.csv")


    date_range = 'Jan-21'
    
    if request.method == "POST":
        date_range = request.POST.get("date_range")
    
    color_values = {
        'blue': range(0, 51),
        'green': range(51, 101),
        'yellow': range(101, 201),
        'red': range(201, 301),
        'darkred': range(301, 9999999)
    }

    for i, row in df.iterrows():
        lat = df.at[i,'lat']
        lng = df.at[i,'lng']
        station = df.at[i,'station']
        value = df.at[i,date_range]
        print(value)

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

    groups = df.groupby('state')

    context = {
        'm': m,
        'groups': groups,
        'data_range': date_range,
               
    }

    return render(request,'index.html',context)



#Submap function
def submap(request,name):
    df = pd.read_csv("map/csvfiles/apims_final_id.csv")
    df = df.transpose()
    group = df[df['state'] == name]
    station_names = group['station'].tolist()
    month_rows = df.iloc[2:]  # Extract rows after the first two rows
    values = df.iloc[:2]  # Extract the first two rows

    month_rows = month_rows.values.tolist()
    values = values.values.tolist()

    for index, row in group.iterrows():
        station_name = row['station']
        month_rows[station_name] = row[2:]

    context = {
        'group': group,
        'name' : name,
        'station_names': station_names,
        'month_rows': month_rows, 
        'values': values,
    }
    return render(request, 'submap.html', context)
