from django.shortcuts import render
import folium
import pandas as pd
from folium import GeoJson


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


    # Get the csv file
    df = pd.read_csv("map/csvfiles/apims_final_id.csv")


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

    return render(request,'index.html',context)



#Comparison - real time vs historical
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
    df = pd.read_csv("map/csvfiles/apims_final_id.csv")

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