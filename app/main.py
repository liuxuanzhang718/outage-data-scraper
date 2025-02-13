import json
import time
import os

from scrapers import Scraper
from scrapers.util import save, timenow

def handler(event, context=""):
    layout_id = event['layout']
    EMCs = event['emc']
    bucket = event['bucket']
    state = event['folder']
    success_cnt = 0

    for emc, url in EMCs.items():
        try:
            sc = Scraper(state, layout_id, url, emc)
            data = sc.parse()
            for key, df in data.items():
                if df.empty:
                    print(f"no {key} outages for {emc} as of {timenow()}")
                else:
                    path = f"{state}/layout_{layout_id}/{key}_{emc}.csv"
                    save(df, bucket, path)
            success_cnt += 1
        except Exception as e:
            print(e)
            continue

    print(f'Successfully scraped {success_cnt} out of {len(EMCs)} EMC outages')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully scraped {success_cnt} out of {len(EMCs)} EMC outages')
    }


if __name__ == "__main__":
    start = time.time()

    # handler test here
    event_path = os.path.join(os.getcwd(), "../events/ca/investor.json")
    with open(event_path) as f:
        test_event = json.loads(f.read())
    handler(test_event)

    # single test here
    # sc = Scraper(state='tx',
    #              layout_id=11,
    #              url="https://ebill.karnesec.org/maps/ExternalOutageMap/",
    #              emc="dev")
    # print(sc.parse())

    end = time.time()
    print(end - start)