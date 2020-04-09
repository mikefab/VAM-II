import json, sys
from tabulate import tabulate
with open('./config.json') as f:
  config = json.load(f)
import helper

# Fetch current and previous food insecure populations
# region_now and region_bef are a dictionaries of region_id to number of insecure people
region_to_people_now = helper.fetch_foodInsecure(0)
region_to_people_before = helper.fetch_foodInsecure(1)


# Fetch and create dictionary of region_id to total population
populations = helper.fetch_populations()

if len(sys.argv) == 1:
    # Fetch country regions and build a dictionary of country IDs to arrays of regions_ids.
    # example: {1: [272, 273...], 2: [432, 654...]...}
    print('About to make one API call per region. ' +
    'This will take a while. ' +
    'To run faster, run "python3 main.py test".'
    )
    country_regions = helper.fetch_country_regions(populations)
else:
    # Alternatively, for testing, this file is an archived version of the country_regions
    print('Running in test mode. This will go quickly')
    with open('./data/country_regions.json') as f:
      country_regions = json.load(f)

# Create a dictionary of countries to corresponding populations
# example: {'1': 60668669, '2': 6394, '3': 2793794,
country_populations = helper.countries_to_populations(populations, country_regions)

# Finally, iterate through each region
# tally up the percentage of food insecure people per country,
# for both today and 30 days prior.
# Then print out the IDs of countries whose percentage of
# insecure people have increased by 5% or more since the month prior.
countries_to_alert = []
for country in country_regions:
    tallyNow = 0
    tallyBef = 0
    for region in country_regions[country]:
        if region in region_to_people_now and region in region_to_people_before:
            tallyNow += region_to_people_now[region]
            tallyBef += region_to_people_before[region]
    if (tallyNow > 0 and tallyBef > 0):
        percentInsecureNow = tallyNow / country_populations[str(country)]
        percentInsecureBefore = tallyBef / country_populations[str(country)]
        change_percent = helper.get_change(percentInsecureNow, percentInsecureBefore)
        if(change_percent >= 5):
            countries_to_alert.append([country, round(change_percent, 2)])

print('Countries with a 5% or higher increase in food insecure people in the last 30 days:')
print(tabulate(countries_to_alert, headers=['Country ID', 'Percent increase']))
