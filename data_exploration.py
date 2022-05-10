'''
This file contains some notebook-style code used for data exploration.
@author: vverrecchia
@date: 2022-05-10
@version: 1

# usage
this code is intended to be run like a notebook, 
cell by cell in an interactive python terminal.

most of the code comes from documentation of the librairies, and from the two tutorials : 
https://datascienceparichay.com/article/pandas-get-all-unique-values-in-a-column/
https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/ 
'''

# %% imports
import os # not using Pathlib to keep dependencies simple
import glob
import json
import pandas as pd

# %% paths

entries = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/sweepstakes_sample/entries"
images = "/homes_unix/verrecchia/workspace/sweepstakes_challenge/sweepstakes_sample/imgs"

# I could make things smarter by using iglob but this won't be 
# an issue for the sample dataset I'm using right now
list_entries = glob.glob(entries+"/entry-*.json")
list_img = glob.glob(images+"/pet-*.jpg")

# %% creating a pandas dataframe

# reading one entry file gives a list of dicts 
# because they are several entries per file

# I am doing this data exploration on a 40-CPU, 256G-of-RAM machine, 
# so I am not concerned about memory issues at this step yet

all_entries_list=[]
for file in list_entries :
    with open(file,'r') as f:
        all_entries_list.extend(json.load(f))

# using extend because we are appending a list of entries each time

print(len(all_entries_list))
# result is 4391, the same lenght than list_img, this is a good sign
# %%
df_entries=pd.DataFrame(all_entries_list)
# %% actual data exploration

# Are all pet ids unique ?
print(len(df_entries)) # 4391
print(df_entries['pet_id'].nunique()) # 4391

# all pet ids are unique. There is no need to use it as index, but we could.

# %%
# Do all pet ids correspond to one (and only) image ?

for pet_id in df_entries['pet_id'].unique():
    corresp_image = glob.glob(os.path.join(images, "*"+pet_id+"*.jpg"))
    # easier to check the case we don't want !
    if len(corresp_image)==0:
        print(pet_id + " don't have any match")
    elif len(corresp_image)> 1:
        print(pet_id+ " have more than 1 match")
# this runs in around 20 seconds and returns nothing
# we have 1 and only 1 image per entry !

# %%
# create a new column with the corresponding image
df_entries["picture_path"]=images+"/pet-"+df_entries["pet_id"]+".jpg"

# quick sanity check just to be sure we only put existing regular files !
for path in df_entries["picture_path"].tolist():
    if not os.path.isfile(path):
        print(path + " is not a valid file")

# %%
# what are the different pet types ?
print(df_entries['pet_type'].unique())
# only dogs and cats

# %%
# what are the different breeds and how many times ?
breeds = df_entries["breed"].value_counts()
print(breeds)

# there are 122 different breeds, the most common being "nan" 
# which is not a surprise

# %%
# what are the possible ages ?
ages = df_entries["age"].value_counts()
print(ages)
# there are 82 different ages
# age is an integer between 0 and 238
# no negative numbers or floating values
# the maximum of 238 (almost 20 years) seems reasonable
# considering cats and dogs lifespan

sum(ages) # result is 4391
# sum(ages) is the sum of the counts, not of the ages themselves
# this means all the entries have an age value

# %%
# last remark :
# there are as many images in list_img than we have entries
# and each entries correspond to one  (and only one) image
# this means that the opposite is true : 
# all images have a corresponding entry, no "orphan"

# %% writing a summary for futur use
df_entries.to_csv("/homes_unix/verrecchia/workspace/sweepstakes_challenge/sweepstakes_sample/summary.csv", columns=['pet_id','age','breed'], header = True, index = False )
# %%
