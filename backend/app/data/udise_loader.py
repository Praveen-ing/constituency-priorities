import csv
import logging
from app.db.bigquery_client import get_bq_client

logger = logging.getLogger(__name__)

# Mock CSV structure for UDISE+ School Data
MOCK_UDISE_DATA = """school_id,ward_id,school_name,total_enrollment,student_capacity,teacher_count
sch_101,rajapuram,Rajapuram Govt High School,450,400,12
sch_102,rajapuram,Rajapuram Primary,200,300,8
sch_201,old_city,Old City Boys School,800,600,20
sch_301,new_market,Market Public School,350,500,15
sch_401,green_valley,Valley View High,1200,1000,40
sch_501,riverside,Riverside Primary,150,200,5"""

def load_udise_data():
    """Parses UDISE+ school data and loads it into BigQuery udise_schools table."""
    logger.info("Starting UDISE+ Data load...")
    
    # Parse mock CSV string
    reader = csv.DictReader(MOCK_UDISE_DATA.splitlines())
    rows_to_insert = []
    
    for row in reader:
        bq_row = {
            "school_id": row["school_id"],
            "ward_id": row["ward_id"],
            "school_name": row["school_name"],
            "total_enrollment": int(row["total_enrollment"]),
            "student_capacity": int(row["student_capacity"]),
            "teacher_count": int(row["teacher_count"])
        }
        rows_to_insert.append(bq_row)

    # In production with real keys, we'd insert into BQ
    # client = get_bq_client()
    # table_id = f"{client.project}.constituency_data.udise_schools"
    # errors = client.insert_rows_json(table_id, rows_to_insert)
    # if errors:
    #     logger.error(f"Failed to insert UDISE+ data: {errors}")
    # else:
    #     logger.info(f"Successfully loaded {len(rows_to_insert)} schools into BigQuery.")
        
    logger.info(f"MOCK LOAD: Successfully parsed {len(rows_to_insert)} UDISE+ schools.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_udise_data()
