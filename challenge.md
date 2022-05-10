# Data engineering challenge

## The problem

You have been contacted by a pet lifestyle brand called AwesomePets who run an
online shop selling gear for dogs and cats. For the past several years,
AwesomePets have been periodically running a sweepstakes where people can win
free gear for their four-legged friends. To enter, participants must visit the
AwesomePets website and submit a picture of their pet along with a short story
and some personal information. On the website's back-end, the sweepstakes entry
is dumped into a common storage location where AwesomePets staff can browse
submissions to select winners. The AwesomePets sweepstakes has been a *massive*
hit and gets hundreds of thousands of submissions each round.

The pet analytics team at AwesomePets has recently realized that their
sweepstakes dataset contains extremely valuable information which they can use
to model many different aspects of customers and their pets. They want to start
creating models right away but have run into a roadblock. The sweepstakes
dataset has grown over the years to contain a massive amount of data, and they
don't have an easy and efficient way to query it!

This is where you come in.

<img src="https://live.staticflickr.com/65535/47737409971_803b7c1b91_b.jpg"
width="50%" height="50%" />

## Task

AwesomePets management has contacted you to help unblock their analytics team.
The analytics team have asked you to prototype a software solution which allows
them to ***efficiently*** query the sweepstakes dataset, specifying one or more
breeds and a range of ages.

AwesomePets has a strict IT infrastructure policy which means it will take
months to get approval to deploy an out-of-the-box database or query engine. The
analytics team has asked that you implement your own custom application for them
to use in the meantime. Your prototype may copy and transform the data and use
any additional data processing steps as required. While your solution must
implement its own storage and query logic, you are free to use supporting
libraries as you see fit.

The full sweepstakes dataset is massive (100s of Tb-scale) and is stored on
Amazon S3 since it cannot be practically stored on a single disk. To help speed
up your prototyping, AwesomePets has uploaded a sample of their dataset at [this
link](https://pets-challenge.s3.eu-central-1.amazonaws.com/sweepstakes_sample.zip)
for you to develop against. AwesomePets has said the first version of your
prototype can simply operate on this data *locally*.

## Instructions

* Implement a simple database or query engine for querying the sweepstakes
    dataset in your programming language of choice.
  * You are allowed to reuse any standard library functions or third-party
        libraries, but the use of existing databases or query engines is not
        allowed (e.g. SQLite, Postgres, MongoDB, Drill, etc.)
  * All written code should be your own, and any code taken from elsewhere
        (e.g. a Stackoverflow answer) should be clearly identified.
* Specs:
  * Your application should be callable from the command line. It should
      accept a JSON input specifying a query with one or more `breed` and `age`
      parameters and can have any schema you prefer. It can return data in any
      structured format you prefer and should return all of the fields from the
      entry JSON files along with a path to the corresponding images.
  * Since AwesomePets will continue accepting new sweepstake submissions, your
      solution should be able to cope with the addition of new files to the
      dataset.
  * As noted above, AwesomePets wants to ensure that they are able to query
      the sweepstakes dataset efficiently (in terms of execution time). It is up
      to you to decide and document how efficient your solution can and should be.

## Deliverables

* The full source code.
* A README file (in English) including the third-party libraries that you use
  and instructions for running your program(s).
* A DESIGN file (in English) describing in as much detail as possible:
  * The design of the program, along with a rationale for this design and
      trade-offs you made.
  * A discussion of how your solution scales in time and space complexity with
      the ever-increasing size of the sweepstakes dataset (graphs and/or
      illustrative sketches are appreciated).
  * A high-level explanation of how you could solve this problem using
      standard tools and discussion of which tools you would pick.
