try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import sys
from tkinter import *
import tkinter

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.pyplot import plot, streamplot, text
from lift_block import periodized_program, pril_lift_block
from random import randint
from matplotlib.ticker import MaxNLocator

from tkinter import ttk

class lift_block_gui(tk.Frame):
    def __init__(self, master) -> None:
        self.MAX_PHASES = 5
        self.master = master
        self.frame = tk.Frame(self.master)
        
        master.title("Lift Generator")
        
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


        #PHASE GUI ELEMENTS
        self.phases = []
        for i in range(1, self.MAX_PHASES+1):
            self.phases.append(self.phase_GUI_element(last_row + i, i, self.master, self.desired_frequency))
        self.phase_scale_handler()
        self.pril_program = None


        columns = (
            ('Lifts', 50)
        )
        self.output_tree = ttk.Treeview(self.master, columns=[""])
        self.output_tree.grid(row = 3, column = 10, columnspan=100, rowspan=4, sticky="nsew")
        self.output_tree.column("", width=300, anchor=tk.CENTER)

        self.write_to_csv = Button(text="Write to CSV", command=self.write_csv)
        self.write_to_csv.grid(row=7, column=13)
        self.csv_filename_entry = Entry()
        self.csv_filename_entry.insert(0,"filename")
        self.csv_filename_entry.grid(row=7, column=14)

        self.all_set_bool_var = BooleanVar()
        self.csv_write_all_sets = Checkbutton(text="Row per set", variable=self.all_set_bool_var)
        self.csv_write_all_sets.grid(row=7, column=15)
        
        self.update_graph()

        self.phase_label = Label(textvariable=self.phase_label_var)
        self.phase_label.grid(row=2, column=6)

        self.prev_phase_plot = tk.Button(text="Prev Phase", command=self.prev_graph)
        self.prev_phase_plot.grid(row=2, column=5)
        self.next_phase_plot = tk.Button(text="Next Phase", command=self.next_graph)
        self.next_phase_plot.grid(row=2, column=7)
        

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

    def get_phase_as_figure(self, a):
        
        try:
            block = self.calculated_blocks[a]
            fig = Figure(figsize = (5, 5),
                        dpi = 100)

            x = []
            actual_intensity_arr = []
            weight_arr = []
            volume_arr = []
            i = 0
            for session in block.sessions:
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
            
        except IndexError:
            fig = Figure(figsize = (5, 5),
                        dpi = 100)
            y = [0 for i in range(1)]
            plot1 = fig.add_subplot(111)
            plot1.plot(y)
            return fig

    

    def update_graph(self):
        try:
            self.phase_label_var.set((self.calculated_blocks[self.current_graph_index].phase_str()))
        except:
            self.phase_label_var.set("Phase " + str(self.current_graph_index+1))


        # creating the Tkinter canvas
        # containing the Matplotlib figure
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
    
    
    def update_tree(self):
    
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
    if sys.argv[1] == 'D':
        app.debug()
    root.mainloop()

if __name__ == '__main__':
    main()