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

### json files  
The sample data contains 1000 "entries" file (json file, one file per day considering the naming of the file)

Each json file contains several entries (usually 4-5, we have to assume a variable number of entries per file).  
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



## Edge cases to test

## First working prototype

### rationale

### what's wrong with it

##
