import numpy as np
from tkinter import *
from tkinter import ttk

#WINDOW_SIZE="1600x900"
WINDOW_SIZE = "1280x720"


class Spinbox(ttk.Entry):

    def __init__(self, master=None, **kw):

        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)

    def set(self, value):
        self.tk.call(self._w, "set", value)


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.grid(row=0, column=0, sticky=N+S+E+W)
        self.rows = 10
        self.columns = 6
        for i in range(self.rows):
            self.rowconfigure(i, weight=1)

        for i in range(self.columns):
            self.columnconfigure(i, weight=1)

        self.create_widgets()
        self.lines_drawn = False
        self.events = []
        self.previous_process = -1
        self.current_circle = -1
        self.currently_drawn_vectors = []

    def create_widgets(self):
        # Number of processes label  0 0
        self.n_processes_label = Label(self, text="Number of Processes")
        self.n_processes_label.grid(row=0, column=0, sticky=N+S+E+W)

        # Number of processes spinbox 1 0
        self.N_PROCESSES_var = StringVar()
        self.N_PROCESSES_var.set(3)

        self.n_processes_spinbox = Spinbox(self, values=list(range(2, 11)),
                                           state="readonly", textvariable=self.N_PROCESSES_var,
                                           command=self.stop_highlight)
        self.n_processes_spinbox.grid(row=1, column=0, sticky=N)

        # Draw
        self.draw_button = Button(self, text="Draw",
                                  command=self.initialize_canvas)
        self.draw_button.grid(row=0, column=1, rowspan=2)

        # Currently adding label 0 1
        self.currently_adding = Label(self, text="Currently adding:")
        self.currently_adding.grid(row=0, column=2, rowspan=2, sticky=E)

        self.adding_modes = [("Local event", "L"),
                             ("Message", "M")]

        self.adding_mode = StringVar()
        self.adding_mode.set("L")

        # Local even radiobutton 0 2
        self.local_event_radiobutton = Radiobutton(self,
                                                   text="Local event",
                                                   variable=self.adding_mode,
                                                   value="L")
        self.local_event_radiobutton.grid(row=0, column=3, sticky=S+W)

        # Message radiobutton 1 2
        self.message_event_radiobutton = Radiobutton(self,
                                                     text="Message",
                                                     variable=self.adding_mode,
                                                     value="M")
        self.message_event_radiobutton.grid(row=1, column=3, sticky=N+W)

        # Done adding/Calculate timestamps/
        self.calculate_button = Button(self, text="Calculate\nTimestamps",
                                       command=self.draw_timestamps)
        self.calculate_button.grid(row=0, column=4, rowspan=2)

        # Clear button 0 5
        self.clear_button = Button(self, text="CLEAR", fg="red",
                                   command=self.clear_canvas)
        self.clear_button.grid(row=0, column=5, rowspan=2)

        # Canvas
        self.canvas = Canvas(self, bg="white")
        self.canvas.grid(row=2, column=0, rowspan=self.rows-2,
                         columnspan=self.columns, sticky=N+S+E+W)

        self.canvas.bind("<ButtonPress>", self.on_click)
        self.canvas.bind("<ButtonRelease>", self.on_release)

    def on_click(self, event):
        x, y = event.x, event.y

        #No lines have been drawn
        if not self.lines_drawn:
            return
        # Out of range
        if x < 40 or x > self.canvas.winfo_width()-50:
            return

        # Event ("L", x, process_number)
        if self.adding_mode.get() == "L":
            process_number = self.find_closest(y)
            self.create_rhombus(x, self.heights[process_number])

            self.events.append(("L", x, process_number))

        # Event ("M", from_x, to_x, from, to)
        if self.adding_mode.get() == "M":
            process_number = self.find_closest(y)
            self.current_circle = self.create_circle(
                x, self.heights[process_number])
            self.previous_process = process_number
            self.previous_x = x

    def on_release(self, event):
        x, y = event.x, event.y
        if x < 40 or x > self.canvas.winfo_width()-50:
            return
        if self.adding_mode.get() == "M":
            process_number = self.find_closest(y)

            if process_number == self.previous_process or x < self.previous_x:
                self.canvas.delete(self.current_circle)
                return

            self.create_circle(x, self.heights[process_number])
            self.canvas.create_line(self.previous_x, self.heights[self.previous_process],
                                    x, self.heights[process_number], arrow=LAST, width=2)
            self.events.append(
                ("M", self.previous_x, x, self.previous_process, process_number))

            self.previous_x = 0
            self.previous_process = -1
            self.current_circle = -1

    def create_rhombus(self, x, y):
        size = 20

        self.canvas.create_polygon(x, y-size/2,
                                   x+size/2, y,
                                   x, y+size/2,
                                   x-size/2, y,
                                   fill="black")

    def create_circle(self, x, y):
        radius = 10

        return self.canvas.create_oval(x-radius,
                                       y-radius,
                                       x+radius,
                                       y+radius,
                                       fill="gray")

    # Given height, returns the height closest to it
    def find_closest(self, y):
        best_index = -1
        best_distance = 10000
        for i, h in enumerate(self.heights):
            distance = abs(h-y)
            if distance < best_distance:
                best_index = i
                best_distance = distance
        return best_index

    def stop_highlight(self):
        self.n_processes_spinbox.selection_clear()

    # Clears canvas
    def clear_canvas(self):
        self.canvas.delete("all")
        self.events = []
        self.lines_drawn = False
        self.currently_drawn_vectors = []

    # Draw lines and whatever else to start plotting
    def initialize_canvas(self):
        self.clear_canvas()

        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()

        self.N_PROCESSES = int(self.N_PROCESSES_var.get())
        gap_size = height/(self.N_PROCESSES+1)

        self.heights = [gap_size*(1+i) for i in range(self.N_PROCESSES)]

        for i, height in enumerate(self.heights):
            self.canvas.create_line(40, height, width-40, height,
                                    arrow=LAST, width=3)
            self.canvas.create_text(20, gap_size*(1+i),
                                    text="p"+str(i))
        self.lines_drawn = True

    # Calculates the timestamps and returns it somehow

    def calculate_timestamps(self):
        # Event ("L", x, process_number)
        # Event ("M", from_previous_x, to_x, from previous process, to )
        # ->
        # ("L", x, process_number)
        # ("S", x, process_number, msg_num)
        # ("R", x, process_number, msg_num)
        counter = 0

        split_events = []
        for event in self.events:
            if event[0] == "M":
                split_events.append(("S", event[1], event[3], counter))
                split_events.append(("R", event[2], event[4], counter))
                counter += 1
            else:
                split_events.append(event)

        sorted_events = sorted(split_events, key=lambda x: x[1])

        messages = {}
        current_vectors = np.zeros(
            (self.N_PROCESSES, self.N_PROCESSES), dtype=np.uint8)
        # Output #(x, process_number, timestamp)
        timestamps = []
        send_vector = []

        for event in sorted_events:
            event_type, x, process_number = event[0], event[1], event[2]
            new_vector = []

            if event_type == "L":
                current_vectors[process_number, process_number] += 1
                new_vector = list(current_vectors[process_number])
            elif event_type == "S":
                current_vectors[process_number, process_number] += 1
                messages[event[3]] = current_vectors[process_number,process_number]
                new_vector = list(current_vectors[process_number])
                send_vector = list(current_vectors[process_number])
            else:
                current_vectors[process_number, process_number] += 1
                receive_vector=list(current_vectors[process_number])
                new_vector = [
                    max(send_vector[0],receive_vector[0]),
                    max(send_vector[1],receive_vector[1]),
                    max(send_vector[2],receive_vector[2])
                ]
                current_vectors[process_number]=new_vector
            timestamps.append((x, process_number, new_vector))

        return timestamps

    # Takes calculated timestamps and draws them
    def draw_timestamps(self):
        self.clear_timestamps()
        timestamps = self.calculate_timestamps()
        self.currently_drawn_vectors = []

        for timestamp in timestamps:
            x, process_number, vector = timestamp
            self.currently_drawn_vectors.append(
                self.canvas.create_text(x, self.heights[process_number]-20, text=repr(vector), font=("Purisa", 15), fill="red"))

    def clear_timestamps(self):
        for item in self.currently_drawn_vectors:
            self.canvas.delete(item)
        self.currently_drawn_vectors = []


root = Tk()
root.title('Vector Clock')
root.geometry(WINDOW_SIZE)
root.resizable(0, 0)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

app = Application(master=root)
app.mainloop()
