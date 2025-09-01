import psycopg2
import pandas as pd
from config import DATABASE_URL

def connect_to_database():
    """Establish connection to the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Successfully connected to the database!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_all_data():
    """Fetch all required data from the database"""
    try:
        conn = connect_to_database()
        if not conn:
            return None, None, None, None, None, None
        
        # Fetch data from all tables
        print("Fetching settlement case data...")
        settlement_query = "SELECT * FROM SettlementCase"
        df = pd.read_sql(settlement_query, conn)
        print("Settlement case data fetched successfully!")
        
        print("Fetching jamati member data...")
        jamati_member_query = "SELECT * FROM JamatiMember"
        jamati_member_df = pd.read_sql(jamati_member_query, conn)
        print("Jamati member data fetched successfully!")
        
        print("Fetching education data...")
        education_query = "SELECT * FROM Education"
        education_df = pd.read_sql(education_query, conn)
        print("Education data fetched successfully!")
        
        print("Fetching finance data...")
        finance_query = "SELECT * FROM Finance"
        finance_df = pd.read_sql(finance_query, conn)
        print("Finance data fetched successfully!")
        
        print("Fetching physical and mental health data...")
        physical_mental_health_query = "SELECT * FROM PhysicalMentalHealth"
        physical_mental_health_df = pd.read_sql(physical_mental_health_query, conn)
        print("Physical and mental health data fetched successfully!")
        
        print("Fetching social inclusion agency data...")
        social_inclusion_agency_query = "SELECT * FROM SocialInclusionAgency"
        social_inclusion_agency_df = pd.read_sql(social_inclusion_agency_query, conn)
        print("Social inclusion agency data fetched successfully!")
        
        # Close the connection
        conn.close()
        
        return df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None, None, None, None

def get_case_data_by_id(case_id):
    """Fetch specific case data by case ID"""
    try:
        conn = connect_to_database()
        if not conn:
            return None
        
        query = f"SELECT * FROM SettlementCase WHERE caseid = {case_id}"
        case_data = pd.read_sql(query, conn)
        conn.close()
        
        return case_data.iloc[0] if not case_data.empty else None
        
    except Exception as e:
        print(f"Error fetching case data: {e}")
        return None

def get_custom_data_by_case_id(case_id):
    """Fetch custom data for a specific case ID"""
    try:
        conn = connect_to_database()
        if not conn:
            return None
        
        query = "SELECT * FROM custom_data WHERE case_id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (case_id,))
        result = cursor.fetchone()
        
        if result:
            # Convert to dictionary
            columns = ['case_id', 'family_progress_status', 'languages_spoken', 'arrival_date']
            custom_data = dict(zip(columns, result))
            cursor.close()
            conn.close()
            return custom_data
        else:
            cursor.close()
            conn.close()
            return None
        
    except Exception as e:
        print(f"Error fetching custom data: {e}")
        return None

def save_custom_data(case_id, family_progress_status, languages_spoken, arrival_date):
    """Save or update custom data for a case"""
    try:
        conn = connect_to_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if record exists
        check_query = "SELECT case_id FROM custom_data WHERE case_id = %s"
        cursor.execute(check_query, (case_id,))
        exists = cursor.fetchone() is not None
        
        if exists:
            # Update existing record
            update_query = """
                UPDATE custom_data 
                SET family_progress_status = %s, languages_spoken = %s, arrival_date = %s
                WHERE case_id = %s
            """
            cursor.execute(update_query, (family_progress_status, languages_spoken, arrival_date, case_id))
        else:
            # Insert new record
            insert_query = """
                INSERT INTO custom_data (case_id, family_progress_status, languages_spoken, arrival_date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (case_id, family_progress_status, languages_spoken, arrival_date))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving custom data: {e}")
        return False

def delete_custom_data(case_id):
    """Delete custom data for a specific case ID"""
    try:
        conn = connect_to_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        delete_query = "DELETE FROM custom_data WHERE case_id = %s"
        cursor.execute(delete_query, (case_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return rows_affected > 0
        
    except Exception as e:
        print(f"Error deleting custom data: {e}")
        return False