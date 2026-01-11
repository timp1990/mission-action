"""
Generate action_sports_by_country.csv based on web research data.
This script creates boolean mappings for 50 action sports across 238 countries.
"""

import pandas as pd
from pathlib import Path

# Define the 50 action sports with their column names
ACTION_SPORTS = {
    # Water Sports - Coastal (10)
    'surfing': 'Surfing',
    'kitesurfing': 'Kitesurfing',
    'windsurfing': 'Windsurfing',
    'scuba_diving': 'Scuba Diving',
    'snorkeling': 'Snorkeling',
    'sup': 'Stand-up Paddleboarding',
    'bodyboarding': 'Bodyboarding',
    'jet_skiing': 'Jet Skiing',
    'wakeboarding': 'Wakeboarding',
    'cliff_diving': 'Cliff Diving',

    # Snow/Winter Sports (8)
    'skiing': 'Skiing',
    'snowboarding': 'Snowboarding',
    'freestyle_skiing': 'Freestyle Skiing',
    'backcountry_skiing': 'Backcountry Skiing',
    'ice_climbing': 'Ice Climbing',
    'snowmobiling': 'Snowmobiling',
    'xc_skiing': 'Cross-country Skiing',
    'heli_skiing': 'Heli-skiing',

    # Mountain/Terrain Sports (8)
    'rock_climbing': 'Rock Climbing',
    'mountaineering': 'Mountaineering',
    'paragliding': 'Paragliding',
    'hang_gliding': 'Hang Gliding',
    'bungee_jumping': 'Bungee Jumping',
    'via_ferrata': 'Via Ferrata',
    'canyoning': 'Canyoning',
    'ziplining': 'Zip-lining',

    # River/Lake Sports (8)
    'white_water_rafting': 'White Water Rafting',
    'kayaking': 'Kayaking',
    'canoeing': 'Canoeing',
    'jet_boating': 'Jet Boating',
    'lake_wakeboarding': 'Lake Wakeboarding',
    'water_skiing': 'Water Skiing',
    'tubing': 'Tubing',
    'flyboarding': 'Flyboarding',

    # Universal Land Sports (10)
    'skateboarding': 'Skateboarding',
    'bmx': 'BMX',
    'mountain_biking': 'Mountain Biking',
    'motocross': 'Motocross',
    'inline_skating': 'Inline Skating',
    'parkour': 'Parkour',
    'trail_running': 'Trail Running',
    'atv_quad': 'ATV/Quad Biking',
    'go_karting': 'Go-karting',
    'obstacle_racing': 'Obstacle Course Racing',

    # Air Sports (6)
    'skydiving': 'Skydiving',
    'base_jumping': 'Base Jumping',
    'wingsuit': 'Wingsuit Flying',
    'hot_air_ballooning': 'Hot Air Ballooning',
    'powered_paragliding': 'Powered Paragliding',
    'indoor_skydiving': 'Indoor Skydiving',
}

# Landlocked countries (44) - NO ocean sports
LANDLOCKED = {
    # Africa (16)
    'Botswana', 'Burkina Faso', 'Burundi', 'Central African Republic',
    'Chad', 'Ethiopia', 'Lesotho', 'Malawi', 'Mali', 'Niger',
    'Rwanda', 'South Sudan', 'Uganda', 'Zambia', 'Zimbabwe',
    # Europe (16)
    'Andorra', 'Austria', 'Belarus', 'Czechia', 'Hungary', 'Kosovo',
    'Liechtenstein', 'Luxembourg', 'Moldova', 'North Macedonia',
    'San Marino', 'Serbia', 'Slovakia', 'Switzerland', 'Vatican City',
    'Armenia',  # Also landlocked
    # Asia (12)
    'Afghanistan', 'Azerbaijan', 'Bhutan', 'Kazakhstan',
    'Kyrgyzstan', 'Laos', 'Mongolia', 'Nepal', 'Tajikistan',
    'Turkmenistan', 'Uzbekistan',
    # South America (2)
    'Bolivia', 'Paraguay',
}

# Countries with skiing infrastructure (67+)
SKIING_COUNTRIES = {
    # Europe
    'Austria', 'Switzerland', 'France', 'Italy', 'Germany', 'Spain',
    'Andorra', 'Norway', 'Sweden', 'Finland', 'Iceland', 'Poland',
    'Czechia', 'Slovakia', 'Slovenia', 'Romania', 'Bulgaria',
    'Greece', 'Turkey', 'United Kingdom', 'Scotland', 'Ireland',
    'Belgium', 'Netherlands', 'Denmark', 'Serbia', 'Montenegro',
    'Bosnia-Herzegovina', 'Croatia', 'Albania', 'North Macedonia',
    'Kosovo', 'Ukraine', 'Russia', 'Belarus', 'Lithuania', 'Latvia',
    'Estonia', 'Hungary', 'Cyprus', 'Portugal', 'Liechtenstein',
    'Georgia',
    # North America
    'United States', 'Canada', 'Mexico',
    # Asia
    'Japan', 'China', 'South Korea', 'North Korea', 'India', 'Pakistan',
    'Nepal', 'Iran', 'Lebanon', 'Israel', 'Kazakhstan', 'Kyrgyzstan',
    'Tajikistan', 'Uzbekistan', 'Afghanistan', 'Mongolia', 'Taiwan',
    'Azerbaijan', 'Armenia',
    # Oceania
    'Australia', 'New Zealand',
    # South America
    'Chile', 'Argentina', 'Bolivia', 'Peru', 'Ecuador', 'Colombia',
    # Africa
    'Morocco', 'South Africa', 'Lesotho',
    # Middle East
    'Saudi Arabia', 'United Arab Emirates', 'Qatar',  # Indoor
}

# Countries with surfing (120+)
SURFING_COUNTRIES = {
    # Europe
    'Portugal', 'Spain', 'France', 'Ireland', 'United Kingdom',
    'Iceland', 'Norway', 'Sweden', 'Denmark', 'Finland',
    'Italy', 'Greece', 'Cyprus', 'Malta', 'Turkey',
    'Romania', 'Bulgaria', 'Poland', 'Latvia', 'Lithuania', 'Estonia',
    # Africa
    'Morocco', 'Senegal', 'Gambia', 'Guinea-Bissau', 'Guinea',
    'Sierra Leone', 'Liberia', "Cote d'Ivoire", 'Ghana', 'Nigeria',
    'Cameroon', 'South Africa', 'Namibia', 'Angola', 'Mozambique',
    'Madagascar', 'Mauritius', 'Reunion', 'Seychelles', 'Comoros',
    'Cape Verde', 'Kenya', 'Tanzania', 'Somalia',
    # North America
    'United States', 'Canada', 'Mexico',
    # Central America & Caribbean
    'Belize', 'Guatemala', 'Honduras', 'El Salvador', 'Nicaragua',
    'Costa Rica', 'Panama', 'Cuba', 'Jamaica', 'Puerto Rico',
    'Dominican Republic', 'Haiti', 'Barbados', 'Trinidad and Tobago',
    'Bahamas', 'Antigua and Barbuda', 'St Lucia', 'Grenada',
    'St Vincent and Grenadines', 'Dominica', 'Aruba', 'Curacao',
    'Cayman Islands', 'Virgin Islands US', 'British Virgin Islands',
    'Martinique', 'Guadeloupe', 'Bermuda', 'Turks and Caicos Islands',
    # South America
    'Colombia', 'Venezuela', 'Guyana', 'Suriname', 'French Guiana',
    'Brazil', 'Uruguay', 'Argentina', 'Chile', 'Peru', 'Ecuador',
    # Asia
    'Israel', 'Lebanon', 'Saudi Arabia', 'Yemen', 'Oman',
    'United Arab Emirates', 'Qatar', 'Kuwait', 'Bahrain', 'Iran',
    'Pakistan', 'India', 'Bangladesh', 'Sri Lanka', 'Maldives',
    'Myanmar', 'Thailand', 'Cambodia', 'Vietnam', 'Malaysia',
    'Singapore', 'Indonesia', 'Brunei', 'Philippines', 'Timor-Leste',
    'China', 'China Hong Kong', 'Taiwan', 'South Korea', 'Japan',
    'Russia',
    # Oceania
    'Australia', 'New Zealand', 'Papua New Guinea', 'Solomon Islands',
    'Vanuatu', 'New Caledonia', 'Fiji', 'Tonga', 'Samoa', 'American Samoa',
    'Cook Islands', 'French Polynesia', 'Kiribati', 'Tuvalu',
    'Marshall Islands', 'Micronesia Federated States', 'Palau', 'Guam',
    'Northern Mariana Islands',
}

# Countries with scuba diving (nearly all coastal)
SCUBA_DIVING_COUNTRIES = SURFING_COUNTRIES.union({
    # Additional diving destinations
    'Egypt', 'Sudan', 'Djibouti', 'Eritrea', 'Tunisia', 'Algeria', 'Libya',
    'Togo', 'Benin', 'Equatorial Guinea', 'Gabon', 'Congo Republic of the',
    'Congo Democratic Republic', 'Sao Tome and Principe', 'Saint Helena',
    'Slovenia', 'Croatia', 'Montenegro', 'Albania', 'Georgia',
    'Anguilla', 'Montserrat', 'Saint Kitts and Nevis', 'Sint Maarten',
    'Greenland', 'Svalbard',
})

# Countries with rock climbing (100+)
ROCK_CLIMBING_COUNTRIES = {
    # Europe
    'Austria', 'Belgium', 'France', 'Germany', 'Luxembourg', 'Netherlands',
    'Switzerland', 'Greece', 'Italy', 'Malta', 'Portugal', 'Spain',
    'Denmark', 'Finland', 'Iceland', 'Norway', 'Sweden', 'United Kingdom',
    'Ireland', 'Czechia', 'Hungary', 'Poland', 'Romania', 'Slovakia',
    'Albania', 'Bosnia-Herzegovina', 'Bulgaria', 'Croatia', 'Kosovo',
    'Montenegro', 'North Macedonia', 'Serbia', 'Slovenia', 'Andorra',
    'Cyprus', 'Monaco', 'Turkey', 'Russia', 'Ukraine',
    # Asia
    'China', 'Japan', 'Mongolia', 'South Korea', 'Taiwan', 'Cambodia',
    'Indonesia', 'Laos', 'Malaysia', 'Myanmar', 'Philippines', 'Singapore',
    'Thailand', 'Vietnam', 'Bangladesh', 'India', 'Nepal', 'Pakistan',
    'Sri Lanka', 'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Uzbekistan',
    'Israel', 'Jordan', 'Lebanon', 'Oman', 'Saudi Arabia',
    'United Arab Emirates', 'Yemen',
    # Africa
    'Algeria', 'Egypt', 'Libya', 'Morocco', 'Tunisia', 'Ethiopia',
    'Kenya', 'Madagascar', 'Tanzania', 'Uganda', 'Botswana', 'Mozambique',
    'Namibia', 'South Africa', 'Zimbabwe', 'Mali', 'Senegal',
    # Americas
    'Canada', 'Mexico', 'United States', 'Belize', 'Costa Rica',
    'El Salvador', 'Guatemala', 'Honduras', 'Nicaragua', 'Panama',
    'Cuba', 'Curacao', 'Dominican Republic', 'Jamaica', 'Puerto Rico',
    'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador',
    'Peru', 'Suriname', 'Uruguay', 'Venezuela',
    # Oceania
    'Australia', 'French Polynesia', 'Guam', 'Kiribati', 'New Caledonia',
    'New Zealand', 'Papua New Guinea', 'Samoa', 'Tonga', 'Vanuatu',
}

# Countries with white water rafting (73)
WHITE_WATER_RAFTING_COUNTRIES = {
    # North America
    'United States', 'Canada', 'Mexico',
    # Central America
    'Belize', 'Guatemala', 'Honduras', 'Nicaragua', 'Costa Rica', 'Panama',
    'Dominican Republic',
    # South America
    'Colombia', 'Ecuador', 'Peru', 'Brazil', 'Chile', 'Argentina',
    # Europe
    'United Kingdom', 'Iceland', 'Norway', 'Finland', 'France', 'Spain',
    'Portugal', 'Italy', 'Switzerland', 'Austria', 'Germany', 'Netherlands',
    'Czechia', 'Poland', 'Slovakia', 'Slovenia', 'Croatia',
    'Bosnia-Herzegovina', 'Montenegro', 'Serbia', 'Albania', 'Greece',
    'Bulgaria', 'Romania', 'Turkey',
    # Middle East
    'Israel', 'United Arab Emirates',
    # Africa
    'Morocco', 'Ethiopia', 'Kenya', 'Uganda', 'Rwanda', 'Tanzania',
    'Zambia', 'Zimbabwe', 'Namibia', 'South Africa', 'Madagascar',
    # Asia
    'Russia', 'Pakistan', 'Nepal', 'Bhutan', 'India', 'China', 'Japan',
    'South Korea', 'Taiwan', 'Thailand', 'Laos', 'Vietnam', 'Philippines',
    'Malaysia', 'Indonesia', 'Sri Lanka',
    # Oceania
    'Australia', 'New Zealand', 'Fiji',
}

# Countries with paragliding (90+)
PARAGLIDING_COUNTRIES = {
    # Europe
    'Albania', 'Austria', 'Belgium', 'Bosnia-Herzegovina', 'Bulgaria',
    'Croatia', 'Czechia', 'Denmark', 'Finland', 'France', 'Georgia',
    'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
    'Kosovo', 'North Macedonia', 'Netherlands', 'Norway', 'Poland',
    'Portugal', 'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
    'Sweden', 'Switzerland', 'Turkey', 'United Kingdom', 'Ukraine',
    # Asia
    'Afghanistan', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Cambodia',
    'China', 'China Hong Kong', 'India', 'Indonesia', 'Iran', 'Israel',
    'Japan', 'Jordan', 'Lebanon', 'Malaysia', 'Nepal', 'Pakistan',
    'Philippines', 'Singapore', 'South Korea', 'Sri Lanka', 'Taiwan',
    'Thailand', 'United Arab Emirates', 'Vietnam',
    # Africa
    'Algeria', 'Egypt', 'Ethiopia', 'Kenya', 'Morocco', 'South Africa',
    'Tanzania', 'Tunisia', 'Uganda', 'Zimbabwe',
    # Americas
    'Canada', 'Costa Rica', 'Guatemala', 'Mexico', 'Nicaragua', 'Panama',
    'United States', 'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia',
    'Ecuador', 'Paraguay', 'Peru', 'Uruguay', 'Venezuela',
    'Dominican Republic',
    # Oceania
    'Australia', 'New Zealand',
}

# Countries with skydiving (97+)
SKYDIVING_COUNTRIES = {
    # Europe
    'Austria', 'Belgium', 'Bosnia-Herzegovina', 'Bulgaria', 'Croatia',
    'Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland', 'France',
    'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
    'Latvia', 'Lithuania', 'Luxembourg', 'North Macedonia', 'Moldova',
    'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia',
    'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland',
    'Turkey', 'Ukraine', 'United Kingdom',
    # Africa
    'Egypt', 'Ghana', 'Kenya', 'Mauritius', 'Morocco', 'Namibia',
    'Nigeria', 'South Africa', 'Tanzania', 'Zambia', 'Zimbabwe',
    # Asia
    'China', 'India', 'Indonesia', 'Israel', 'Japan', 'Jordan',
    'Kuwait', 'Malaysia', 'Nepal', 'Pakistan', 'Philippines', 'Qatar',
    'Saudi Arabia', 'Thailand', 'United Arab Emirates',
    # Americas
    'Canada', 'Costa Rica', 'Curacao', 'El Salvador', 'Guatemala',
    'Mexico', 'Panama', 'United States', 'Argentina', 'Bolivia',
    'Brazil', 'Chile', 'Colombia', 'Cuba', 'Dominican Republic',
    'Ecuador', 'Peru', 'Uruguay', 'Paraguay', 'Suriname', 'Venezuela',
    'Bahamas', 'Belize',
    # Oceania
    'Australia', 'New Zealand',
}

# Countries with kitesurfing (95+)
KITESURFING_COUNTRIES = {
    # Europe
    'Austria', 'Croatia', 'Denmark', 'Finland', 'France', 'Germany',
    'Greece', 'Iceland', 'Ireland', 'Italy', 'Montenegro', 'Netherlands',
    'Norway', 'Poland', 'Portugal', 'Spain', 'Sweden', 'Turkey',
    'United Kingdom',
    # Africa
    'Cape Verde', 'Egypt', 'Kenya', 'Madagascar', 'Mauritius', 'Morocco',
    'Mozambique', 'Namibia', 'Senegal', 'South Africa', 'Tanzania',
    # Middle East
    'Bahrain', 'Israel', 'Jordan', 'Lebanon', 'Oman', 'Qatar',
    'Saudi Arabia', 'United Arab Emirates',
    # Asia
    'India', 'Indonesia', 'Japan', 'Malaysia', 'Philippines', 'Singapore',
    'South Korea', 'Sri Lanka', 'Taiwan', 'Thailand', 'Vietnam',
    # Americas
    'Canada', 'Mexico', 'United States', 'Antigua and Barbuda', 'Aruba',
    'Bahamas', 'Barbados', 'Belize', 'Bonaire', 'British Virgin Islands',
    'Colombia', 'Costa Rica', 'Cuba', 'Curacao', 'Dominican Republic',
    'Guadeloupe', 'Honduras', 'Jamaica', 'Martinique', 'Nicaragua',
    'Panama', 'Puerto Rico', 'St Lucia', 'St Vincent and Grenadines',
    'Venezuela', 'Argentina', 'Brazil', 'Chile', 'Ecuador', 'Peru',
    'Uruguay',
    # Oceania
    'Australia', 'Fiji', 'New Zealand', 'Tokelau',
}

# Countries with bungee jumping (50)
BUNGEE_JUMPING_COUNTRIES = {
    # Africa
    'South Africa', 'Zimbabwe', 'Zambia', 'Kenya', 'Uganda',
    # Asia
    'China', 'China Macau', 'India', 'Thailand', 'Nepal', 'Japan',
    'South Korea', 'Singapore', 'Malaysia', 'Philippines', 'Indonesia',
    'Bhutan',
    # Europe
    'Switzerland', 'France', 'Austria', 'Portugal', 'Romania', 'Italy',
    'Spain', 'Germany', 'United Kingdom', 'Slovenia', 'Croatia', 'Greece',
    'Norway', 'Czechia', 'Netherlands', 'Belgium', 'Denmark', 'Sweden',
    'Russia',
    # Middle East
    'Israel', 'Turkey', 'Lebanon',
    # Americas
    'Canada', 'United States', 'Costa Rica', 'Mexico', 'Colombia',
    'Ecuador', 'Peru', 'Brazil', 'Argentina', 'Chile',
    # Oceania
    'Australia', 'New Zealand',
}

# High tourism infrastructure countries (TTDI > 3.0) - for universal sports
HIGH_TOURISM_COUNTRIES = {
    'United States', 'Spain', 'France', 'Japan', 'Italy', 'Germany',
    'United Kingdom', 'Australia', 'Switzerland', 'Singapore', 'Austria',
    'Netherlands', 'South Korea', 'Canada', 'Portugal', 'Sweden', 'Norway',
    'Finland', 'Denmark', 'Belgium', 'New Zealand', 'Ireland', 'Greece',
    'Czechia', 'Poland', 'Hungary', 'China', 'Turkey', 'Thailand',
    'Malaysia', 'Indonesia', 'Mexico', 'Brazil', 'Argentina', 'Chile',
    'South Africa', 'United Arab Emirates', 'Qatar', 'Saudi Arabia',
    'Israel', 'Morocco', 'Egypt', 'Kenya', 'India', 'Vietnam', 'Taiwan',
    'Croatia', 'Slovenia', 'Estonia', 'Latvia', 'Lithuania', 'Slovakia',
    'Romania', 'Bulgaria', 'Serbia', 'Cyprus', 'Malta', 'Iceland',
    'Luxembourg', 'Costa Rica', 'Panama', 'Dominican Republic', 'Jamaica',
    'Bahamas', 'Barbados', 'Trinidad and Tobago', 'Colombia', 'Peru',
    'Ecuador', 'Uruguay', 'Philippines', 'Sri Lanka', 'Nepal', 'Oman',
    'Jordan', 'Mauritius', 'Seychelles', 'Maldives', 'Fiji',
}


def is_landlocked(country: str) -> bool:
    """Check if a country is landlocked."""
    return country in LANDLOCKED


def get_sport_availability(country: str) -> dict:
    """Determine which sports are available in a given country."""
    landlocked = is_landlocked(country)
    high_tourism = country in HIGH_TOURISM_COUNTRIES

    availability = {}

    # Water Sports - Coastal (only for non-landlocked)
    availability['surfing'] = not landlocked and country in SURFING_COUNTRIES
    availability['kitesurfing'] = not landlocked and country in KITESURFING_COUNTRIES
    availability['windsurfing'] = not landlocked and country in KITESURFING_COUNTRIES  # Same as kitesurfing
    availability['scuba_diving'] = not landlocked and country in SCUBA_DIVING_COUNTRIES
    availability['snorkeling'] = not landlocked and country in SCUBA_DIVING_COUNTRIES
    availability['sup'] = not landlocked and (high_tourism or country in SURFING_COUNTRIES)
    availability['bodyboarding'] = not landlocked and country in SURFING_COUNTRIES
    availability['jet_skiing'] = not landlocked and high_tourism
    availability['wakeboarding'] = high_tourism or country in WHITE_WATER_RAFTING_COUNTRIES
    availability['cliff_diving'] = not landlocked and country in ROCK_CLIMBING_COUNTRIES

    # Snow/Winter Sports
    has_skiing = country in SKIING_COUNTRIES
    availability['skiing'] = has_skiing
    availability['snowboarding'] = has_skiing
    availability['freestyle_skiing'] = has_skiing and high_tourism
    availability['backcountry_skiing'] = has_skiing
    availability['ice_climbing'] = has_skiing and country in ROCK_CLIMBING_COUNTRIES
    availability['snowmobiling'] = has_skiing and high_tourism
    availability['xc_skiing'] = has_skiing
    availability['heli_skiing'] = country in {'Canada', 'United States', 'New Zealand', 'Switzerland',
                                               'Austria', 'France', 'Italy', 'Chile', 'Argentina',
                                               'Japan', 'Russia', 'Norway', 'Sweden', 'Iceland'}

    # Mountain/Terrain Sports
    has_climbing = country in ROCK_CLIMBING_COUNTRIES
    availability['rock_climbing'] = has_climbing
    availability['mountaineering'] = has_climbing and country in SKIING_COUNTRIES
    availability['paragliding'] = country in PARAGLIDING_COUNTRIES
    availability['hang_gliding'] = country in PARAGLIDING_COUNTRIES
    availability['bungee_jumping'] = country in BUNGEE_JUMPING_COUNTRIES
    availability['via_ferrata'] = has_climbing and country in SKIING_COUNTRIES
    availability['canyoning'] = has_climbing and country in WHITE_WATER_RAFTING_COUNTRIES
    availability['ziplining'] = high_tourism or country in {'Costa Rica', 'South Africa', 'New Zealand',
                                                            'Mexico', 'Peru', 'Ecuador', 'Colombia',
                                                            'Thailand', 'Philippines', 'Nepal'}

    # River/Lake Sports
    has_rafting = country in WHITE_WATER_RAFTING_COUNTRIES
    availability['white_water_rafting'] = has_rafting
    availability['kayaking'] = has_rafting or high_tourism
    availability['canoeing'] = has_rafting or high_tourism
    availability['jet_boating'] = country in {'New Zealand', 'United States', 'Canada', 'Australia',
                                               'Switzerland', 'United Kingdom'}
    availability['lake_wakeboarding'] = high_tourism
    availability['water_skiing'] = high_tourism
    availability['tubing'] = has_rafting or high_tourism
    availability['flyboarding'] = high_tourism and not landlocked

    # Universal Land Sports (most available in high tourism countries)
    availability['skateboarding'] = high_tourism
    availability['bmx'] = high_tourism
    availability['mountain_biking'] = high_tourism or has_climbing
    availability['motocross'] = high_tourism
    availability['inline_skating'] = high_tourism
    availability['parkour'] = high_tourism
    availability['trail_running'] = high_tourism or has_climbing
    availability['atv_quad'] = high_tourism
    availability['go_karting'] = high_tourism
    availability['obstacle_racing'] = high_tourism

    # Air Sports
    availability['skydiving'] = country in SKYDIVING_COUNTRIES
    availability['base_jumping'] = country in SKYDIVING_COUNTRIES and has_climbing
    availability['wingsuit'] = country in {'United States', 'Switzerland', 'France', 'Norway',
                                            'Italy', 'Spain', 'China', 'United Arab Emirates',
                                            'New Zealand', 'South Africa'}
    availability['hot_air_ballooning'] = high_tourism
    availability['powered_paragliding'] = country in PARAGLIDING_COUNTRIES
    availability['indoor_skydiving'] = country in {'United States', 'United Kingdom', 'France',
                                                    'Spain', 'Germany', 'Australia', 'China',
                                                    'United Arab Emirates', 'Japan', 'Singapore',
                                                    'Poland', 'Canada', 'Brazil', 'Thailand',
                                                    'Netherlands', 'Austria', 'Switzerland',
                                                    'Belgium', 'Czech Republic', 'Italy'}

    return availability


def main():
    # Load the country data
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    countries_df = pd.read_csv(data_dir / 'joshua_project_countries.csv')

    # Add parent directory to path for imports
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils.country_codes import get_iso_alpha3

    # Build the action sports data
    rows = []
    for _, row in countries_df.iterrows():
        country = str(row['Country'])
        iso_code = get_iso_alpha3(country)

        availability = get_sport_availability(country)

        row_data = {
            'country_name': country,
            'iso_alpha_3': iso_code if iso_code else '',
        }
        row_data.update(availability)
        rows.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Save to CSV
    output_path = data_dir / 'action_sports_by_country.csv'
    df.to_csv(output_path, index=False)
    print(f"Created {output_path}")
    print(f"Total countries: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # Print some stats
    print("\nSport availability counts:")
    for col in df.columns[2:]:  # Skip country_name and iso_alpha_3
        count = df[col].sum()
        print(f"  {col}: {count} countries")


if __name__ == "__main__":
    main()
