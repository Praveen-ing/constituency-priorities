import csv
import logging
from app.db.bigquery_client import get_bq_client

logger = logging.getLogger(__name__)

# Mock CSV structure for Census 2011 Data at Ward Level
# In production, this would read from actual data.gov.in files
MOCK_CENSUS_DATA = """ward_id,ward_name,total_population,households,households_with_water,households_with_toilet,area_sqkm
rajapuram,Rajapuram,45000,10500,8200,9100,4.2
old_city,Old City,85000,16200,12000,13500,5.8
new_market,New Market,32000,8100,7500,7900,3.1
green_valley,Green Valley,54000,14000,13500,13800,8.4
riverside,Riverside,41000,9500,6000,7200,4.0"""

def load_census_data():
    """Parses Census CSV data and loads it into BigQuery census_wards table."""
    logger.info("Starting Census Data load...")
    
    # Parse mock CSV string
    reader = csv.DictReader(MOCK_CENSUS_DATA.splitlines())
    rows_to_insert = []
    
    for row in reader:
        bq_row = {
            "ward_id": row["ward_id"],
            "ward_name": row["ward_name"],
            "total_population": int(row["total_population"]),
            "households": int(row["households"]),
            "households_with_water": int(row["households_with_water"]),
            "households_with_toilet": int(row["households_with_toilet"]),
            "area_sqkm": float(row["area_sqkm"])
        }
        rows_to_insert.append(bq_row)

    # In production with real keys, we'd insert into BQ
    # client = get_bq_client()
    # table_id = f"{client.project}.constituency_data.census_wards"
    # errors = client.insert_rows_json(table_id, rows_to_insert)
    # if errors:
    #     logger.error(f"Failed to insert Census data: {errors}")
    # else:
    #     logger.info(f"Successfully loaded {len(rows_to_insert)} Census wards into BigQuery.")
        
    logger.info(f"MOCK LOAD: Successfully parsed {len(rows_to_insert)} Census wards.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_census_data()
