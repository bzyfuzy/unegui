import os
import re
import csv
import json
import pymongo
from pymongo import MongoClient, errors
from dateutil import tz
from datetime import datetime, timedelta
csv_path = os.environ.get('CSVS_PATH')
json_path = os.environ.get('JSONS_PATH')

db_uri = os.environ.get('DB_URI')
db_name = os.environ.get('DB_NAME')


def store_appartment(path):
    pattern = r"/adv/(\d+)_[^/]+/"
    with open(path, encoding='utf-8') as json_file:
        client = MongoClient(db_uri)
        db = client[db_name]
        appartments = json.load(json_file)
        
        documents = []
        for appartment in appartments:
            type = appartment.get("category", 0)
            oroo = type + " өрөө"
            if(type == 5):
                oroo = "5 өрөө"
            match = re.search(pattern, appartment["link"])
            id = ""
            if match:
                id = match.group(1)
            if "Өчигдөр" in appartment["post_date"]:
                yesterday = datetime.now() - timedelta(days = 1)
                posted_date = datetime.strptime(appartment["post_date"].replace("Өчигдөр",yesterday.strftime("%Y-%m-%d")), '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
            elif "Өнөөдөр" in appartment["post_date"]:
                posted_date = datetime.strptime(appartment["post_date"].replace("Өнөөдөр",datetime.now().strftime("%Y-%m-%d")), '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
            else:
                posted_date = datetime.strptime(appartment["post_date"], '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
               

            document = {
                "ad_id": str(id),
                "garchig": appartment["title"],
                "link": appartment["link"],
                "hayag": appartment["address"],
                "tailbar": appartment["detail"],
                "detail": {
                    "oroo": oroo,
                    "heden_davhart": appartment["davhart"],
                    "barilgiin_davhar": appartment["b_davhar"],
                    "talbai": appartment["talbai"],
                    "ashiglaltand_orson_on": appartment["ashiglaltand"],
                    "une": appartment["price"],
                    "date": posted_date,
                    "images": appartment["imgs"].split(", ")
                },
                "created_at": datetime.utcnow()
            }
            documents.append(document)
        db["bair"].create_index([("ad_id", pymongo.ASCENDING)],
                           unique=True)
        # try:
        #     db["bair"].insert_many(documents)
        # except Exception as e:
        #     print(e)

        try:
            result = db["bair"].insert_many(documents)
            # print("Inserted count:", len(result.inserted_ids))
        except errors.BulkWriteError as bwe:
        # Handle the bulk write error
            for err in bwe.details['writeErrors']:
                if err['code'] == 11000:  # MongoDB code for duplicate key error
                    pass
                    # print(f"Duplicate key error for document with _id: {err['op']['_id']}")
        except Exception as e:
            # pass
            print("Error:", e)
            
   
def store_car(path):
    pattern = r"/adv/(\d+)_[^/]+/"
    year_pattern = r"(\d{4})/(\d{4})"
    

    with open(path, encoding='utf-8') as json_file:
        client = MongoClient(db_uri)
        db = client[db_name]
        cars:list[dict] = json.load(json_file)
        documents = []
        for car in cars:
            match = re.search(pattern, car["link"])
            id = ""
            details = {
                "manufactured": 0,
                "imported": 0,
                "text": car.get("detail", ""),
                "mileage": car.get("millage", ""),
                "transmission": car.get("transmission", ""),
                "engine": {
                    "size": car.get("engine_size", ""),
                    "type": car.get("engine_type", "")
                },
                "color": car.get("color", ""),
                "drivetrain": car.get("wheel", "")
            }
            year_match = re.search(year_pattern, car["title"])
            if year_match:
                details["manufactured"] = int(year_match.group(1))
                details["imported"] = int(year_match.group(2))

            if match:
                id = match.group(1)
            
            if "Өчигдөр" in car["post_date"]:
                yesterday = datetime.now() - timedelta(days = 1)
                posted_date = datetime.strptime(car["post_date"].replace("Өчигдөр",yesterday.strftime("%Y-%m-%d")), '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
            elif "Өнөөдөр" in car["post_date"]:
                posted_date = datetime.strptime(car["post_date"].replace("Өнөөдөр",datetime.now().strftime("%Y-%m-%d")), '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
            else:
                posted_date = datetime.strptime(car["post_date"], '%Y-%m-%d %H:%M').replace(tzinfo=tz.gettz('Asia/Ulaanbaatar'))
                
            document = {
                "ad_id": str(id),
                "category": car["category"],
                "title": car["title"],
                "link": car["link"],
                "price": car["price"],
                "post_date": posted_date,
                "images": car["imgs"].split(", "),
                "details": details,
                "created_at": datetime.utcnow()
            }
            documents.append(document)
        db["cars"].create_index([("ad_id", pymongo.ASCENDING)],
                           unique=True)
        # try:
        #     db["cars"].insert_many(documents)
        # except Exception as e:
        #     error+=1
        #     print(error)
        try:
            result = db["cars"].insert_many(documents)
            # print("Inserted count:", len(result.inserted_ids))
        except errors.BulkWriteError as bwe:
        # Handle the bulk write error
            for err in bwe.details['writeErrors']:
                if err['code'] == 11000:  # MongoDB code for duplicate key error
                    pass
                    # print(f"Duplicate key error for document with _id: {err['op']['_id']}")
        except Exception as e:
            # pass
            print("Error:", e)

def make_json(csvFilePath, jsonFilePath):
    data = []
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            data.append(rows)

    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        json.dump(data, jsonf, ensure_ascii=False)

def convert_csvs():

    apartments_directory = os.path.join(csv_path, "apartments")
    apartments_results = os.path.join(json_path, "apartments")
    for filename in os.listdir(apartments_directory):
        f = os.path.join(apartments_directory, filename)
        if os.path.isfile(f) and ".csv" in filename:
            make_json(f, os.path.join(apartments_results, filename.split(".")[0]+".json"))

    cars_directory = os.path.join(csv_path, "cars")
    cars_results = os.path.join(json_path, "cars")      

    for filename in os.listdir(cars_directory):
        f = os.path.join(cars_directory, filename)
        if os.path.isfile(f) and ".csv" in filename:
            make_json(f, os.path.join(cars_results, filename.split(".")[0]+".json"))

def store_jsons():
    cars_dir = os.path.join(json_path, "cars")
    for filename in os.listdir(cars_dir):
        f = os.path.join(cars_dir, filename)
        if os.path.isfile(f) and ".json" in filename:
            store_car(f)

    appartment_dir = os.path.join(json_path, "apartments")
    for filename in os.listdir(appartment_dir):
        f = os.path.join(appartment_dir, filename)
        if os.path.isfile(f) and ".json" in filename:
            store_appartment(f)


def store_ads():
    convert_csvs()
    store_jsons()