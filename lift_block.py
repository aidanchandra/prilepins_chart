from typing import Iterable, List
import csv
import time
import matplotlib

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.pyplot import plot, streamplot, text
from random import randint
from matplotlib.ticker import MaxNLocator

class lift_set:
    def __init__(self, weight:float, reps:int, percent_onerm:float, actual_intensity:float) -> None:
        self.weight = weight
        self.reps = reps
        self.percent_onerm = percent_onerm
        self.actual_intensity = actual_intensity
        pass
    def __str__(self) -> str:
        return str(self.reps) + "r@" + str(self.percent_onerm) + "%(" + str(self.weight) + ")[" + str(self.actual_intensity) + "]"

class lift_session:
    def __init__(self,  lift_name:str, session_number:int = None, session_week:int = None, session_weekly_number:int = None,sets:List[lift_set]=None) -> None:
        self.session_number = session_number
        self.session_week = session_week
        self.session_weekly_number = session_weekly_number
        self.lift_name = lift_name
        
        if sets is not None:
            self.sets = sets
        else:
            self.sets = []
        pass

    def get_working_weight(self):
        #TODO: Named this way to program in warmup sets later on
        return self.get_weight()

    def get_actual_intensity(self):
        total = 0
        for set in self.sets:
            total += set.actual_intensity
        return round(total/len(self.sets),1)
    
    def get_weight(self):
        total = 0
        for set in self.sets:
            total += set.weight
        return round(total/len(self.sets),1)

    def get_volume(self):
        total = 0
        for set in self.sets:
            total += set.reps
        return total

    def get_session_week(self):
        return self.session_week
    
    def get_session_date(self):
        return self.session_weekly_number

    def set_session_number(self, session_number:int):
        self.session_number = session_number
    
    def set_session_week(self, session_week:int):
        self.session_week = session_week
    
    def set_session_weekly_number(self,session_weekly_number:int):
        self.session_weekly_number = session_weekly_number


    def add_set(self, set:lift_set):
        self.sets.append(set)

    def is_unspecified(self) -> bool:
        return self.session_number == None and self.session_week == None and self.session_weekly_number == None
    
    def __str__(self) -> str:
        if(self.session_number != None and self.session_week != None and self.session_weekly_number != None):
            return "Week " + str(self.session_week) + " Session " + str(self.session_weekly_number) + " (#" + str(self.session_number) + ")"
        elif (self.session_number != None):
            return "Session #" + str(self.session_number)
        else:
            return "Unidentified Session"
    
    def reps_as_string(self) -> str:
        returnable = ""
        for rep in self.sets:
            returnable += "     " + str(rep) + "\n"
        return returnable

    def session_string(self) -> str:        
        returnable = ""
        returnable += self.__str__() + "\n"
        for rep in self.sets:
            returnable += "     " + str(rep) + "\n"
        return returnable
    


class lift_block:

    def __init__(self, lift_name) -> None:
        self.lift_name = lift_name
        self.sessions = []
        self.session_numbers = []
        self.next_session_number = 1
        pass
    
    def add_session(self, session:lift_session):

        if session.is_unspecified():
            session.set_session_number(self.next_session_number)
            self.next_session_number += 1

        if session.session_number in self.session_numbers:
            raise Exception("Session number collision in lift block when adding " + str(session))

        if session.lift_name != self.lift_name:
            print("Warning, lift names do not match (" + str(session.lift_name) + " as session does not match " + self.lift_name + ")")
        
        self.sessions.append(session)
        self.session_numbers.append(session.session_number)
    
    def __str__(self) -> str:
        returnable = ""
        for session in self.sessions:
            returnable += " " + session.session_string()
        return returnable



    def get_csv(self, output_name:str=None):

        rows = []
        for session in self.sessions:
            row = ["#" + str(session.session_number)]
            for set in session.sets:
                row.append(str(set))
            rows.append(row)

        filename = str(self.lift_name) + ".csv" if output_name == None else output_name
            
        with open(filename, 'w') as csvfile: 
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerows(rows)
    

    def get_as_figure(self) -> Figure:

        fig = Figure(figsize = (5, 5),
                        dpi = 100)

        x = []
        actual_intensity_arr = []
        weight_arr = []
        volume_arr = []
        i = 0
        for session in self.sessions:
            x.append(i)
            i+=1
            actual_intensity_arr.append(session.get_actual_intensity())
            weight_arr.append(session.get_weight())
            volume_arr.append(session.get_volume())

        plot1 = fig.add_subplot(311)

        #plot1.plot(actual_intensity_arr)
        plot1.plot(x, actual_intensity_arr, label = "Actual Intensity")
        ##TODO: Force integer x axis
        plot2 = fig.add_subplot(312)

        plot2.plot(x, weight_arr, label = "Weight")

        plot3 = fig.add_subplot(313)

        plot3.plot(x, volume_arr, label = "Volume")

        plot3.legend()
        plot2.legend()
        plot1.legend()
        return fig
    
    


class pril_lift_block(lift_block):

    def __init__(self, lift_name:str, onerm:float, phase_number:int = 1, weekly_frequency:int = None, session_periodization:List[int]=[0], deload:bool = False) -> None:
        super().__init__(lift_name)
        
        self.phase_number = phase_number
        self.onerm = onerm
        self.pril_chart = prilepin_chart()
        self.session_periodization = session_periodization
        self.deload = deload
        self.weekly_frequency = weekly_frequency
        self.session_counter = 0
        

    def __str__(self) -> str:
        return "Phase " + str(self.phase_number) + ":\n" + super().__str__() if not self.deload else "Deload Phase " + str(self.phase_number) + ":\n" + super().__str__()
        
    def phase_str(self) -> str:
        return "Phase " + str(self.phase_number) if not self.deload else "Deload Phase " + str(self.phase_number)

    def get_phase_summary(self):
        """Returns a string of the following statistics

            Start and end weight
            Total amount of sessions
            Average jumps in intensity
            Weekly per-session periodization
        """        
        #TODO: Reconcile the whole phase/block synonym thing
        #TODO: Don't delete me you fuck
        returnable = ""
        returnable += "Starting at weight " + str(self.get_starting_weight())
        returnable += " and ending at weight " + str(self.get_ending_weight())
        returnable += " in " + str(len(self.sessions)) + " sessions"
        returnable += " over " + str(self.sessions[-1].session_week) + " weeks"
        #TODO: returnable += '\n with jumps of ' + self.
        return returnable

    def get_starting_weight(self):
        try:
            return self.sessions[0].get_working_weight()
        except IndexError:
            raise Exception("Tried to request starting weight of a block with no sessions")
    
    def get_ending_weight(self):
        try:
            return self.sessions[-1].get_working_weight()
        except IndexError:
            raise Exception("Tried to request starting weight of a block with no sessions")

    def add_session(self, session):
        if self.weekly_frequency != None:
            session.set_session_week(1 + int(self.session_counter / self.weekly_frequency))
            session.set_session_number(1 + self.session_counter)
            session.set_session_weekly_number(1 + self.session_counter % self.weekly_frequency)
            self.session_counter +=1
            super().add_session(session)

        else:
            super().add_session(session)

    
    def generate_session(self, desired_actual_intensity:float, tolerance:float = 0.1, disable_periodization:bool=False) -> lift_session:
        if not disable_periodization:
            desired_actual_intensity += self.session_periodization[self.session_counter%len(self.session_periodization)]
        training_percent = 0
        session = self.pril_chart.calculate(training_percent, self.onerm, self.lift_name)

        while abs(desired_actual_intensity - session.get_actual_intensity()) > tolerance:
            if session.get_actual_intensity() > desired_actual_intensity:
                training_percent -=0.1
                session = self.pril_chart.calculate(training_percent, self.onerm, self.lift_name)
            else:
                training_percent+=0.1
                session = self.pril_chart.calculate(training_percent, self.onerm, self.lift_name)
        
        #Session now matches our desired actual intensity
        
 
        return session
        
    

    def generate_next_session(self, intensity_jump:float, disable_periodization=False) -> lift_session:
        if self.sessions == []:
            raise Exception("No session to generate next from")
        
        desired_intensity = intensity_jump + self.sessions[-1].get_actual_intensity() + self.session_periodization[self.session_counter%len(self.session_periodization)]
        return self.generate_session(desired_intensity)


class periodized_program():
    
        
        def __init__(self, lift_name:str, start_weight:float, end_weight:float, phases:int, frequency_per_week:int, weekly_periodization_per_phase:List[List[float]], percent_increase_arr:List[float], 
            gain_per_phase:List[float]=None, reset_percent:float=0.8, program_deload:bool=True, phase_week_limit:int=None) -> None:
            
            self.lift_name = str(lift_name)
            
            if phases != len(gain_per_phase):
                raise Exception("Number of phases does not match gain per phase")
            elif phases != len(weekly_periodization_per_phase):
                raise Exception("Number of phases does not match the number of weeks in the weekly periodization")


            ##Calculate the end max PER PHASE
            weight_gain = end_weight - start_weight

            sum = 0
            for gain in gain_per_phase:
                sum +=gain
            if sum != weight_gain:
                raise Exception("Desired total weight gain does not equal the sum of gains each phase")
            
            if gain_per_phase is None:
                gain_per_phase = [weight_gain/phases for i in range(0,phases)]
            
            self.blocks = []

            iterative_weight = start_weight
            for phase in range(0, phases):
                percent_increase = percent_increase_arr[phase]
                phase_start_weight = iterative_weight
                phase_end_weight = phase_start_weight + gain_per_phase[phase]
                phase_periodization = weekly_periodization_per_phase[phase]

                ##Create a phase block with the goal end weight
                print("Starting at",phase_start_weight,"Going to",phase_end_weight)

                phase_block = pril_lift_block(lift_name, phase_end_weight, phase + 1, frequency_per_week, session_periodization=phase_periodization)

                ##Add the first session at the reset percent 
                phase_block.add_session(phase_block.generate_session(reset_percent * 100))

                ##If we are time limited, calcualte a new percent jump that will reach 100 in the recommended time
                if phase_week_limit is not None:
                    percent_to_increase = 100 * (1-reset_percent)
                    percent_increase = percent_to_increase/phase_week_limit

                ##-----------------------


                ##Then, just do a percent increase unitl we hit 100%
                session_to_add = phase_block.generate_next_session(percent_increase/frequency_per_week)
                while session_to_add.get_actual_intensity() < 100:
                    phase_block.add_session(session_to_add)
                    session_to_add = phase_block.generate_next_session(percent_increase/frequency_per_week)
                    
                ##-----------------------
                

                ##This phase is done
                self.blocks.append(phase_block)

                ##Add a dload phase
                if program_deload:
                    deload_block = pril_lift_block(lift_name, phase_end_weight*0.8, phase + 1, frequency_per_week, session_periodization=phase_periodization, deload=True)
                    deload_block.add_session(phase_block.generate_session(0.6 * 100))
                    for i in range(0, frequency_per_week-1):
                        deload_block.add_session(deload_block.generate_next_session(5))
                
                    self.blocks.append(deload_block)

                iterative_weight = phase_end_weight
            pass

        def get_blocks(self):
            return self.blocks

        def as_csv(self, filename:str, seperate_sets:bool = False):
            headers = ["Block", "Session", "Set"]
            rows = []
            for block in self.blocks:
                if isinstance(block, pril_lift_block):
                    block_cell = block.phase_str()
                    for session in block.sessions:
                        session_cell = str(session)
                        if seperate_sets:
                            for set in session.sets:
                                rows.append([block_cell, session_cell, str(set)])
                        else:
                                rows.append([block_cell, session_cell, session.reps_as_string()])

            
            with open(filename, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)
                csvwriter.writerows(rows)
        
        def as_PDF(self):
            return lift_block_PDF(self)


# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.validators import Auto
# from reportlab.graphics.charts.legends import Legend
# from reportlab.graphics.charts.piecharts import Pie
# from reportlab.graphics.shapes import Drawing, String
# from reportlab.platypus import SimpleDocTemplate, Paragraph
# from reportlab.graphics.charts.legends import Legend
# from reportlab.graphics.charts.piecharts import Pie
# from reportlab.pdfbase.pdfmetrics import stringWidth, EmbeddedType1Face, registerTypeFace, Font, registerFont
# from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
# from reportlab.lib.colors import Color, PCMYKColor, white
# from reportlab.platypus import PageBreak
# from reportlab.platypus import Spacer
# from reportlab.graphics.shapes import Drawing
# from reportlab.graphics.charts.piecharts import Pie
# from reportlab.lib.units import inch
# from reportlab.lib.styles import (ParagraphStyle, getSampleStyleSheet)
# from reportlab.lib.colors import purple, PCMYKColor, red, Color, CMYKColor, yellow
# from reportlab.graphics.charts.legends import Legend
# from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
# from reportlab.lib.validators import Auto
# from reportlab.pdfbase.pdfmetrics import stringWidth, EmbeddedType1Face, registerTypeFace, Font, registerFont
# from reportlab.graphics.charts.barcharts import VerticalBarChart
# from reportlab.graphics.charts.textlabels import Label
# from pprint import pprint
# from reportlab.platypus import SimpleDocTemplate, Image
# import random
# from reportlab.lib import utils

from reportlab.lib import utils, colors
from reportlab.pdfbase import pdfform
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, flowables, Image, PageBreak, Table, TableStyle, Flowable
import string
import random
import datetime
import os

interactiveTextBoxNameIterator = 0 #This literally just incraments everytime we call InteraciveTextBox for unnamed fields ("") so they don't collide. this is terrible. #TODO: Please fix
class lift_block_PDF:

    center_header_1 = ParagraphStyle('Header 1',
                            fontName="Times",
                            fontSize=26,
                            leading = 0,
                            alignment=1,
                            spaceAfter=18)
    
    center_header_1_bold = ParagraphStyle('Header 1',
                            fontName="Times-bold",
                            fontSize=26,
                            leading = 20,
                            alignment=1,
                            spaceAfter=26)

    center_header_2 = ParagraphStyle('Header 1',
                            fontName="Times",
                            fontSize=22,
                            leading = 20,
                            alignment=1,
                            spaceAfter=16)

    left_header_1 = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=14,
                                alignment=0,
                                spaceAfter=16)

    left_header_2 = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=12,
                                alignment=0,
                                spaceAfter=16)

    left_header_3 = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=17,
                                alignment=0,
                                spaceAfter=22)

    left_header_4 = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=11,
                                alignment=0,
                                spaceAfter=22)

    cell_body_1 = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=11,
                                alignment=0,
                                spaceAfter=6)

    class InteractiveTextbox(Flowable):
        def __init__(self, name:str, width:int, tooltip:str="", height:int=13,
        borderStyle:str='solid', relative=True, borderColor=colors.black, fillColor=colors.white):

            Flowable.__init__(self)
            global interactiveTextBoxNameIterator
            if name == "":
                self.name = str(interactiveTextBoxNameIterator)
                interactiveTextBoxNameIterator +=1
            else:
                self.name = name

            self.tooltip = tooltip
            self.width = width
            self.height = height
            self.borderStyle = borderStyle
            self.relative = relative
            self.bordercolor = borderColor
            self.fillColor = fillColor

        def draw(self):
            self.canv.saveState()
            pdfform.textFieldRelative(self.canv, self.name, maxlen=1000, xR=0, yR=0, width=self.width, height=self.height, multiline=self.height >= 14)
            self.canv.restoreState()

    def __init__(self, pril_program:periodized_program) -> None:
        self.pril_program = pril_program

        self.phase_index = pril_program

    def get_height(self, elements):
        #TODO: The wrap function edits the object it's sensing and therefore is the reason for needing the regenerate below
        if isinstance(elements, Iterable):
            total_height = 0
            for flowable in elements:
                w, h = flowable.wrap(0,0)
                total_height += h
            return total_height
        else:
            w, h = elements.wrap(0,0)
            return h

    def generate_PDF(self, filename:str,
            draw_graphs:bool,
            seperate_phases:bool,
            draw_summary:bool,
            draw_RPE:bool,
            draw_recovery:bool,
            draw_warmup:bool,
            draw_cooldown:bool,
            fillable:bool,
            timestepped:bool,
            forcetime:bool,
            writable:bool,
            draw_empty_sets:bool,
            num_empty_sets_before:int=None,
            num_empty_sets_after:int=None,
            start_datetime:datetime.datetime=None,
            notes:str=None, #TODO: Might have to be defaulted to ""
        ):

        

        if forcetime and start_datetime == None:
            raise Exception("Requested to force dates but provided no starting date")
        
        if draw_empty_sets and (num_empty_sets_after == None or num_empty_sets_before == None):
            raise Exception("Need to specify nubmer of sessions before and after since draw_empty_sets is set to True")

        #height is 215 when we have fillable and 310 when is not fillable (BRUH)
        TOTAL_PAGE_HEIGHT = 570 if writable else 830 #I hate this so much
        current_height = 0 
        elements = []
        if seperate_phases:
            #TODO: This should be easy
            for phase in self.pril_program.get_blocks():
                pass

        else:
            doc = SimpleDocTemplate(filename+'.pdf')
            index = 0

            for phase in self.pril_program.get_blocks():

                self.addTo(elements, self.generate_header(phase, notes))
                
                if draw_graphs:
                    self.addTo(elements,self.generate_graph(phase))
                    current_height = TOTAL_PAGE_HEIGHT/2 ##Always assume the first top stuff will take up at most a half page
                else:
                    current_height = 10 ##Always assume the first top stuff will take up at most a half page

                if draw_summary:
                    self.addTo(elements, Paragraph(phase.get_phase_summary(), self.left_header_4))


                for session in phase.sessions:
                    session_header = self.generate_session_header(session, timestepped, forcetime, start_datetime) ##Single flowable
                    table = self.generate_session_block(session, 
                        draw_RPE, draw_recovery, draw_warmup, draw_cooldown, 
                        fillable, writable, draw_empty_sets, num_empty_sets_before, num_empty_sets_after) ##List of a bunch of tables
                    height_about_to_add = self.get_height( table)

                    print("")
                    print(str(session))
                    print("Current height",current_height)
                    print("About to add", height_about_to_add) #215 
                    print("Would result in", (current_height+height_about_to_add))
                    print("Total allowed height", TOTAL_PAGE_HEIGHT)
                    if (current_height + height_about_to_add) > TOTAL_PAGE_HEIGHT:
                        print("Pagebreak")
                        elements.append(PageBreak())
                        current_height = height_about_to_add ##Since we r on a new page
                    else:
                        current_height += height_about_to_add
                    
                    self.addTo(elements, session_header)
                    self.addTo(elements, self.generate_session_block(session, 
                        draw_RPE, draw_recovery, draw_warmup, draw_cooldown, 
                        fillable, writable, draw_empty_sets, num_empty_sets_before, num_empty_sets_after)) ##This regenrates bc the widths get fucked up if I don't regenerate it... fuck this
                
                self.addTo(elements,PageBreak())
                index +=1
            
            doc.build(elements)
        
        self.clear_temp_files()

        

    def clear_temp_files(self, path="temp/"):
        for file in os.scandir(path):
            os.remove(file.path)

    def addTo(self, elements:list, object: flowables):
        """Helper function to always add either a flowable or each flowable in a list to elements

        Args:
            elements (list): elements
            object (either a flowable or a list of flowables): object
        """      
        try:
            elements.extend(object)
        except:
            elements.append(object)

    def generate_session_block(self, session:lift_session, draw_RPE:bool, draw_recovery: bool, draw_warmup:bool, draw_cooldown:bool, fillable:bool, 
        writable:bool, draw_empty_sets:bool, num_empty_sets_before:int, num_empty_sets_after:int):

        def cellText(data:str, height=None):
            if height == None:
                return Paragraph(data, self.cell_body_1)
            else:
                temp_style = ParagraphStyle('Header 1',
                                fontName="Times",
                                fontSize=11,
                                alignment=0,
                                spaceAfter=6,
                                leading=height)
                return Paragraph(data, temp_style)



        tables = []

        TOTAL_WIDTH = 400

        #Top header
        if fillable:
            if writable:
                data = [[
                    [cellText("Session"), self.InteractiveTextbox("Session" + str(session.session_number), width=50)], 
                    [cellText("Date"), self.InteractiveTextbox("Date" + str(session.session_number), width=50)],
                    [cellText("Target"), self.InteractiveTextbox("Target" + str(session.session_number), width=50)],
                    [cellText("Actual"), self.InteractiveTextbox("Actual" + str(session.session_number), width=50)],
                    [cellText("Felt"), self.InteractiveTextbox("Felt" + str(session.session_number), width=50)],
                    [cellText("Notes"), self.InteractiveTextbox("Notes" + str(session.session_number), width=50)]
                ]]
                table = Table(data, spaceAfter=1, spaceBefore=1)
                table.setStyle(TableStyle([
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
                tables.append(table)
            else:
                #Height of 26 because it will always be double its desired height without the bottom one
                #TODO: Make height a pretty variable?
                data = [[
                    [cellText("Session", height=26)], 
                    [cellText("Date", height=26)],
                    [cellText("Target", height=26)],
                    [cellText("Actual", height=26)],
                    [cellText("Felt", height=26)],
                    [cellText("Notes", height=26)]
                ]]
                table = Table(data, spaceAfter=1, spaceBefore=1)
                table.setStyle(TableStyle([
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
                tables.append(table)
        
        #Middle header
        MIDDLE_HEIGHT = 60
        if fillable:
            total_columns = sum([int(draw_recovery), int(draw_cooldown), int(draw_warmup)])
            if total_columns != 0:
                each_width = TOTAL_WIDTH/total_columns
            data = [[]]
            if writable:
                if draw_recovery:
                    name = "Recovery Notes" #Becase I am EXCEPTIONALLY lazy
                    data[0].append([cellText(name),self.InteractiveTextbox(name + str(session.session_number), width=each_width, height=MIDDLE_HEIGHT)])
                if draw_warmup:
                    name = "Warmup" #Becase I am EXCEPTIONALLY lazy
                    data[0].append([cellText(name),self.InteractiveTextbox(name + str(session.session_number), width=each_width, height=MIDDLE_HEIGHT)])
                if draw_cooldown:
                    name = "Cooldown" #Becase I am EXCEPTIONALLY lazy
                    data[0].append([cellText(name),self.InteractiveTextbox(name + str(session.session_number), width=each_width, height=MIDDLE_HEIGHT)])
            else:
                SCALE_FACTOR = 1.3 #Shouldn't need to change
                if draw_recovery:
                    data[0].append(cellText("Recovery Notes", height=int(SCALE_FACTOR*MIDDLE_HEIGHT)))
                    #data[0].append(cellText("Recovery Notes" + ''.join(['\n' for i in range(0, int(MIDDLE_HEIGHT/13))])))
                if draw_warmup:
                    data[0].append(cellText("Warmup", height=int(SCALE_FACTOR*MIDDLE_HEIGHT)))
                if draw_cooldown:
                    data[0].append(cellText("Cooldown", height=int(SCALE_FACTOR*MIDDLE_HEIGHT)))
            if total_columns != 0:
                table = Table(data, spaceAfter=1, spaceBefore=1)
                table.setStyle(TableStyle([
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
                tables.append(table)
        
        #Now for each actual set
        if not fillable:
            for set in session.sets:
                tables.append(Paragraph(str(set) ,self.left_header_4))
        else:
            data = []
            if draw_RPE:
                data.append(["", "Assignment" , "Actual", "RPE", "Notes"])
            else:
                data.append(["", "Assignment" , "Actual", "Notes"])

            #Empy sets before
            if draw_empty_sets:
                index = 0
                for i in range(0, num_empty_sets_before):
                    index +=1
                    ##40 because -2
                    if writable:
                        if draw_RPE:
                            data.append([cellText("0." + str(index)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 9*mm),self.InteractiveTextbox("", 48*mm)])
                        else:
                            data.append([cellText("0." + str(index)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 69*mm)])
                    else:
                        if draw_RPE:
                            data.append([cellText("0." + str(index)), "", "", "",""])
                        else:
                            data.append([cellText("0." + str(index)), "", "", ""])
                        

            #Each assigned set
            index = 0
            for set in session.sets:
                index +=1
                internal_string = str(index) if not draw_empty_sets else "1." + str(index)
                if writable:
                    if draw_RPE:
                        data.append([cellText(str(internal_string)), cellText(str(set)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 9*mm),self.InteractiveTextbox("", 48*mm)])
                    else:
                        data.append([cellText(str(internal_string)), cellText(str(set)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 69*mm)])
                else:
                    if draw_RPE:
                        data.append([cellText(str(internal_string)), cellText(str(set)), "", "",""])
                    else:
                        data.append([cellText(str(internal_string)), cellText(str(set)), "", ""])

            #Empty sets after
            if draw_empty_sets:
                index = 0
                for i in range(0, num_empty_sets_after):
                    index +=1
                    if writable:
                        if draw_RPE:
                            data.append([cellText("2." + str(index)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 9*mm),self.InteractiveTextbox("", 48*mm)])
                        else:
                            data.append([cellText("2." + str(index)), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 40*mm), self.InteractiveTextbox("", 69*mm)])
                    else:
                        if draw_RPE:
                            data.append([cellText("2." + str(index)), "", "", "",""])
                        else:
                            data.append([cellText("2." + str(index)), "", "", ""])
            
            if draw_RPE:
                table = Table(data, colWidths=[10*mm, 42*mm, 42*mm, 11*mm, 50*mm])
            else:
                table = Table(data, colWidths=[10*mm, 42*mm, 42*mm, 61*mm])
            
            table.setStyle(TableStyle([
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
            tables.append(table)
            
        return tables
            


    def generate_session_header(self, session:lift_session, timestepped, forcetime, start_datetime) -> flowables:

        #TODO: clean this shit up

        #If we DO NOT want to add forcetime stuff
        if not forcetime:
            if timestepped:
                return Paragraph(str(session), self.left_header_3)
            else:
                return Paragraph("#" + str(session.session_number), self.left_header_3)
        else:
            session_week = session.get_session_week()
            pass#TODO:
            

    def get_combined_fig(self) -> Figure:
        #since each block has no awareness of the other ones we need to create a new figure in here
        fig = Figure(figsize = (10, 5), ##Size of 10,5 because we really only want combined graphs for a PDF
                        dpi = 500)

        x = []
        actual_intensity_arr = []
        weight_arr = []
        volume_arr = []
        i = 0

        for block in self.pril_program.get_blocks():
            for session in block.sessions:
                x.append(i)
                i+=1
                actual_intensity_arr.append(session.get_actual_intensity())
                weight_arr.append(session.get_weight())
                volume_arr.append(session.get_volume())

        plot1 = fig.add_subplot(311)

        #plot1.plot(actual_intensity_arr)
        plot1.plot(x, actual_intensity_arr, label = "Actual Intensity")
        ##TODO: Force integer to appear on x axis
        plot2 = fig.add_subplot(312)

        plot2.plot(x, weight_arr, label = "Weight")

        plot3 = fig.add_subplot(313)

        plot3.plot(x, volume_arr, label = "Volume")

        plot3.legend()
        plot2.legend()
        plot1.legend()
        return fig

    def generate_PNG(self, fig:Figure, path:str="temp/") -> str:
        """Generates a PNG in /temp of the requested figure

        Args:
            fig (Figure): figure input of matplotlib

        Returns:
            str: file name within specified directory
        """        
        def get_random_filename():
            return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

        fig.set_size_inches(7, 3)
        this_filename = get_random_filename()
        fig.savefig(path + this_filename + '.png')
        return path + this_filename + ".png"

    def get_png_as_flowble(self, path:str, width:int=500):
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))


    def generate_combined_graph(self) -> flowables:
        combined_figure = self.get_combined_fig()
        filepath = self.generate_PNG(combined_figure)
        return self.get_png_as_flowble(filepath)
        


    def generate_graph(self, phase:lift_block) -> flowables:
        figure = phase.get_as_figure()
        filepath = self.generate_PNG(figure)
        return self.get_png_as_flowble(filepath)
            

    def generate_header(self, phase:lift_block = None, notes:str = None) -> flowables:

        if phase == None and notes == None:
            return Paragraph(str(self.pril_program.lift_name.capitalize()))

        if phase == None and notes != None:
            return Paragraph(str(self.pril_program.lift_name.capitalize()) + " " + notes)

        if phase != None and notes == None:
            return [Paragraph(str(self.pril_program.lift_name.capitalize()) + " " + phase.phase_str(), self.center_header_1_bold)]

        if phase != None and notes != None:
            # print(self.pril_program.lift_name)
            return [Paragraph(str(self.pril_program.lift_name.capitalize()) + " " + phase.phase_str(), self.center_header_1_bold), Paragraph(notes, self.center_header_2)]
            




def timer(letter,start):
    print(letter,time.time()-start)
    return time.time()        

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

        session = lift_session(lift_name)
        for i in range(0,sets):
            session.add_set(lift_set(round(onerm_weight*(onerm_percent/100),1), reps, round(onerm_percent,1), round(actual_intensity,1)))
        
        return session

    def get_rep_sets(self, onerm, reps_per_set_lean_percent, total_reps_lean_percent, lean):
        '''
        Lean of 0 is optimal
        Lean of 0.2 is 20% more difficult of the delta between optimal reps and
        '''
        repset = {}
        with open("data/RepSets_two.csv") as csvfile:
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


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from lift_block import periodized_program

    pril_program = periodized_program(
        lift_name="deadlift",
        start_weight=265,
        end_weight=315,
        phases=3,
        percent_increase_arr=[3.5, 2, 1],
        frequency_per_week=3,
        gain_per_phase=[25, 15, 10],
        weekly_periodization_per_phase=[[0.0, 1.5, -0.5],[0.0, 1.5, -0.5],[0.0, 1.5, -0.5]],
        #weekly_periodization_per_phase=[[0.0, 0.25, -0.5]],
    )

    pril_pdf = pril_program.as_PDF()
    pril_pdf.generate_PDF("a",
         seperate_phases=False,
        notes="Aidan",
        draw_RPE=True,
        draw_warmup=True,
        draw_cooldown=True,
        fillable=True,
        draw_recovery=True,
        draw_summary=True,
        draw_graphs = True,
        timestepped = True,
        forcetime = False,
        writable=False,
        draw_empty_sets=True,
        num_empty_sets_before=3,
        num_empty_sets_after=2)