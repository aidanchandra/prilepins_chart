from chart import prilepin_chart
pril_chart = prilepin_chart()

#Lift and onerm
lift = "Deadlift"
onerm = 225

#Total duration of training w/lift frequency
weeks = 8
frequency = 2

#Cadence of modifications
cadence = [0,-0.5] #Session-Session periodization. If you train a lift 3 times a week, a cadence of [-0.2, 0.2, 0] may be advisable


desired_intensity = 75
weight = 75

jump = 1.3      #Jump in actual intensity per session OR week
tolernace = 0.1 #Acceptable error % in jumps of actual intensity

'''
    Constant modifier to increase/decrease reps per set. Negative means less reps per set (strength focused) and
    positive means more reps per set (power/mass)
'''
rep_mod = 0   

'''
    Constant modifier to increase/decrease total reps. Negative means less overall reps (strength focused) and
    positive means more reps per set (mass)
''' 
volume_mod = 0

if len(cadence) != frequency:
    print("It's reccomened to have the cadence match the frequency")
    input()

for week in range(0,weeks*frequency): 
    desired_mod = cadence[week%(len(cadence))]
    
    old_intensity = desired_intensity
    desired_intensity+=jump

    calculated_intensity = desired_intensity
    
    
    calculated_intensity, string = pril_chart.calculate(weight, onerm, lift, reps_per_set_modifier = rep_mod, total_reps_modifier=volume_mod)
    while desired_intensity-calculated_intensity > tolernace:
        
        if calculated_intensity > desired_intensity:
            weight -=1
        else:
            weight+=1
        
        calculated_intensity, string = pril_chart.calculate(weight, onerm, lift, reps_per_set_modifier = rep_mod, total_reps_modifier=volume_mod)
        
    print("Session " + str(week+1))
    print("Warmup: ")
    
    for i in range(0,string[0]): ##For each set
        print(str(string[1]) + "r@" + str(string[2]) + "%(" + str(string[3]) + ")[" + str(string[4]) + "]")
        print("")
    
    desired_intensity=calculated_intensity