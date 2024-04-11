import requests
from datetime import datetime
from pymongo import MongoClient

# Function to check if the paper with the given arXiv ID exists
def is_paper_exists(arxiv_id):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    response = requests.get(url)
    return response.status_code != 404

# Function to use binary search to find the number of papers in a month
def find_paper_count(year, month, lower_bound, upper_bound):
    left = lower_bound
    right = upper_bound
    while left <= right:
        mid = (left + right) // 2
        arxiv_id = f"{year % 100:02}{month:02}.{mid:0{5 if year > 2015 or (year == 2015 and month > 1) else 4}}"
        if is_paper_exists(arxiv_id):
            left = mid + 1
        else:
            right = mid - 1
    return right

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.arxiv
collection = db.papers_per_month

# Loop over each month and store the results in MongoDB
for year in range(2008, 2025):
    for month in range(1, 13):
        if year == 2024 and month > 4:
            break
        lower_bound = 1
        upper_bound = 9999 if year < 2015 or (year == 2015 and month == 1) else 99999
        count = find_paper_count(year, month, lower_bound, upper_bound)
        print(f"Number of papers uploaded in {year}-{month:02}: {count}")

        # Store the data in MongoDB
        document = {
            "year": year,
            "month": month,
            "papers_uploaded": count
        }
        collection.insert_one(document)

        # Optional: Add a delay to avoid overloading the server
        # time.sleep(1)

print("Data has been stored to MongoDB.")