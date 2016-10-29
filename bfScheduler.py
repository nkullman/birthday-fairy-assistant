def main():
    print("Hi, Birthday Fairy,")
    print("I\'m here to help you spread the birthday joy.")
    print("")
    print("For each participant, I look at the N best soup dates for them,")
    print("which are the N soup dates closest to either their birthday or half-birthday.")
    print("")
    print("Would you tell me, how large should I make N?")
    print("(Something like 4 or 5 is suggested. Larger values tend to produce more even birthday spreads.)")
    numDaysThatCanBeGood = int(input())
    print("Great, N set to "+str(numDaysThatCanBeGood)+".")
    print("")
    print("Here we go...")
    import pandas as pd
    import datetime
    import math
    import os

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

    print("Writing the model file...")
    with open ("cplex/bfOptModel.lp",'w') as f:
        
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
    print("")
    print("Model file written. Solving the model...")
    os.system("cplex < cplex/batchInstructionsForCPLEX.txt")
    print("")
    print("Model solved. Getting output...")

    # make template for output df
    valsdf = pd.DataFrame({"Variable":[],"Value":[]}).set_index("Variable")

    # indicator for whether we are in the variable section of the file
    inVars = False
    with open("cplex/bfOptSolution.sol",'r') as f:
        for line in f:
            # if not inVars before but entering now, change the value on the toggle
            if not(inVars) and (line[3] == 'v' and line[4:6] == "ar"):
                inVars = True
            # if toggle still negatory, skip the line
            if not(inVars):
                continue
            # toggle flipped, heads up for the end of the section now
            if line[2] == '/':
                inVars == False
                break
            # found a variable. store its info
            # first, variable name
            varstart = line.find('name="')+6
            varend = line.find('"',varstart)
            var = line[varstart:varend]
            # next, variable value
            valend = line.rfind('"')
            valstart = line.rfind('"',0,valend-1)+1
            val = line[valstart:valend]
            # store in output dataframe
            valsdf.ix[var,:] = float(val)
    f.closed
    print("Output read.")
    print("Scrubbing output...")
    outcols = ["DessertChef","PreparesFor","OnDate"]
    outdf = pd.DataFrame(columns=outcols)
    assignments = valsdf.loc[(valsdf.index.str.startswith("x")) & (valsdf["Value"]>0)]
    for var,row in assignments.iterrows():
        a = var.split("_")
        i = int(a[1])
        j = int(a[2])
        k = int(a[3])
        chef = ppl_bdays.loc[i][0]
        recipient = ppl_bdays.loc[j][0]
        date = dates.loc[k][0]
        outdf.loc[len(outdf)] = [chef,recipient,date]
    print("Writing to file...")
    outdf.to_csv("bfAssignments.csv",index=None)
    print("Done!")

main()
