#!/usr/bin/env python
# coding: utf-8

# In[5]:


#import prerequisite modules
from pymongo import MongoClient
import wget
import zipfile
import pandas as pd
import pymongo
import logging

# Extraction function
def extract_data(filepath):
   
    wget.download(filepath)
    unzipcsvfile = zipfile.ZipFile('./call_logs.zip')
    call_logs = pd.read_csv(unzipcsvfile.open('call_logs.csv'))
    billing_data = pd.read_csv(unzipcsvfile.open('billing_systems.csv'))

      # create common column name
    call_logs = call_logs.rename(columns={"call_date": "date"})
    billing_data = billing_data.rename(columns={"transaction_date": "date"})

        # Merge the two datasets based on date column
    merged_data = pd.merge(call_logs, billing_data, on=['date'])
        # Convert call duration to minutes for easier analysis
    merged_data['duration_minutes'] = merged_data['call_duration'] / 60
    merged_data


    # Use Python logging module to log errors and activities
    logger = logging.getLogger(__name__)
    logger.info("Data transformation completed.")

    return merged_data

# Transformation function
def transform_data(merged_data):
        # Data cleaning and handling missing values( all roww should not have null vaues) so, drop all null
    unique_df = merged_data.dropna()

    #drop the call duration column as it is no longer neccessary
    unique_df2 =unique_df.drop(['call_duration'], axis=1)

        # Group and aggregate the data



    call_times = unique_df2[['caller_number','receiver_number']].groupby('caller_number').aggregate('count')
    call_duration = unique_df2[['caller_number','duration_minutes']].groupby('caller_number').aggregate('sum')

    #group = unique_df2.groupby(['caller_number','date'])
    fraud_df = pd.merge(call_times, call_duration, on=['caller_number'])
    #rename columns for call_number to reflect counts and duration in minuts to reflect sum


    fraud_df.rename(columns = {'receiver_number':'received_numbers(unique_count)', 'duration_minutes':'Total_call_duration_per_day',
                                }, inplace = True)

        # Identify patterns in the data: Fraudsters tend to make many short calls to various enique numbers. Therefore, we can set a threshold
    # of receiver number count to 500 and call duration aggreagre to 300 minutes. Such users will be consinders with suspicion: for the sake of this example we shall set it to 3

    transformed_data = fraud_df[(fraud_df['received_numbers(unique_count)'] >= 3) & (fraud_df['Total_call_duration_per_day'] >= 3)].reset_index()

    transformed_data.reset_index(inplace=True)
    data_dict = transformed_data.to_dict("records")

    # Use data compression techniques to optimize performance
    transformed_data['received_numbers(unique_count)'].astype('int32')

    # Use Python logging module to log errors and activities
    logger = logging.getLogger(__name__)
    logger.info("Data extraction completed.")


    return data_dict

# Loading function
def load_data(data_dict):
        # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017", tlsAllowInvalidCertificates=True)
    db = client["fraud_db"]
    collection = db["fraud"]
    #load data into the fraud collection

    collection.insert_many(data_dict)

    # Use Python logging module to log errors and activities
    logger = logging.getLogger(__name__)
    logger.info("Data loading completed.")
    # Example usage
if __name__ == '__main__':
    
    filepath = 'https://bit.ly/3YRn7z4'
   
    merged_data = extract_data(filepath)
    data_dict = transform_data(merged_data)
    load_data(data_dict)


# In[ ]:




