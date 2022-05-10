# -*- coding: utf-8 -*
'''
Query the data based on an age range and a breed, using an input json file. 


@author: vverrecchia
@date; 2022-05-10
@version: 1

usage : 
python query.py --data [data_dir] --query [input_json] --summary [summary_csv_file] --output [output_csv_file]

Important Note : Since this code is using f-strings, Python >=3.6 is needed !
'''

# %% imports
import os
import glob
import json
import pandas as pd

# %% paths
DATA_DIR = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/sample_preprocessed"
INPUT_JSON = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/git/AwesomePets_sweepstake/test_queries/unsorted_age.json"
SUMMARY_FILE = os.path.join(DATA_DIR, "summary.csv")
OUTPUT = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/unsorted_age.csv"

# The kind of variables we would need to scale up when the summary file doesn't fit in memory
# CHUNK SIZE = 1 000 000
# N_CORES = 4
# %% function definitions

def check_age(low=0, up=999):
    # we assume that values will be integers >=0 as said in DESIGN
    if low>=up :
        return up, low
    else :
        return low, up
    # in case both values are equal, no problem since we use inclusive between 

def check_breed(in_list=[""], possible_breeds_list=[""]):
    if in_list==[""]: 
        print("Breed list was empty, returning 0 results")
        return "none"
    elif in_list==["*"]:
        print("Breed was set to *. Returning all breeds.")
        return "all"
    elif in_list==["nan"]:
        return "nan"
    else : 
        final_breed_list=[]
        for breed in in_list:
            if breed in possible_breeds_list:
                final_breed_list.append(breed)
            else :
                # this includes the case were "nan" or "" or "*" are in 
                # a list of several breeds
                print(f"Breed {breed} is not in the list of breeds. Results won't include this breed.")
            
        if final_breed_list==[]:
            print("There was no existing breed in the breed list. Returning 0 results")
            return "none"
        else :
            return final_breed_list

def read_input_file(input_json=INPUT_JSON):
    with open(input_json, 'r') as f:
       query_filters = json.load(f)
    
    breed_list = query_filters['breed']
    up_age = query_filters['age_range']['up']
    low_age = query_filters['age_range']['low']

    # we check for the age stuff directly when we read
    low, up = check_age(low_age, up_age)
    return breed_list, low, up

def fetch_entry_and_add_image_path(pet_id, data):
    with open(os.path.join(data,pet_id,f"{pet_id}.json"),'r') as entry_json:
        dict_entry=json.load(entry_json)
    
    dict_entry["img_path"]= str(os.path.join(data, pet_id, f"pet-{pet_id}.jpg"))
    # we must pass a list of dict to create this dataframe
    return pd.DataFrame([dict_entry])

# %% main
def main(data = DATA_DIR, query = INPUT_JSON, summary = SUMMARY_FILE, output = OUTPUT):
    # read the input file
    breed_list, low, up = read_input_file(query)
    # read the summary file
    df_summary = pd.read_csv(SUMMARY_FILE, header=None, names=["pet_id","age","breed"])
    breed_names=df_summary["breed"].unique()
    # actual query
    breed_filter=check_breed(in_list=breed_list, possible_breeds_list=breed_names)

    if breed_filter!="none": # if it's none we're already done
        # first filter on the age
        age_filtered=df_summary[df_summary["age"].between(left=low, right=up, inclusive = 'both')]    
        if age_filtered.empty:
            print("your query was valid but returned 0 results")
        else :         
            if breed_filter=="all":
            # only filter on the age so we're done
                for pet in age_filtered['pet_id']:
                    one_entry=fetch_entry_and_add_image_path(pet, data)
                    one_entry.to_csv(output, mode='a', header=False, index=False)
                print(f"query returned {len(age_filtered)} results, written in {output}")

            elif breed_filter=="nan": 
                # use df["breed"].isnull() to check for nan results
                breed_filtered=age_filtered[age_filtered["breed"].isnull()]
                for pet in breed_filtered['pet_id']:
                    one_entry=fetch_entry_and_add_image_path(pet, data)
                    one_entry.to_csv(output, mode='a', header=False, index=False)
                print(f"query returned {len(breed_filtered)} results, written in {output}")
            else : 
                # df["breed"].isin(breed_filter)
                breed_filtered=age_filtered[age_filtered["breed"].isin(breed_filter)]
                for pet in breed_filtered['pet_id']:
                    one_entry=fetch_entry_and_add_image_path(pet, data)
                    one_entry.to_csv(output, mode='a', header=False, index=False)
                print(f"query returned {len(breed_filtered)} results, written in {output}")
# %%
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='reorganise data from sweepstakes')
    parser.add_argument('-q', '--query', action='store',
                        default=INPUT_JSON,
                        help='input json file with the query')
    parser.add_argument('-d', '--data', action='store',
                        default=DATA_DIR,
                        help='directory in which to store outputs. should be an existing directory')
    parser.add_argument('-s', '--summary', 
                        default=SUMMARY_FILE,
                        help='summary file to append with basic informations. Should be an existing file ')
    parser.add_argument('-o', '--output', action='store',
                        default=OUTPUT,
                        help='output csv file with the result of the query, if the query returned anything')
    
    args = vars(parser.parse_args())

    main(**args)

# %%
