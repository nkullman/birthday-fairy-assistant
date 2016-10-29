# Birthday Fairy Assistant
Hello, Birthday Fairies,

It's been placed on you to figure out who gets a celebratory dessert on which dates and who has to prepare this dessert. And if that weren't enough, there's a spacing factor to this -- no one likes long dessert droughts, right?

Welcome to your new celebration scheduling assistant.

You're a couple clicks away from the optimal dessert distribution.

## How to use the scheduler
### 1. Modify the input data
1. __Soup dates__
    - A list of dates in mm-dd-yy format (demo data are the Wednesdays of the 30 weeks of instruction in UW's 2016-2017 academic year)
2. __Your participants and their birthdays__
    - A list of participants names and their birthdays in mm-dd format
3. __Any other custom constraints__
    - A list of names, events, dates, and conditions that define custom constraints
    - The names must match a participant's name exactly, and the dates must match a soup date exactly (including the mm-dd-y formatting)
    - The last column determines whether the constraint is one forbidding an assignment or requiring an assignment (allowable values in this column are "forbid" and "require")
    - The second column determines whether the constraint is for a person's celebration or preparation of dessert (allowable values in this column are "celebrate" and "prepare").
    - For example, the first line in the demo file adds the constraint that says "We cannot celebrate George Washington's birthday at the soup on January 4, 2017." The second line adds the constraint saying "Larry Bird must prepare a birthday dessert on October 5, 2016."
