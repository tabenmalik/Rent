import argparse
import contextlib
import csv
import datetime as dt
import sys

import requests
import bs4


def create_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output')

    # TODO: mutually exclusive
    parser.add_argument('-a', '--append')

    return parser


def get_floorplans():
    today = dt.date.today().strftime('%Y-%m-%d')

    response = requests.get('https://www.ellaparkside.com/floorplans')
    if response.status_code != 200:
        return None

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    floor_plans = []

    for fp in soup.select('.fp-container'):
        num = fp.attrs['id'][-1]
        fp_name = fp.find('h2', {'data-selenium-id': f'Floorplan{num}Name'})

        # One of the fp-containers has nothing to do with the list
        # of floor plans
        if not fp_name:
            continue

        fp_name = fp_name.contents[0].strip()

        fp_availability = fp.find('span', {'data-selenium-id': f'Floorplan{num}Availability'})
        fp_availability = fp_availability.contents[0].strip()
            
        fp_beds = fp.find('span', {'data-selenium-id': f'Floorplan{num}Beds'})
        fp_beds = fp_beds.contents[0].strip()
        
        fp_baths = fp.find('span', {'data-selenium-id': f'Floorplan{num}Baths'})
        fp_baths = fp_baths.contents[0].strip()
        
        fp_sqft_span = fp.find('span', {'data-selenium-id': f'Floorplan{num}SqFt'})
        fp_sqft = fp_sqft_span.contents[0].strip()
        if len(fp_sqft_span.contents) > 1:
            fp_sqft += fp_sqft_span.contents[-1].strip()
            
        fp_rent_span = fp.find('span', {'data-selenium-id': f'Floorplan{num}Rent'})
        fp_rent = fp_rent_span.contents[0].strip()
        if len(fp_rent_span.contents) > 2:
            fp_rent += fp_rent_span.contents[-2].strip()
            
        floor_plans.append({
            'Date': today,
            'Name': fp_name, 
            'Availability': fp_availability, 
            'Beds': fp_beds, 
            'Baths': fp_baths, 
            'Sqft': fp_sqft, 
            'Rent': fp_rent
        })

    return floor_plans


def outstream(fn=None, /, *args, **kwargs):
    """
    A nifty trick, slightly modified, from https://stackoverflow.com/a/75196027
    """
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout

    return open(fn, *args, **kwargs) if fn or fn == '-' else stdout()


def main(argv=None):
    parser = create_arg_parser()
    args = parser.parse_args(argv)

    floor_plans = get_floorplans()
    
    if not floor_plans:
        sys.stderr("Couldn't get floor plans...")
        sys.exit(1)
    
    mode = 'a' if args.append else 'w'

    with outstream(args.output, mode=mode, newline='') as rent_csv:
        csvwriter = csv.DictWriter(rent_csv, fieldnames=floor_plans[0].keys())
        csvwriter.writerows(floor_plans)


if __name__ == '__main__':
    sys.exit(main())
