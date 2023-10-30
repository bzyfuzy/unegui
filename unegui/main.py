from datetime import datetime
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from store import store_ads
# from dotenv import load_dotenv
# load_dotenv()

def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("cron_car")
    process.crawl("cron_apartment")

    process.start()
    store_ads()

def crawl_normals():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("car")
    process.crawl("apartment")
    process.start()
    
    store_ads()

def make_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

def prepare_folders():
    csv_path = os.getenv('CSVS_PATH')
    json_path = os.environ.get('JSONS_PATH')
    make_dir(csv_path)
    make_dir(json_path)
    make_dir(os.path.join(csv_path, "apartments"))
    make_dir(os.path.join(json_path, "apartments"))
    make_dir(os.path.join(csv_path, "cars"))
    make_dir(os.path.join(json_path, "cars"))
    

if __name__ == "__main__":
    print("job_started:", datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    prepare_folders()
    main()
    print("job_ended:", datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))