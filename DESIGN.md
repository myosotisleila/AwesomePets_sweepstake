# Design

## Context and Objectives

The context is a sweepstakes on pets : owners register their pets (basic informations + picture) for a chance to win gears.  

The data is currently separated in two folders : one with the informations (json files) and one with the images (jpeg files). There are several entries in each file.  

The objective is :

1. To store this data in a meaningful way
2. To be able to query this data with age and breed information

The user won't be adding, deleting or modifying the database, only consulting it.
However, new data continues to come in during the queries.  

More details about the context, tasks and specifications can be found in the challenge.md file.

### Functional Needs

- The script must run from command-line
- The query information will be a separate json file
- There can be one or more breeds specified
- The age will (always) be a range  
- There will always be both breed and age in the input  
- The output will return all entries that satisfy the filtering criterias, and the paths to the pictures

### Main constrains

- the full dataset is over 100s of Tb : cannot fit in memory
- the query should be time-efficient
- the solution should scale in time and space complexity as the dataset continues to grow
- cannot use existing databases or query engines
- new entries will continue to come in the database (database is not frozen)
  
### Results priorities

In order of priority, I want to :

1. Give all the results in the database that satisfies the query and existed before the query  
2. Deal with the fact that new entries can come in  
3. Deal with the scale of the full dataset  
4. Take care of the edge cases in the query (ex : empty breed list)  
5. Give an efficient solution in terms of time  
6. Give an efficient solution in terms of space  
7. Deal with the fact that entries could be removed or modified during query*

\* from and RGPD point of view, people should be able to modify or remove their data at any point in time

For now, we will consider that the data is present locally and won't deal with the fact that the dataset is, in fact, hosted on Amazon S3.

## Data exploration

The sample data contains 1000 "entries" file (json file, one file per day considering the naming of the file)

Each json file contains several entries (usually 4-5 new entries per day).  
The entries all have the same structure, with the following fields :

```json
"pet_id" <-- this will be in the name of the corresponding picture
"pet_type"
"name"
"age" <-- an integer number, in months
"breed" <-- this can be 'nan'
"color"
"fur_length"
"vaccinated"
"gender"
"entry_date"
"story"
"owner_location_id"
"owner_account_id"
```  

In our case, we are interested only in the "pet_id", "age" and "breed" fields.  

After some data exploration (that you can see in data_exploration.py), we can  say the following : 
- each pet id_is unique
- pets (in "pet_type") are only cats and dogs
- the age (in month) is always an integer, minimum is 0
- the maximum age in the sample dataset is 238 (around 20 years) which is reasonable for cats and dogs. We can assume the age will never be over 999 months, unless we suddenly start having pet turtles.
- all entries have the "age" filled, no NaN
- the breed is either 'nan' or a breed name
They are many breeds (122 in the sample, more to expect in the full dataset), with extremely unbalanced numbers (around 25% of the entries are for "domestic short hair" and most breeds only have 1 or 2 entries)
- each pet_id correspond to one and only one (regular) file in the image folder, named like pet-\[pet_id\].jpg 
- there are no images without corresponding json file

We will consider that the sample is representative of the full dataset (i.e.  the affirmations above are valid for the full dataset)

## Edge cases to test
Considering the data exploration and the task's description, there are a few
edge cases to test: 

- empty breed list : []
- breed list is ["nan"] 
- breed list contains values that are not in the database
- age is a range with twice the same value (i.e. 0-0 or 12-12)
- the numbers in the age range are not sorted (i.e. 15-4)

There are also things to test that are common use-case (not really edge-cases):
- the query runs while new files are coming or being processed in the database
- breed list contains only one breed (i.e. ["domestic short hair"])
- breed list contains several breeds (i.e ["scottish terrier", "labrador"])
- age range is a sorted age range (i.e. 4-15)

## Data preprocessing

### Current state

The data comes in two folders, one for the images, one for the json files.
One json file contains several entries for the same day, and has quite a lot of informations we don't use in the query.

### Rationale

We would like to make things easier by :
- having one summary file with only the needed infos (pet_id, age, breed) to be able to fit in memory and to query fast. We don't need sophisticated relational tables or joint, since we know which queries we will have in advance
- having one folder per entry, containing the json and the image, instead of all images in one place and all json on the other
- using the pet_id for the folder name and the json file (it's already in the image file) to fetch the data easily 

### Updating the database

Considering the current state of the data, with one entry file per day, it looks like the database is updated once a day at midnight (all entry dates are at 00:00:00). The files would come in the original "entries" and "imgs" folders. 

We need a script able to take new data from the day, format it in the way we want, and update the "summary" file accordingly (in this order). 
Updating the summary file last avoid the problem of querying data that doesn't exist yet. However, there are still many things that can go wrong during the updating part. This will be discussed in more details in the "Limitations" section. 

### Getting an idea of the size of the full dataset
> "You talk about a summary file, but Violaine, would it fit?"

The sample we have is 127,5 Mo :
3,4 Mo from the json files, and 124,1 for the images.
However, the summary only takes 107,9 ko.

If the total dataset is 500 To for example, 
the total from the json file would be around 13,3 To
The summary file would use around 420 Go 

This is still too much to fit in memory at once, but is more manageable. 
Especially since csv files can be read in chunks easily in pandas, using
"skiprows" and "nrows" arguments. 

Once we have separate chunks, it also becomes easy to parallel, since we are only consulting data, not modifying it. 

**TL;DR : no, it won't fit, but it makes fix easier for future improvements**

### The preprocessing itself
The preprocessing itself is in the file data_preprocessing.py

The concept is to read (one by one) the entries file, 
create several small json files (one per pet_id)
create one folder for each pet_id
store in this folder the corresponding small json file
move the corresponding picture in the folder

and finally update a csv summary file (already existing) with the new entries of this file. 

For moving the picture, we chose os.rename() instead of other options like shutils.move() or Pathlib because it is faster, and more atomic (it does not copy-then-delete the file, unlike shutils).

source : https://www.learndatasci.com/solutions/python-move-file/ 

I chose to update the summary file only once per entry file (instead of once per pet) as a trade-of between robustness and speed: 
On the bad side, if the scripts fails in the middle of an entry file, some files will already have been treated but the summary file won't have been updated. 
On the plus side, we open/write/close the summary file only once per entry file, so we avoid a lot of I/O operations. 

The preprocessing has been run once for all the sampling data. 
It can easily become part of a CRON job to run daily, after the update of the database, as long as the new files keep coming in the same directories "entries" and "imgs". 

### Testing for the preprocessing 
There is currently no testing (or even basic assertions) in the code for the data preprocessing. 
Things that I would like to implement : 
- test what happens when we run into access rights problems
(especially writing problems when trying to move or delete files)
- test what happens when there is no new data one day and the directories are empty (by design, it should not be a problem, but a test would be nice)
- test what happens when we try to append to the csv file once it became huge
(normally, nothing because we should not load the whole file in memory)
- test what happens if we are running into a duplicate (entry with an existing id that already has a folder with this name, and possibly some files inside)

About the timing of the preprocessing, for the sample, it took a few seconds. 
This would likely take hours or days for the first "big" preprocessing (and then a lot less every day, depending on how much now data comes every day)

This lead to the following very important tests : 
- test what happens when new data is coming right when we run the preprocessing script (if the preprocessing takes more than 24 hours, this WILL happen)
- test what happens when we query the database while the preprocessing script is running (if we want to start querying quickly, even though the first big preprocessing is not over yet), especially what happens when we append the summary file while we are still reading it for the query.

## Querying the data
Mostly, we want to query that summary.csv file we created just before, load it as a pandas dataframe, and filter it to get all the pet_ids that we want.  

In this case, the csv file acts like a very minimal SQL database with only one table, but we don't need more. 
Then we will fetch the entries for these pet_ids and put them in the result file.

### Input
For the query, we will use a very simple json file to store breed, upper and lower age range. 

We assume that the range bounds are **both included** in the results, i.e. if we ask for age range 1-4 months, we will get pets of 1,2,3 and 4 months old. 

### Output
The output will be a big csv file file with all entries satisfying the query, with an extra column "img_path" for the path to the corresponding picture. 

The reason why we give a csv as output, and not a json, is because it's easy to append to a csv file in python without opening the whole file, something that, as far as I know, is not possible with json. 

Considering we may have filtrates that are bigger than the RAM of the computer (especially if we query something like "domestic short hair" that represents almost 25% of all breed), writing csv file will be easier to scale to the full dataset by querying and writing in chunks. 

### Assumptions
Considering the time constrains, I will leave all the chunking and parallel processing for further improvements, and code as if the summary file and the filtrates fits in memory. 

I will also consider that the input json file with the query will be properly formatted, always contains both query fields as expected (list of strings for the breed, dict with 2 keys "up" and "low" with positive integers values for the age). In practice, this would means that the query input json file would be automatically generated from a user-filled form somewhere else, and that some basic checking as already been done at this earlier step. 

### Expected behavior
- empty breed list : [] -> returns nothing and warn user
- breed list is ["nan"] -> returns all entries whith a breed value of "nan"
- breed list is ["*"] -> returns all breed (filtrates only on age)
- breed list contains values that are not in the database -> warn the user and return nothing (or, if it's a list with some valid values for breed, warn the user but return the other breeds)
- age is a range with twice the same value (i.e. 0-0 or 12-12) -> return entries for this specific age
- the numbers in the age range are not sorted (i.e. 15-4) -> sort the values and return entries normally
- query returns 0 results -> returns nothing and warn user, with a different message (i.e. "your query was valid but returned 0 results")

### Code for Query
The code for querying is in the file query.py
it uses an input file in json format. 
There is a model json input in "test_queries/model.json" and many small test queries.

### Code for Testing
I couldn't do the testing proper with a code due to time constrains. 
However, I did test all the test_queries by hand (by running the code from command-line with different inputs). 
Feel free to do the same and play around ! 

## Discussion

### Current limitations and further improvements
This solution is a very minimal solution, that has several issues : 
1. querying the database during the preprocessing step would result in conflicts
2. trying to preprocess data while it is coming too
3. this code only works (for now) if the summary file and its filtrate fits in memory
4.  this code is heavily dependant on the query defined in the task. 
If the client wants to extend the usage in the future (for example, to check which clients have both dog and cat, how many pets they have, or any other smart use of this data) this would result quickly in a convoluted code. 

Points 1,2 and 4 could be avoided by using proper relational database tools, as discussed later. 

For point 3. Please see the next paragraph on scalability.

### Scalability 
Currently, the execution time scales linearly with the number of results, and would not be efficient on the full dataset. 

About the storage itself, the preprocessed data doesn't take more space than the raw one, and the size of the summary file is very small compared to the rest of the data. The problems comes when trying to read the summary file to filter it, and the summary file don't fit in memory. 

The execution time problem and memory can be partially covered by looking at the file in chunks and parallel computing, but if running the query script on a single machine, this solution would be limited too.

This would be more useful when using distributed computing, over distributed data, which lead to my next point.

### Using standard tools
Since all the metadata is already in json, and the data is already on amazon S3, and considering that the data has a well-known and fixed structure, Apache Drill would be my go-to application. 

From Tweag's blog, I learnt about Lagoon, which doesn't need a strict structure like Drill. This could also be an option, but we don't really need the extra power of Lagoon for this specific task. 

Source : https://www.tweag.io/blog/2020-09-23-lagoon-announcement/ 

Another tool that I love is to use the HDF5 file format to store the data. 
It allows to keep data and metadata close together, is made to be read and written in chunks to hosts huge amonts of data that don't fit in memory, can be very efficient in I/O operations when setup properly (pretty much, this means to write and read files in appropriate chunk size), is cross-plateform and has libraries in different languages. (pandas does a good job implementing dataframes in HDF, even with multi-indexes etc.)
https://www.hdfgroup.org/solutions/hdf5/

The problem with HDF5 file format is that I don't know how well it supports concurrency in reading/writing, since I only have used it in frozen datasets. 
This could be a major reason to not use HDF5 file format, and is the reason why I didn't use this solution in the challenge. 

There is also a "HDF on cloud" service ("Highly Scalable Data Service") which I know only by name, but would be a very nice (and open-source) solution.
https://www.hdfgroup.org/solutions/highly-scalable-data-service-hsds/ 

## Closing thoughts

I hope you will find this design clear and interesting. Even though I couldn't do everything I wanted (such as preparing the code for chunking, do proper testing, and put everything in a singularity container to distribute it), I had a lot of fun thinking about the problem and trying to find the most simple solution with the least possible dependencies and requirements. 

