# AwesomePets_sweepstake

@author: vverrecchia
@date: 2022-05-10
@version: 1

## take-home challenge for TWEAG Violaine Verrecchia

The context for this challenge can be found in the file challenge.md  
All explainations about the rationale of the code, choices of architecture, and known limitations are in the DESIGN.md file.  

## installation
Currently there is no container file for the code. 
The code needs to run in python >= 3.6 (I used 3.10.4)
It uses standard librairies, and pandas 1.4.2 (any recent one should work)

## inputs and outputs
the input data should be in a directory (base) with the same organization than the one provided for the challenge : 
- one folder for the entries (one json file per day)
- one folder for the images (named "imgs") containing .jpg images

It also need some input json file for the query. 
A model can be found in test_queries/model.json

The output for preprocessing is reorganized data in a new folder(data) : 
- one summary.csv file containing only pet_id, age and breed
- one folder per entry, named with the pet_id
- one json file and one jpg picture in each folder with the corresponding pet_id

## usage  
data_exploration.py is meant to be run like a notebook, in an interactive python terminal. 

data_preprocessing.py : 
python data_preprocessing.py --input [input_dir] --output [output_dir] --summary [summary_csv_file]

python query.py --data [data_dir] --query [input_json] --summary [summary_csv_file] --output [output_csv_file]


