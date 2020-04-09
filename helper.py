import csv, json
import urllib.request

with open('./config.json') as f:
  config = json.load(f)

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')

def fetch_populations():
    url = config['urls']['population']
    popCSV = urllib.request.urlopen(url)
    datareader = csv.reader(popCSV.read().decode('utf-8').splitlines())
    populations = []
    for row in datareader:
        populations.append(row)
    return populations

def fetch_foodInsecure(before):
    # fetch map of region_ids to number of food insecure people.
    # return a dictionary of region_id to number of food insecure people
    # This makes grouping regions by country easier
    if before == 0:
        url = config['urls']['food_security']
    else:
        url = config['urls']['food_security_before']
    json_url = urllib.request.urlopen(url)
    food = {}
    for key in json.loads(json_url.read()):
        food[key['region_id']] = key['food_insecure_people']
    return food

def fetch_country_regions(populations):
    country_regions = {}
    for index, record in enumerate(populations):
        if index > 0:
            url = config['urls']['country_regions'].format(record[0])
            with urllib.request.urlopen(url) as url:
                data = json.loads(url.read().decode())
                if data['country_id'] in country_regions:
                    country_regions[data['country_id']].append(data['region_id'])
                else:
                    country_regions[data['country_id']] = [data['region_id']]
    return(country_regions)

def countries_to_populations(populations, country_regions):
    region_population = form_region_population(populations)
    country_population = {}
    for country in country_regions:
        for region in country_regions[country]:
            if str(region) in region_population:
                if country in country_population:
                    country_population[country] += region_population[str(region)]
                else:
                    country_population[country] = region_population[str(region)]
    return country_population


def form_region_population(populations):
    region_population = {}
    for record in populations:
        try:
            region_population[record[0]] = int(record[1])
        except:
            # print('Cannot convert value to int.')
            pass
    return region_population
