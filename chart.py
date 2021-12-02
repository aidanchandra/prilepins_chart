from pprint import pprint


class prilepin_chart: 
    import csv
    from pprint import pprint
    from typing import Type
    import numbers

    '''
    Lean chooses the set/rep range when none exists for the provided %1RM
    For example, for a %1RM of 78%, the closest are 80% (5sx3r) and 75% (5sx4r)
    With a lean of HIGH, the reps/sets defaults to the higher percent,
    effecitvely making the session easier by using reps/sets from a higher %1rm.
    With a lean of LOW, the reps/sets defaults to the lower percent, so it's
    as if you were training at that lower percent, making the session more difficult
    With a lean of ROUND, the program selects the closest rep/set choice by the closest
    %1RM.
    '''

    def __init__(self) -> None:
        self.prilipenes_by_reps, self.rep_set_data_by_high_med_low = self.get_charts()


    ##*************************
    ##*** Utility Functions ***
    ##*************************
    def key_locator(self, dict_in: dict, key: numbers.Complex, lean) -> dict:
        """Returns the closest value to the key in the dict based off of lean rules

        Args:
            dict_in (dict): dict from which we locate the cloest key
            key (float or int): key to locate and return within dict_in

        Returns:
            dict[closest number]
        """    
        returnable = None
        if not isinstance(dict_in, dict):
            raise TypeError("Argument dict_in is not of type dict " + str(type(dict_in)))
        if not isinstance(key, self.numbers.Complex):
            raise TypeError("Arugment key is not a float, got " + str(type(key)))

        try:
            returnable = dict_in[key]
        except KeyError:
            if lean == "HIGH":
                return self.key_locator(dict_in, key+1)
            if lean == "LOW":
                return self.key_locator(dict_in, key-1)
            if lean == "ROUND":
                for i in range(0,1000):
                    if (round(key+(i/10),2)) in dict_in.keys():
                        return dict_in[round(key+(i/10),2)]
                    if (round(key-(i/10),2)) in dict_in.keys():
                        return dict_in[round(key-(i/10),2)]



        return returnable

    def get_charts(self):
        """Gets the necessary charts from CSVs
        """    
        
        repsets = []
        with open("data/RepsSets.csv") as csvfile:
            reader = self.csv.reader(csvfile) 
            for row in reader: 
                repsets.append(row)

        prils = []
        with open("data/Pril.csv") as csvfile:
            reader = self.csv.reader(csvfile) 
            for row in reader:
                prils.append(row)

        self.rep_set_data_by_high_med_low = {}
        self.rep_set_data_by_high_med_low["high"] = {}
        self.rep_set_data_by_high_med_low["med"] = {}
        self.rep_set_data_by_high_med_low["low"] = {}

        for row in repsets[1:]:
            self.rep_set_data_by_high_med_low["high"][float(row[0])/100] = [int(row[1]), int(row[2])] ##Sets of reps
            self.rep_set_data_by_high_med_low["med"][float(row[0])/100] = [int(row[3]), int(row[4])] ##Sets of reps
            self.rep_set_data_by_high_med_low["low"][float(row[0])/100] = [int(row[5]), int(row[6])] ##Sets of reps

        self.prilipenes_by_reps = {}
        for row in prils[1:]:
            self.prilipenes_by_reps[int(row[0])] = float(row[1])/100
        
        return self.prilipenes_by_reps, self.rep_set_data_by_high_med_low

    ##************************
    ##***** Calculations *****
    ##************************
    def calculate(self, onerm_percent, onerm_weight, lift_name, reps_per_set_modifier=0, total_reps_modifier=0, lean="ROUND"):
        sets_of_reps = self.get_rep_sets(onerm_percent, reps_per_set_modifier, total_reps_modifier, lean) ##Calculate the reps per set given our working % and modifiers to increase or decrease that

        reps = sets_of_reps[1]
        sets = sets_of_reps[0]

        prilipenes_intensity = self.prilipenes_by_reps[reps]
        actual_intensity = onerm_percent/prilipenes_intensity ##Calculate the actual intensity of this session

        return actual_intensity, [sets,reps,round(onerm_percent,1),round(onerm_weight*(onerm_percent/100),1),round(actual_intensity,1)] ##Return the data

    def get_rep_sets(self, onerm, reps_per_set_lean_percent, total_reps_lean_percent, lean):
        '''
        Lean of 0 is optimal
        Lean of 0.2 is 20% more difficult of the delta between optimal reps and
        '''
        repset = {}
        with open("RepSets_two.csv") as csvfile:
            reader = self.csv.reader(csvfile)

            firstRow = True
            for row in reader:
                if firstRow:
                    firstRow = False
                    continue
                repset[int(row[0])] = {
                    'Reps/Set':[float(row[1]),float(row[2])],
                    'OptimalReps/Set':float(row[3]),
                    'TotalReps':[float(row[4]),float(row[5])],
                    'OptimalTotal':float(row[6]),
                }
        
        desired_data = self.key_locator(repset, onerm, lean=lean)
        '''
            {'OptimalReps/Set': 1.0,    Optimal
            'OptimalTotal': 2.0,        Optimal
            'Reps/Set': [2.0, 1.0],     High/Low tolerances
            'TotalReps': [2.0, 1.0]}    High/Low tolerances
        '''

        total_upper_delta = abs(desired_data['OptimalTotal'] - desired_data['TotalReps'][0])
        total_lower_delta = abs(desired_data['OptimalTotal'] -desired_data['TotalReps'][1])
        optimal_total_reps = desired_data["OptimalTotal"]


        reps_per_set_upper_delta = abs(desired_data['OptimalReps/Set'] - desired_data['Reps/Set'][0])
        reps_per_set_lower_delta = abs(desired_data['OptimalReps/Set'] - desired_data['Reps/Set'][1])
        optimal_reps_per_set = desired_data["OptimalReps/Set"]
        

        desired_reps_per_set = int((optimal_reps_per_set + (reps_per_set_lean_percent * reps_per_set_upper_delta) if reps_per_set_lean_percent > 0 else optimal_reps_per_set + (reps_per_set_lean_percent * reps_per_set_lower_delta)))
        desired_total_reps = int((optimal_total_reps + (total_reps_lean_percent * total_upper_delta) if total_reps_lean_percent > 0 else optimal_total_reps + (total_reps_lean_percent * total_lower_delta)))
        
        sets = int(desired_total_reps/desired_reps_per_set)
        reps = desired_reps_per_set

        return [sets,reps]






