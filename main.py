pip install folium

pip install geopy

import heapq
import folium
from geopy.geocoders import Nominatim


def get_user_input():
    edges = []
    print("Bağlantıları girin (örn: Türkiye Almanya 500), bitirmek için 'done' yazın:")
    while True:
        entry = input("Bağlantı: ")
        if entry.lower() == 'done':
            break
        try:
            from_country, to_country, cost = entry.split()
            edges.append((from_country, to_country, int(cost)))
        except ValueError:
            print("Geçersiz giriş! 'Ülke1 Ülke2 Mesafe' formatında olmalı.")
    return edges


class Graph:
    def __init__(self):
        self.nodes = {}

    def add_edge(self, from_country, to_country, cost):
        self.nodes.setdefault(from_country, []).append((to_country, cost))
        self.nodes.setdefault(to_country, []).append((from_country, cost))

    def dijkstra(self, start, end):
        queue = [(0, start)]
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous_nodes = {node: None for node in self.nodes}

        while queue:
            current_distance, current_node = heapq.heappop(queue)
            if current_node == end:
                break
            for neighbor, weight in self.nodes.get(current_node, []):
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

        path, node = [], end
        while node:
            path.append(node)
            node = previous_nodes[node]

        return path[::-1], distances[end]


def get_coordinates(countries):
    geolocator = Nominatim(user_agent="simple_route_planner")
    coords = {}
    for country in countries:
        location = geolocator.geocode(country)
        if location:
            coords[country] = [location.latitude, location.longitude]
        else:
            print(f"Koordinat bulunamadı: {country}")
    return coords


def create_map(route, coords):
    map_ = folium.Map(location=[20, 0], zoom_start=2)
    for i in range(len(route) - 1):
        from_country, to_country = route[i], route[i + 1]
        if from_country in coords and to_country in coords:
            folium.Marker(location=coords[from_country], popup=from_country).add_to(map_)
            folium.Marker(location=coords[to_country], popup=to_country).add_to(map_)
            folium.PolyLine([coords[from_country], coords[to_country]], color='blue').add_to(map_)
    map_.save("route_map.html")
    print("Harita oluşturuldu: route_map.html")


# Kullanıcı girişi
edges = get_user_input()
graph = Graph()
for edge in edges:
    graph.add_edge(*edge)

start_country = input("Başlangıç ülkesini girin: ")
end_country = input("Hedef ülkesini girin: ")

# En kısa rota ve maliyet
route, cost = graph.dijkstra(start_country, end_country)
print(f"En kısa rota: {route}, Toplam maliyet: {cost}")

# Harita oluşturma
coordinates = get_coordinates(route)
create_map(route, coordinates)
