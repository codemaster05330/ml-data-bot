# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import spacy
import os
from inspect import signature

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pandas as pd

nlp = spacy.load('en_core_web_lg')

def get_num_columns_reply(df):
    return "The {dataset} dataset contains "+get_num_columns(df)+" columns."
def get_num_columns(df):
    return str(df.shape[1])

def get_num_rows_reply(df):
    return "The {dataset} dataset contains "+get_num_rows(df)+" rows."
def get_num_rows(df):
    return str(df.shape[0])

def get_categorical_columns_reply(df):
    cols = get_categorical_columns(df)
    ans = "The {dataset} dataset contains "
    for c in cols:
        ans += (c + ', ')
    ans += "as Categorical columns"
    return ans
def get_categorical_columns(df):
    cols = df.columns
    num_cols = df._get_numeric_data().columns
    cat_cols = list(set(cols) - set(num_cols))
    return cat_cols

def get_numerical_columns_reply(df):
    cols = get_numerical_columns(df)
    ans = "The {dataset} dataset contains "
    for c in cols:
        ans += (c + ', ')
    ans += "as Numerical columns"
    return ans
def get_numerical_columns(df):
    cols = df.columns
    num_cols = df._get_numeric_data().columns
    return num_cols

def check_null_values_reply(df):
    ans = check_null_values(df)
    if ans:
        return "Yes, there are some null values in {dataset} dataset"
    return "No, there is no null value found in {dataset} dataset"
def check_null_values(df):
    return df.isnull().any().any()

def remove_null_values_reply(df, file_path):
    df = remove_null_values(df)
    df.to_csv(file_path, index=False)
    return "The {dataset} dataset file is modified and null values are removed from it."
def remove_null_values(df):
    return df.dropna()

def replace_null_with_mean_reply(df, file_path):
    df = replace_null_with_mean(df)
    df.to_csv(file_path, index=False)
    return "The null values in the {dataset} dataset is replaced with mean of that respective column. You can see the changes in the dataset file."
def replace_null_with_mean(df):
    n_cols = get_numerical_columns(df)
    for col in n_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].mean(), inplace=True)
    return df

def label_encode_categorical_columns_reply(df, file_path):
    df = label_encode_categorical_columns(df)
    df.to_csv(file_path, index=False)
    return "The {dataset} dataset file is modified to Label Encode Categorical columns."
def label_encode_categorical_columns(df):
    c_cols = get_categorical_columns(df)
    for col in c_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    return df

def standardize_numerical_columns_reply(df, file_path):
    df = standardize_numerical_columns(df)
    df.to_csv(file_path, index=False)
    return "The {dataset} dataset file is modified to Standardize Numerical columns."
def standardize_numerical_columns(df):
    n_cols = get_numerical_columns(df)
    scaler = MinMaxScaler()
    df[n_cols] = scaler.fit_transform(df[n_cols])
    return df

def find_data_file_path(text, base_path='datasets/'):
    li = os.listdir(base_path)
    lis = []
    for l in li:
        a = l.split('.csv')[0]
        a = a.replace('_', ' ')
        lis.append(a)
    mapping = []
    for l in lis:
        t1 = nlp(l)
        t2 = nlp(text)
        mapping.append((t1.similarity(t2), l))
    mapping = sorted(mapping, reverse=True)
    file_name = mapping[0][1].replace(' ','_')+'.csv'
    return base_path+file_name

def get_data(file_path):
    df = pd.read_csv(file_path)
    return df

def get_reply_from_context(df, file_path, qtype, dataset):
    function_sim = []
    for fm in function_map:
        t1 = nlp(fm[0])
        t2 = nlp(qtype)
        function_sim.append((t1.similarity(t2), fm[1]))
    function_sim = sorted(function_sim, reverse=True)
    fn = function_sim[0][1]
    sig = signature(fn)
    if len(sig.parameters) == 2:
        reply = fn(df, file_path).replace("{dataset}", dataset)
    else:
        reply = fn(df).replace("{dataset}", dataset)
    return reply

function_map = [
    ('columns', get_num_columns_reply),
    ('rows', get_num_rows_reply),
    ('check null values', check_null_values_reply),
    ('remove null values', remove_null_values_reply),
    ('replace null values with mean', replace_null_with_mean_reply),
    ('categorical columns', get_categorical_columns_reply),
    ('numerical columns', get_numerical_columns_reply),
    ('Label encode categorical columns', label_encode_categorical_columns_reply),
    ('standardize numerical columns', standardize_numerical_columns_reply)
]

class ActionAnswer(Action):

    def name(self) -> Text:
        return "action_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        qtype = tracker.get_slot("question_type")
        dataset = tracker.get_slot("dataset")
        file_path = find_data_file_path(dataset)
        df = get_data(file_path)
        reply = get_reply_from_context(df, file_path, qtype, dataset)
        dispatcher.utter_message(text=reply)

        return [SlotSet("dataset", dataset)]
