import pandas as pd
import datetime
import math

# Read input data
dates = pd.read_csv("input_data/SoupDates.csv",header=None)
ppl_bdays = pd.read_csv("input_data/ParticipantsAndBdays.csv",header=None)
custConstraints = pd.read_csv("input_data/CustomConstraints.csv",header=None)

# Compute sets of "good celebration days" for each person
Dj = {}
# first, the days of the year on which soups fall
soupDates_yday = [datetime.datetime.strptime(x,"%m-%d-%y").timetuple().tm_yday for x in dates[0].values]
# some sloppy rearrangement to clean up on a later date
soupDates_yday_calday = {}
for x in dates[0].values:
    soupDates_yday_calday[datetime.datetime.strptime(x,"%m-%d-%y").timetuple().tm_yday] = x
# By default, "good days" are the 4 soup days closest to that person's birthday or half-birthday
numDaysThatCanBeGood = 4
for idx,row in ppl_bdays.iterrows():
    bday = datetime.datetime.strptime(row[1],"%m-%d")
    bday_yday = bday.timetuple().tm_yday
    halfBday_yday = (bday + datetime.timedelta(days=(math.floor(365/2)))).timetuple().tm_yday
    Dj[idx] = sorted(soupDates_yday, key=lambda 
                             soupday: min(abs(soupday-bday_yday),
                                              abs(soupday-halfBday_yday)))[0:numDaysThatCanBeGood]
# Making use of above sloppiness
for entry in Dj:
    Dj[entry] = [soupDates_yday_calday[yday] for yday in Dj[entry]]

wwith open ("bfOptModel.lp",'w') as f:
    
    # write objective function
    f.write("MINIMIZE\n")
    f.write("OBJECTIVE:\n")
    for k in dates.index.drop(0):
        f.write("+ w_"+str(k-1)+"_"+str(k)+"\n")
    
    # constraints
    f.write("\nSubject to:\n\n")
    
    # write constraint: everyone bakes
    for i in ppl_bdays.index:
        f.write("MustBake_"+str(i)+": ")
        for j in ppl_bdays.index:
            if i == j:
                continue
            for k in dates.index:
                f.write("+ x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
        f.write(" = 1\n")
        
    # write constraint: everyone gets a cake
    for j in ppl_bdays.index:
        f.write("GetsCake_"+str(j)+": ")
        for i in ppl_bdays.index:
            if i == j:
                continue
            for k in dates.index:
                f.write("+ x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
        f.write(" = 1\n")
        
    # write constraint: everyone gets a good day
    for j in ppl_bdays.index:
        f.write("GetsGoodDay_"+str(j)+": ")
        for i in ppl_bdays.index:
            if i == j:
                continue
            for k in dates.index:
                if dates.loc[k][0] not in Dj[j]:
                    f.write("+ x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
        f.write(" = 0\n")
        
    # write constraint: cake presence indicator for date k
    for k in dates.index:
        f.write("Date_"+str(k)+"_CakeIndicator: -y_"+str(k)+"\n")
        for i in ppl_bdays.index:
            for j in ppl_bdays.index:
                if i == j:
                    continue
                f.write("+ x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
        f.write(" >= 0 \n")
        
    # write constraint: count of bdays on date k
    for k in dates.index:
        f.write("Date_"+str(k)+"_NumCakes: -n_"+str(k)+"\n")
        for i in ppl_bdays.index:
            for j in ppl_bdays.index:
                if i == j:
                    continue
                f.write("+ x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
        f.write(" = 0 \n")
        
    # write constraint: trigger for w_k-1,k    
    for k in dates.index.drop(0):
        f.write("Trigger_w_"+str(k-1)+"_"+str(k)+":  "+
                "w_"+str(k-1)+"_"+str(k)+" + y_"+str(k-1)+" + y_"+str(k)+" >= 1\n")
        
    ## custom constraints
    for c in custConstraints.index:
        person = custConstraints.loc[c][0]
        personidx = ppl_bdays.loc[ppl_bdays[0] == person].index.tolist()[0]
        date = custConstraints.loc[c][2]
        k = dates.loc[dates[0] == date].index.tolist()[0]
        ending = " = 0\n" if custConstraints.loc[c][3] == "forbid" else " = 1\n"
        f.write("CustomConstraint_"+str(c)+": \n")
        if custConstraints.loc[c][1] == "celebrate":
            # writing constraint for this person's receipt (they are j \in P)
            j = personidx
            for i in ppl_bdays.index:
                if i == j:
                    continue
                f.write(" + x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
            f.write(ending)
        elif custConstraints.loc[c][1] == "prepare":
            # writing constraint for this person's delivery (they are i \in P)
            i = personidx
            for j in ppl_bdays.index:
                if i == j:
                    continue
                f.write(" + x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
            f.write(ending)
    
    # Binary statement
    f.write("Binary\n")
    # w vars
    for k in dates.index.drop(0):
        f.write("w_"+str(k-1)+"_"+str(k)+"\n")
    # y vars
    for k in dates.index:
        f.write("y_"+str(k)+"\n")
    # x vars
    for i in ppl_bdays.index:
        for j in ppl_bdays.index:
            if i == j:
                continue
            for k in dates.index:
                f.write("x_"+str(i)+"_"+str(j)+"_"+str(k)+"\n")
                
    # Conclude
    f.write("\n\nEnd\n")
    
f.closed