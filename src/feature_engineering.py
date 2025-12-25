import pandas as pd
import numpy as np

def load_data(path: str) -> pd.DataFrame:
    """Load raw data and rename columns to standard format"""
    df = pd.read_csv(path)
    df.rename(columns={
        'PatientId': 'patient_id',
        'AppointmentID': 'appointment_id',
        'Gender': 'gender',
        'ScheduledDay': 'scheduled_day',
        'AppointmentDay': 'appointment_day',
        'Age': 'age',
        'Neighbourhood': 'neighbourhood',
        'Scholarship': 'scholarship',
        'Hipertension': 'hypertension',
        'Diabetes': 'diabetes',
        'Alcoholism': 'alcoholism',
        'Handcap': 'handicap',
        'SMS_received': 'sms_received',
        'No-show': 'no_show'
    }, inplace=True)
    return df

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning and filtering"""
    # convert datetime cols
    df['scheduled_day'] = pd.to_datetime(df['scheduled_day'])
    df['appointment_day'] = pd.to_datetime(df['appointment_day'])
    
    # cleaning no_show var
    if 'no_show' in df.columns:
        df['no_show'] = df['no_show'].map({'No': 0, 'Yes': 1})
    
    # invalid records - remove
    df = df[(df['age'] >= 0) & (df['age'] <= 120)]
    df = df[df['appointment_day'] >= df['scheduled_day']]
    
    # remove duplicates
    df = df.drop_duplicates(subset=['appointment_id'])
    df = df.sort_values(['scheduled_day', 'appointment_day']).reset_index(drop=True)
    
    return df

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate features for model training/inference"""
    # extracting time-based features
    df['scheduled_date'] = df['scheduled_day'].dt.date
    df['appointment_date'] = df['appointment_day'].dt.date
    
    # hour block (morning/afternoon/evening)
    df['appointment_hour'] = df['appointment_day'].dt.hour
    
    def get_hour_block(hour):
        if hour < 8: return 0  # early morning
        elif hour < 12: return 1  # morning
        elif hour < 16: return 2  # afternoon
        else: return 3  # evening
        
    df['hour_block'] = df['appointment_hour'].apply(get_hour_block)
    df['day_of_week'] = df['appointment_day'].dt.dayofweek
    df['is_holiday_or_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # calc lead time
    df['lead_time_days'] = (df['appointment_day'] - df['scheduled_day']).dt.days
    df['same_day_appointment'] = (df['lead_time_days'] == 0).astype(int)
    df['appointment_month'] = df['appointment_day'].dt.month
    
    return df

def engineer_patient_history(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features based on patient history. 
    Note: In production inference, these would be fetched from a feature store."""
    
    df = df.sort_values(['patient_id', 'appointment_day']).reset_index(drop=True)
    
    # Calculate rolling stats
    df['prev_no_shows'] = df.groupby('patient_id')['no_show'].cumsum() - df['no_show']
    df['prev_appointments'] = df.groupby('patient_id').cumcount()
    
    # Historical rate
    patient_history = df.groupby('patient_id').agg({
        'no_show': ['mean']
    }).reset_index()
    patient_history.columns = ['patient_id', 'historical_no_show_rate']
    
    df = df.merge(patient_history, on='patient_id', how='left')
    
    df['rolling_no_show_rate'] = np.where(
        df['prev_appointments'] > 0,
        df['prev_no_shows'] / df['prev_appointments'],
        df['historical_no_show_rate']
    )
    
    overall_rate = df['no_show'].mean()
    df['rolling_no_show_rate'] = df['rolling_no_show_rate'].fillna(overall_rate)
    
    return df
