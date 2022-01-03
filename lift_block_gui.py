try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import sys
from tkinter import *
import tkinter
import os

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.pyplot import plot, streamplot, text
from lift_block import periodized_program, pril_lift_block
from random import randint, triangular
from matplotlib.ticker import MaxNLocator

from tkinter import ttk

class lift_block_gui(tk.Frame):
    def __init__(self, master) -> None:
        self.MAX_PHASES = 5
        self.master = master
        self.frame = tk.Frame(self.master)
        
        master.title("Lift Generator")
        
        '''
        Buttons for UI
        '''
        self.lift_name_label = tk.Label(master, text="Lift Name")
        self.lift_name_entry = tk.Entry(master, width=15)

        self.lift_name_label.grid(row=0, column=0, sticky=W, pady=2)
        self.lift_name_entry.grid(row=0,column=1, sticky=W, pady=2)

        self.lift_start_weight = tk.Label(master, text="Start Weight")
        self.lift_start_entry = tk.Entry(master, width=15)

        self.lift_start_weight.grid(row=1, column=0, sticky=W, pady=2)
        self.lift_start_entry.grid(row=1,column=1, sticky=W, pady=2)

        self.lift_end_weight = tk.Label(master, text="End Weight")
        self.lift_end_entry = tk.Entry(master, width=15)

        self.lift_end_weight.grid(row=2, column=0, sticky=W, pady=2)
        self.lift_end_entry.grid(row=2,column=1, sticky=W, pady=2)

        self.desired_frequency = IntVar()
        self.frequency_label = tk.Label(master, text="Frequency")
        self.frequency_counter = Scale(master, from_=1 ,to=7, orient=HORIZONTAL,
            variable= self.desired_frequency, command=self.phase_scale_handler)

        self.frequency_label.grid(row=4, column=0, sticky=W, pady=2)
        self.frequency_counter.grid(row=4,column=1, sticky=W, pady=2)

        self.desired_phases = IntVar()
        self.phase_label = tk.Label(master, text="Phases")
        self.phase_counter = Scale(master, from_=1, to=self.MAX_PHASES, orient=HORIZONTAL,
            variable=self.desired_phases, command=self.phase_scale_handler)

        self.calculate_button = tk.Button(master, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=6, column = 0)

        self.phase_label.grid(row=5, column=0, sticky=W, pady=2)
        self.phase_counter.grid(row=5,column=1, sticky=W, pady=2)
        last_row = 5



        ##RENDERING OF GRAPHS - UP TO 2 TIMES THE MAX AMOUNT OF PHASES
        self.current_graph_index = 0
        self.phase_label_var = StringVar()
        self.calculated_blocks = []

        self.phase_label = Label(textvariable=self.phase_label_var)
        self.phase_label.grid(row=2, column=6)

        self.prev_phase_plot = tk.Button(text="Prev Phase", command=self.prev_graph)
        self.prev_phase_plot.grid(row=2, column=5)
        self.next_phase_plot = tk.Button(text="Next Phase", command=self.next_graph)
        self.next_phase_plot.grid(row=2, column=7)
        


        #PHASE GUI ELEMENTS
        self.phases = []
        for i in range(1, self.MAX_PHASES+1):
            self.phases.append(self.phase_GUI_element(last_row + i, i, self.master, self.desired_frequency))
        self.phase_scale_handler()
        self.pril_program = None

        #Leftmost output pane
        self.output_tree = ttk.Treeview(self.master, columns=[""])
        self.output_tree.grid(row = 3, column = 10, columnspan=100, rowspan=4, sticky="nsew")
        self.output_tree.column("", width=300, anchor=tk.CENTER)

        #Write to CSV buttons
        self.write_to_csv = Button(text="Write to CSV", command=self.write_csv)
        self.write_to_csv.grid(row=7, column=13)
        self.csv_filename_entry = Entry()
        self.csv_filename_entry.insert(0,"filename")
        self.csv_filename_entry.grid(row=7, column=14)

        self.all_set_bool_var = BooleanVar()
        self.csv_write_all_sets = Checkbutton(text="Row per set", variable=self.all_set_bool_var)
        self.csv_write_all_sets.grid(row=7, column=15)

        #Generate PDF buttons
        '''
           X pril_pdf.generate_PDF("a",      Filename w/o PDF
           X seperate_phases=False,          Each phase in a seperate PDF #TODO:
            notes="Hello",                  Notes for the phase - not required #TODO:
           X draw_RPE=True,                  Draw RPE y/n - required, no default, should assign here deafult to True
           X draw_warmup=True,               Draw warmup - required, no default, should assign here default to True
           X draw_cooldown=True,             Draw cooldown - required, no default, should assign here default to True
           X fillable=True,                  Y: nice fillable table, F: simply just list the assigned sets
           X draw_recovery=True,             Draw recovery - required, no default, should assign here default to True
           X draw_summary=True,              Draw summary at the top - required, no default, should assign here default to True
           X draw_graphs = True,             Draw graphs at the top - required, no default, should assign here default to True
           X timestepped = True,             Draw weeks or only session numbers - required, no default, should assign here to default to True
           X forcetime = False,              #TODO: Not yet implemented
           X writable=False,                 Insert textboxes - required, no default, should assign to FALSE
           X draw_empty_sets=False,          Draw empty before/after 'buffer' sets, no default, should assign to TRUE
            num_empty_sets_before=3,        Draw n empty sets before, should assign to 2        STATE DEPENDENT ON draw_empty_sets
            num_empty_sets_after=3)         Draw n empty sets AFTER, should assign to 2         STATE DEPENDENT ON draw_empty_sets
        '''

        self.pdf_generate_button = Button(text="Write PDF", command=self.generate_PDF)
        self.pdf_generate_button.grid(row=8, column=13)

        self.pdf_output_name = Entry()
        self.pdf_output_name.insert(0,"filename")
        self.pdf_output_name.grid(row=8, column=14)

        self.drawSeperateBool = BooleanVar()
        self.drawSeperate_checkbox = Checkbutton(text="Separate Phases", variable=self.drawSeperateBool)
        self.drawSeperate_checkbox.grid(row=8, column=15)
        self.drawSeperate_checkbox.config(state=DISABLED)

        self.drawRPEBool = BooleanVar()
        self.drawRPE_checkbox = Checkbutton(text="Draw RPE", variable=self.drawRPEBool)
        self.drawRPE_checkbox.grid(row=9, column=13)

        self.drawWarmupBool = BooleanVar()
        self.drawWarmup_checkbox = Checkbutton(text="Draw Warmup", variable=self.drawWarmupBool)
        self.drawWarmup_checkbox.grid(row=9, column=13)

        self.drawCooldownBool = BooleanVar()
        self.drawCooldown_checkbox = Checkbutton(text="Draw Cooldown", variable=self.drawCooldownBool)
        self.drawCooldown_checkbox.grid(row=9, column=14)

        self.drawRecoveryBool = BooleanVar()
        self.drawRecovery_checkbox = Checkbutton(text="Draw Recovery", variable=self.drawRecoveryBool)
        self.drawRecovery_checkbox.grid(row=9, column=15)

        self.fillableBool = BooleanVar()
        self.fillable_checkbox = Checkbutton(text="Fillable", variable=self.fillableBool)
        self.fillable_checkbox.grid(row=10, column=13)

        self.summaryBool = BooleanVar()
        self.summary_checkbox = Checkbutton(text="Draw Summary", variable=self.summaryBool)
        self.summary_checkbox.grid(row=10, column=14)

        self.graphsBool = BooleanVar()
        self.graphs_checkbox = Checkbutton(text="Draw Graphs", variable=self.graphsBool)
        self.graphs_checkbox.grid(row=10, column=15)

        self.timesteppedBool = BooleanVar()
        self.timestepped_checkbox = Checkbutton(text="Timestepped", variable=self.timesteppedBool)
        self.timestepped_checkbox.grid(row=11, column=13)

        self.forcetimeBool = BooleanVar()
        self.forcetime_checkbox = Checkbutton(text="Forcetime", variable=self.forcetimeBool)
        self.forcetime_checkbox.grid(row=11, column=14)
        self.forcetime_checkbox.config(state=DISABLED)

        self.writableBool = BooleanVar()
        self.writable_checkbox = Checkbutton(text="Writable", variable=self.writableBool)
        self.writable_checkbox.grid(row=11, column=15)

        Label(text="# Before").grid(row=12, column=14)
        Label(text="# After").grid(row=12, column=15)



        self.emptySetsBool = BooleanVar()
        self.emptySets_checkbox = Checkbutton(text="Draw Empty Sets", variable=self.emptySetsBool, command=self.update_emptysets)
        self.emptySets_checkbox.grid(row=13, column=13)

        options = [str(i) for i in range(1, 9)]

        self.sets_after_str = StringVar()
        self.sets_after_str.set("1")
        self.after_dropdown = OptionMenu(self.master ,self.sets_after_str ,*options)
        self.after_dropdown.grid(row=13, column=14)


        self.sets_before_str = StringVar()
        self.sets_before_str.set("1")
        self.before_dropdown = OptionMenu(self.master, self.sets_before_str ,*options)
        self.before_dropdown.grid(row=13, column=15)

        self.update_button = tk.Button(master, text="Update", command=self.update)
        self.update_button.grid(row=11, column = 0)
        self.update_button.config(state=DISABLED)

        #Defaults for all that
        self.drawSeperateBool.set(False)
        self.drawRPEBool.set(True)
        self.drawWarmupBool.set(True)
        self.drawCooldownBool.set(True)
        self.drawRecoveryBool.set(True)
        self.fillableBool.set(True)
        self.summaryBool.set(True)
        self.graphsBool.set(True)
        self.timesteppedBool.set(True)
        self.forcetimeBool.set(False)
        self.writableBool.set(False)
        self.emptySetsBool.set(True)

        ##Foprce self update of graph
        self.update_graph()
        self.update_emptysets()

    def update(self):
        pass

    def generate_PDF(self):
        try:
            pril_pdf = self.pril_program.as_PDF()
        except AttributeError:
            self.popup("Pleasae generate a program first")
            return
        pril_pdf.generate_PDF(self.pdf_output_name.get(),
            seperate_phases=self.drawSeperateBool.get(),
            notes=None, #TODO:
            draw_RPE=self.drawRPEBool.get(),
            draw_warmup=self.drawWarmupBool.get(),
            draw_cooldown=self.drawCooldownBool.get(),
            fillable=self.fillableBool.get(),
            draw_recovery=self.drawRecoveryBool.get(),
            draw_summary=self.summaryBool.get(),
            draw_graphs = self.graphsBool.get(),
            timestepped = self.timesteppedBool.get(),
            forcetime = self.forcetimeBool.get(),
            writable=self.writableBool.get(),
            draw_empty_sets=self.emptySetsBool.get(),
            num_empty_sets_before=int(self.sets_before_str.get()),
            num_empty_sets_after=int(self.sets_after_str.get()))
        self.popup("PDF generated!")
        

    def update_emptysets(self):
        if self.emptySetsBool.get() == False:
            self.before_dropdown.config(state=DISABLED)
            self.after_dropdown.config(state=DISABLED)
        else:
            self.before_dropdown.config(state=NORMAL)
            self.after_dropdown.config(state=NORMAL)

            

    def debug(self):
        self.lift_name_entry.insert(0,"Deadlift")
        self.lift_start_entry.insert(0,"195")
        self.lift_end_entry.insert(0,"225")
        self.frequency_counter.set(3)
        self.desired_frequency.set(3)
        self.phases[0].set_default()

    def write_csv(self):
        if self.pril_program == None:
            self.popup("No program has been generated yet")
        else:
            self.pril_program.as_csv(filename=self.csv_filename_entry.get().replace(".csv","")+".csv", seperate_sets=self.all_set_bool_var.get())
            self.popup("Done writing to CSV")

    def next_graph(self):
        if self.current_graph_index >= (2 * self.desired_phases.get())-1:
            return
        self.current_graph_index += 1
        self.update_graph()


    def prev_graph(self):
        if self.current_graph_index <= 0:
            return
        self.current_graph_index -= 1
        self.update_graph()

    def get_phase_as_figure(self, graph_index:int):
        try:
            block = self.calculated_blocks[graph_index] ##This line should throw the error
            #TODO: Clear the array after each new calculate
            return block.get_as_figure()
        
        #If we haven't calculated data for that phase or if we try to render
        # a graph out of bounds (which shouldn't happen)
        except IndexError:
            fig = Figure(figsize = (5, 5),
                        dpi = 100)
            y = [0 for i in range(1)]
            plot1 = fig.add_subplot(111)
            plot1.plot(y)
            return fig


    

    def update_graph(self):
        """Sets two output variables 
            current_graph and phase_label_var
        """        
        ##Set the title of the graphs to the current graph index
        try:
            self.phase_label_var.set((self.calculated_blocks[self.current_graph_index].phase_str()))
        except:
            self.phase_label_var.set("Phase " + str(self.current_graph_index+1))

        ##Set the current graph
        self.current_graph = FigureCanvasTkAgg(self.get_phase_as_figure(self.current_graph_index),
                                master = self.master)  
    
        

        self.current_graph.draw()
        self.current_graph.get_tk_widget().grid(row=3, column=3, columnspan=7)

    def plot(self):
        pass

    def phase_scale_handler(self, e=None):
        value = self.desired_phases.get()
        
        counter = 0
        for phase_obj in self.phases:
            if counter > value-1:
                phase_obj.set_disabled()
            else:
                phase_obj.set_enabled()
            counter +=1
        
        if self.current_graph_index >= (2 * self.desired_phases.get())-1:
            self.current_graph_index = 2 * self.desired_phases.get() - 1
            self.update_graph()
        
    def popup(self,message):
        win = Toplevel()
        win.wm_title(message)

        l = Label(win, text=message)
        l.grid(row=0, column=0)

        b = Button(win, text="Okay", command=win.destroy)
        b.grid(row=1, column=0)


    def calculate(self):
        try:
            #TODO: Update all phases with the calculated blocks
            if self.all_data_provided() == True:

                phase = self.phases[0]

                print(phase.get_weight_gain())
                print(phase.get_increase())
                print(phase.get_periodization())


                self.pril_program = periodized_program(
                lift_name=self.lift_name_entry.get(),
                start_weight=float(self.lift_start_entry.get()),
                end_weight=float(self.lift_end_entry.get()),
                phases=self.desired_phases.get(),
                frequency_per_week=self.desired_frequency.get(),

                percent_increase_arr=[self.phases[i].get_increase() for i in range(0,self.desired_phases.get())],
                gain_per_phase=[ self.phases[i].get_weight_gain() for i in range(0,self.desired_phases.get()) ],
                weekly_periodization_per_phase=[self.phases[i].get_periodization() for i in range(0,self.desired_phases.get())],
                )

                blocks = self.pril_program.get_blocks()
                for block in blocks:
                    print(block)
                self.calculated_blocks = blocks
                self.update_graph()
                self.update_tree()
                    

            else:
                self.popup(self.all_data_provided())
        except Exception as e:
            self.popup(str(e))
    
    
    def update_tree(self):
        for item in self.output_tree.get_children():
            self.output_tree.delete(item)
    
        for block in self.pril_program.get_blocks():
            self.output_tree.insert("", index="end",iid=block.phase_str(), text=block.phase_str())
            for session in block.sessions:
                self.output_tree.insert(block.phase_str(), index="end", iid = session.session_string(), text=session.session_string())
                for set in session.sets:
                    self.output_tree.insert(session.session_string(), index="end", text=str(set))

                   
        



    def all_data_provided(self):
        if self.lift_name_entry.get() == "":
            return "Must provide a Lift Name"
        
        if self.lift_start_entry.get() == "":
            return "Must provide a starting weight"

        if self.lift_end_entry.get() == "":
            return "Must provide an ending weight"
        
        try:
            float(self.lift_start_entry.get())
        except:
            return "Starting weight is not a number"

        try:
            float(self.lift_end_entry.get())
        except:
            return "Ending weight is not a number"
        
        for phase in self.phases:
            if phase.isComplete() != True:
                return "Phase " + str(phase.i) + " is not complete: " + phase.isComplete()

        return True


    

    class phase_GUI_element():
        def __init__(self, row, i, master, frequency_var) -> None:
            self.row = row
            self.master = master
            self.i = i
            self.frequency_var = frequency_var

            self.isEnabled = True
            
            self.lbl = tk.Label(master,text=str(i))
            self.lbl.grid(row=row, column=1)

            self.incrm = tk.Label(master,text="% Increase/week")
            self.incrm.grid(row=row, column=2)
            self.incrm_in = tk.Entry(master,width=3)
            self.incrm_in.grid(row=row, column=3)

            self.wgt = tk.Label(master,text="+weight")
            self.wgt.grid(row=row, column=4)
            self.wgt_in = tk.Entry(master,width=5)
            self.wgt_in.grid(row=row, column=5)

            self.prd = tk.Label(master,text="periodization")
            self.prd.grid(row=row, column=6)

            self.periodization_frame = tk.Frame(master)
            self.periodizations = []
            for i in range(0,7):
                prd_in = tk.Entry(self.periodization_frame, width=3)
                prd_in.pack(side=LEFT)
                self.periodizations.append(prd_in)
           
            self.periodization_frame.grid(row=row, column=7)

            self.elements = [self.lbl, self.incrm, self.incrm_in, self.wgt, self.wgt_in, self.prd]
            self.input_elements = [self.incrm_in, self.wgt_in]
        
        def set_default(self):
            self.incrm_in.insert(0, "3.5")
            self.wgt_in.insert(0,"30")
            self.periodizations[0].insert(0,"0")
            self.periodizations[1].insert(0,"0.5")
            self.periodizations[2].insert(0,"-0.5")


        def set_enabled(self):
            for element in self.elements:
                element.config(state=NORMAL)
            
            counter = 1
            for element in self.periodizations:
                if counter <= self.frequency_var.get():
                    element.config(state=NORMAL) 
                else:
                    element.config(state=DISABLED)
                counter +=1
            
            self.isEnabled = True

        def set_disabled(self):
            for element in self.elements:
                element.config(state=DISABLED)
            
            for element in self.periodizations:
                element.config(state=DISABLED)
            
            self.isEnabled = False
        
        def isEnalbed(self):
            return self.isEnabled

        def isComplete(self):
            for element in self.input_elements:
                if element['state'] == 'normal':
                    if element.get() == "":
                        return "Empty input in phase " + str(self.i)
                    try:
                        float(element.get())
                    except:
                        return "Non-number input in phase " + str(self.i)
            
            for element in self.periodizations:
                if element['state'] == 'normal':
                    if element.get() == "":
                        return "Empty input in periodization for phase " + str(self.i)
                    try:
                        float(element.get())
                    except:
                        return "Non-number input in periodization for phase " + str(self.i)

            return True

        def get_weight_gain(self):
            return float(self.wgt_in.get())
        def get_increase(self):
            return float(self.incrm_in.get())
        def get_periodization(self):
            returnable = []
            for element in self.periodizations:
                if element['state'] == 'normal':
                    returnable.append(float(element.get()))

            return returnable







        



def main(): 
    root = tk.Tk()
    app = lift_block_gui(root)
    if len(sys.argv) > 1 and sys.argv[1] == 'D':
        app.debug()
    root.mainloop()

if __name__ == '__main__':
    #updater_agent = auto_update()
    #updater_agent.update()
    main()
