# Birthday Fairy Assistant
Hello, Birthday Fairies,

The burden's on you to figure out who gets a celebratory dessert on which dates and who has to prepare this dessert. And if that weren't enough, there's a spacing factor to this -- no one likes long dessert droughts, right?

Welcome to your new celebration scheduling assistant.

You're a couple clicks away from the optimal schedule of dessert distribution.

## How to use the scheduler
### 0. Clone this repository
`git clone https://github.com/nkullman/birthday-fairy-assistant.git`
### 1. Modify the input data
1. __Soup dates__ `input_data/SoupDates.csv`
    - A list of dates in mm-dd-yy format (demo data are the Wednesdays of the 30 weeks of instruction in UW's 2016-2017 academic year)
    
        | Soup Date |
        |-----------|
        | 9-28-16   |
        | 10-5-16   |
    
2. __Your participants and their birthdays__ `input_data/ParticipantsAndBdays.csv`
    - A list of participants' names and their birthdays in mm-dd format  
    
        | Participant       | Birthday |
        |-------------------|----------|
        | Charles Darwin    | 2-12     |
        | Charles Schwab    | 7-19     |
        | Charles Barkley   | 2-20     |
        | Charles Lindbergh | 2-4      |

3. __Any other custom constraints__ `input_data/CustomConstraints.csv`
    - A list of names, events, dates, and conditions that define custom constraints
    
        | Participant       | Event     | Date    | Condition |
        |-------------------|-----------|---------|-----------|
        | George Washington | celebrate | 1-4-17  | forbid    |
        | Larry Bird        | prepare   | 10-5-16 | require   |
    
    - The names must match a participant's name exactly, and the dates must match a soup date exactly
    - The last column determines whether the constraint is one forbidding an assignment or requiring an assignment (allowable values in this column are "forbid" and "require")
    - The second column determines whether the constraint is for a person's celebration or preparation of dessert (allowable values in this column are "celebrate" and "prepare").
    - For example, the first line in the demo file adds the constraint that says "We cannot celebrate George Washington's birthday at the soup on January 4, 2017." The second line adds the constraint saying "Larry Bird must prepare a birthday dessert on October 5, 2016."

### 2. Make sure you have what you need
The scheduler requires the following:
 - The CPLEX executable in your `PATH` environment variable (get CPLEX for free [here](https://www.ibm.com/developerworks/community/blogs/jfp/entry/CPLEX_Is_Free_For_Students?lang=en))
 - Python 3.x and a few common libraries: math, os, datetime, and pandas
 
### 3. Run `bfScheduler.py`

### 4. Behold your optimal solution
Your assignments are in `bfAssignments.csv`

| DessertChef              | PreparesFor       | OnDate   |
|--------------------------|-------------------|----------|
| George Washington        | Dwyane Wade       | 1-4-17   |
| George Washington Carver | Charles Lindbergh | 2-1-17   |
| Langston Hughes          | Donald Trump      | 11-16-16 |
