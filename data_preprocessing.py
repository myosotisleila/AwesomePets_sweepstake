# -*- coding: utf-8 -*
'''
Store the entries from the sweepstake with one file per entry instead of one per day
in folders using pet id as name to be accessed easily. 

Also updates a summary csv file that we will query later on. 

This script can be run from command-line and is meant to be part of a CRON job (or equivalent)
to make a daily routine after new data comes in. 

@author: vverrecchia
@date; 2022-05-10
@version: 1

usage : 
python data_preprocessing.py --input [input_dir] --output [output_dir] --summary [summary_csv_file]

All arguments are optionals. The defaults should probably not be changed unless you are trying to make a new database

'''

import os
import glob
import json
import pandas as pd

INPUT_DIR = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/sweepstakes_sample"
OUTPUT_DIR = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/sample_preprocessed"
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "summary.csv")

def main(input = INPUT_DIR, output = OUTPUT_DIR, summary = SUMMARY_FILE):
    # TO DO : check that output dir and summary file exists
    # This has more to do with the fact that we want to 
    # append to the existing database, not create a new one
    # and specifying a new file or folder is probably a mistake

    input_json_pattern = os.path.join(input, "entries", "entry-*.json")
    # using iglob to avoid giant lists, since we are only iterating once over it
    # source : glob documentation + https://www.programcreek.com/python/example/4198/glob.iglob 
    for path in glob.iglob(input_json_pattern):
        # since it's an iterator, if the directory is empty
        # the for loop will just stops without executing anything !
        with open(path,'r') as f:
            entries_list = json.load(f)
    
        for entry in entries_list:
            pet_id=entry['pet_id']
            # the json file first
            pet_infos=json.dumps(entry, indent=4)
            pet_dir=os.path.join(output,pet_id)
            os.mkdir(pet_dir)
            with open(os.path.join(pet_dir, pet_id+".json"), 'w') as outfile:
                outfile.write(pet_infos)
            # then the image
            pet_img=os.path.join(input,"imgs","pet-"+pet_id+".jpg")
            pet_out_img=os.path.join(output, pet_id, "pet-"+pet_id+".jpg")
            os.rename(pet_img, pet_out_img)  # we could use os.replace, or shutils or pathlib here

        # to avoid too much I/O operations, we write the summary only once
        # we use pandas for this because the syntax is neat

        df_entries = pd.DataFrame(entries_list)
        df_entries.to_csv(summary, columns=['pet_id','age','breed'], mode='a', header=False, index=False) 
        # do not forget mode = "a"  to append the file and not overwrite it !
        # source : https://www.geeksforgeeks.org/how-to-append-pandas-dataframe-to-existing-csv-file/ 

        # last, we remove the entry file
        os.remove(path)
        
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='reorganise data from sweepstakes')
    parser.add_argument('-i', '--input', action='store',
                        default=INPUT_DIR,
                        help='input directory. Should have an "entries" and "imgs" folders')
    parser.add_argument('-o', '--output', action='store',
                        default=OUTPUT_DIR,
                        help='directory in which to store outputs. should be an existing directory')
    parser.add_argument('-s', '--summary', 
                        default=SUMMARY_FILE,
                        help='summary file to append with basic informations. Should be an existing file ')

    args = vars(parser.parse_args())

    main(**args)