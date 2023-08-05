import tkinter
from tkinter import messagebox
import customtkinter
from tkinter import *
import heapq
from tkinter import filedialog
from time import sleep
import json
import socket
import select
from struct import pack
import time
import threading
from PIL import Image, ImageTk
import cv2
from DBOperations import DatabaseOperations
from datetime import datetime
from copy import copy, deepcopy
from customtkinter import CTkEntry as OriginalCTkEntry


user_name = 'user'
sock =None


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

# Grid size
GRID_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
resolution = 1
bot_len_X = 2 #feet
bot_len_Y = 2 #feet
# command = 'command'

resolution_factor = 1

# Screen size
WIDTH = GRID_SIZE * GRID_WIDTH
HEIGHT = GRID_SIZE * GRID_HEIGHT

grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
start_pos = None
end_pos = None
y_axis_min = 0
y_axis_max = 0
x_axis_min = 0
x_axis_max = 0 
obstacle_mode = False
pause=True

newMap_name = None
map_id = None
mode = "home"
map_data = None
dest_data = None
#cap = cv2.VideoCapture("http://10.0.10.236:8080/stream/video.mjpeg")

db_file_path = "agv.db"

#destination stuff
dest_color_array = ["brown1","purple", "cyan","brown","olive"]
dest_count = 0
destName = None
path_dest_names = []
path_list = []

class App(customtkinter.CTk):
       
    def __init__(self):
        super().__init__()
        
        #Create an instance of tkinter frame
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # configure window
        self.title("Autonomous Robot Navigator")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))

        #self.geometry(f"{1100}x{580}")

        #self.eval('tk::PlaceWindow . left')
        # configure grid layout (4x4)
        self.grid_columnconfigure((0,4), weight=0)
        self.grid_columnconfigure((1,2,3), weight=1)
        self.grid_rowconfigure((0), weight=1)

        #self.grid_rowconfigure(0, weight=1) # weights will tell if we need the column to grow or not on resize
        """
        
        Cofiguration display Tab
        
        """
      
        self.configuration_tab = customtkinter.CTkFrame(self, corner_radius=10)
        self.configuration_tab.grid(row=0, column=0, sticky="nwse", pady=10, padx = (10,0))
        self.configuration_tab.grid_rowconfigure((8,9), weight=1)
        self.configuration_tab.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=0)

        self.configuration_tab.grid_columnconfigure(0, weight=1)
        
        #elements inside configuration Tab START
        self.map_config_label = customtkinter.CTkLabel(self.configuration_tab, text="Configuration", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.map_config_label.grid(row=0, column=0, padx = 70,pady=(10, 5))
        
        self.navigate_tab = customtkinter.CTkFrame(self.configuration_tab, corner_radius=10)
        self.navigate_tab.grid(row=1, column=0, sticky="nwse", pady=10, padx = (10,10))
        self.navigate_tab.grid_rowconfigure((0,1,2,3), weight=1)
        self.navigate_tab.grid_columnconfigure((0,1,2), weight=1)
        
        self.button_connect = customtkinter.CTkButton(self.navigate_tab, text = "Connect",command=lambda:threading.Thread(target=self.start_connection).start())
        self.button_connect.grid(row=1, column=0, padx=5, pady=(20,5),columnspan = 3)
        
        self.button_map_collection = customtkinter.CTkOptionMenu(self.navigate_tab, values=["Select Map"], command=self.set_map)
        self.button_map_collection.grid(row=2, column=0, padx=5, pady=5, columnspan = 3)

        self.button_dest_collection = customtkinter.CTkOptionMenu(self.navigate_tab, values=["Select Destination"],command=self.set_destination_color_main)
        self.button_dest_collection.grid(row=3, column=1, sticky='w', padx = (10,0))
        
        self.main_dest_box_canvas = customtkinter.CTkCanvas(self.navigate_tab, width=50, height=50, bg="#333333", highlightthickness=0)
        self.main_dest_box_canvas.grid(row=3,column=0,sticky='e')

        box_width = 40
        box_height = 40
        # self.main_dest_box_canvas.create_rectangle(5, 5, box_width, box_height, fill="orange")  # Added a slight offset for the rectangle

        self.button_start = customtkinter.CTkButton(self.navigate_tab, text="Start")
        self.button_start.grid(row=5, column=0, padx=5, pady=5, columnspan = 3)
     
        self.tabview = customtkinter.CTkTabview(self.configuration_tab, height = 375)
        self.tabview.grid(row=7, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.tabview.add("Bot")
        self.tabview.add("Map")
        self.tabview.add("Path")
        self.tabview.add("   UI  ")
        self.tabview.tab("   UI  ").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Map").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Bot").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Path").grid_columnconfigure(0, weight=1)


        self.label_Device_id = customtkinter.CTkLabel(self.tabview.tab("Bot"), text="Device ID", anchor="w")
        self.label_Device_id.grid(row=1, column=0, padx=5, pady=(5, 0))
        self.dropdown_Device_id = customtkinter.CTkOptionMenu(self.tabview.tab("Bot"), values=["BNMITAGV1","BNMITAGV2","BNMITAGV3"])
        self.dropdown_Device_id.grid(row=1, column=1, padx=5, pady=(5,0))
        
        self.button_login = customtkinter.CTkButton(self.tabview.tab("Bot"), text="Forward",command=lambda m="FORWARD":threading.Thread(target=self.send_command,args=[m]).start())
        self.button_login.grid(row=2, column=0, sticky="news", pady=(20,5))
        self.button_login = customtkinter.CTkButton(self.tabview.tab("Bot"), text="Left",command=lambda m="LEFT":threading.Thread(target=self.send_command,args=[m]).start())
        self.button_login.grid(row=3, column=0, pady=(20,5))
        self.button_login = customtkinter.CTkButton(self.tabview.tab("Bot"), text="Right",command=lambda m="RIGHT":threading.Thread(target=self.send_command,args=[m]).start())
        self.button_login.grid(row=3, column=1,  pady=(20,5))
        self.button_login = customtkinter.CTkButton(self.tabview.tab("Bot"), text="Backward",command=lambda m="BACKWARD":threading.Thread(target=self.send_command,args=[m]).start())
        self.button_login.grid(row=2, column=1,  pady=(20,5))
        self.label_Duration = customtkinter.CTkLabel(self.tabview.tab("Bot"), text="Duration", anchor="w")
        self.label_Duration.grid(row=6, column=0,  pady=(20, 0))
        self.entry_Duration = customtkinter.CTkEntry(self.tabview.tab("Bot"), placeholder_text="milliseconds")
        self.entry_Duration.grid(row=6, column=1,  pady=(20, 0))
        self.label_speed = customtkinter.CTkLabel(self.tabview.tab("Bot"), text="Speed : 35 m/min", anchor="w")
        self.label_speed.grid(row=7, column=0, pady=(20, 0))
        # self.entry_speed = customtkinter.CTkEntry(self.tabview.tab("Bot"), placeholder_text="Speed")
        # self.entry_speed.grid(row=7, column=1, padx=5, pady=(5, 0))
        self.speed_slider = customtkinter.CTkSlider(self.tabview.tab("Bot"), from_=35, to=100, number_of_steps=13,command = self.print_speed)
        self.speed_slider.grid(row=7, column=1,  pady=(15, 0))
        self.speed_slider._set_dimensions(160,20)
        self.speed_slider.set(30)

        # self.button_print = customtkinter.CTkButton(self.tabview.tab("Bot"), text="Print",command=send_command, anchor="w")
        # self.button_print.grid(row=8, column=0, padx=5, pady=(20,5))
        self.button_addbot = customtkinter.CTkButton(self.tabview.tab("Bot"), text = "Add Bot")
        self.button_addbot.grid(row=8, column=0, columnspan = 2, padx=5, pady=(10,5), sticky="nsew")
         
        
        self.label_x_coordinate = customtkinter.CTkLabel(self.tabview.tab("Map"), text="Enter X Length:", anchor="w")
        self.label_x_coordinate.grid(row=0, column=0, padx=5, pady=(5, 0))
        self.entry_x_coordinate = customtkinter.CTkEntry(self.tabview.tab("Map"), placeholder_text="X Value")
        self.entry_x_coordinate.grid(row=0, column=1, padx=5, pady=(5, 0))

        self.label_y_coordinate = customtkinter.CTkLabel(self.tabview.tab("Map"), text="Enter Y Length:", anchor="w")
        self.label_y_coordinate.grid(row=1, column=0, padx=5, pady=(5, 0))
        self.entry_y_coordinate = customtkinter.CTkEntry(self.tabview.tab("Map"),placeholder_text="Y Value")
        self.entry_y_coordinate.grid(row=1, column=1, padx=5, pady=(5, 0))
        
        self.label_si_unit = customtkinter.CTkLabel(self.tabview.tab("Map"), text="Enter SI Unit:", anchor="w")
        self.label_si_unit.grid(row=2, column=0, padx=5, pady=(5, 0))
        self.dropdown_si_unit = customtkinter.CTkOptionMenu(self.tabview.tab("Map"), values=["Feet"])
        self.dropdown_si_unit.grid(row=2, column=1, padx=5, pady=5)
        
        self.label_xy_resolution = customtkinter.CTkLabel(self.tabview.tab("Map"), text="Enter Resolution:", anchor="w")
        self.label_xy_resolution.grid(row=3, column=0, padx=5, pady=(5, 0))
        self.dropdown_xy_resolution = customtkinter.CTkOptionMenu(self.tabview.tab("Map"), values=["1","0.5","0.25"],command=self.resize_grid_resolution)
        self.dropdown_xy_resolution.grid(row=3, column=1, padx=5, pady=5)
        
        self.button_addmap = customtkinter.CTkButton(self.tabview.tab("Map"), text = "New Map",  command=self.new_map_mode) # text should change to update map once if any map is opened
        self.button_addmap.grid(row=4, column=0, padx=5, pady=(10,10), sticky="nsew")
        
        self.button_refresh_map = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Refresh Grid", command=self.resize_grid_on_refresh)
        self.button_refresh_map.grid(row=4, column=1 ,padx=5, pady=(10,10), sticky="nsew")
        
        self.button_add_source = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Add Source", command=self.start_source_mode)
        self.button_add_source.grid(row=5, column=0, padx=5, pady=(5,10), sticky="nsew")
       
        self.button_add_obstacles = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Add Obstacle", command=self.start_obstacles_mode, state="disabled")
        self.button_add_obstacles.grid(row=5, column=1, padx=5, pady=(5,10), sticky="nsew")
        
        self.button_add_destination = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Add Dest "+str(dest_count +1), command=self.start_destination_mode, state="disabled")
        self.button_add_destination.grid(row=6, column=0, padx=5, pady=(5,10), sticky="nsew")
    
        self.button_close_map = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Close Map")
        self.button_close_map.grid(row=6, column=1, padx=5, pady=(5,10), sticky="nsew")
        
        self.button_move_up = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Move Up", command= self.move_up_clicked)
        self.button_move_up.grid(row=7, column=0, columnspan =2, padx=5, pady=(5,10))       
        self.button_move_left = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Move Left", command = self.move_left_clicked)
        self.button_move_left.grid(row=8, column=0, padx=5, pady=(5,10), sticky="nsew")       
        self.button_move_right = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Move Right", command = self.move_right_clicked)
        self.button_move_right.grid(row=8, column=1, padx=5, pady=(5,10), sticky="nsew")       
        self.button_move_down = customtkinter.CTkButton(self.tabview.tab("Map"), text = "Move Down", command = self.move_down_clicked)
        self.button_move_down.grid(row=9, column=0, columnspan =2, padx=5, pady=(5,10))
        
        #Path Tab
        
        self.path_dest_box_canvas = customtkinter.CTkCanvas(self.tabview.tab("Path"), width=40, height=40, bg="#ffffff", highlightthickness=0)
        self.path_dest_box_canvas.grid(row=0,column=0,sticky='e')
        
        self.path_dest_collection = customtkinter.CTkOptionMenu(self.tabview.tab("Path"), values=["Select Destination"],command=self.set_destination_color_path)
        self.path_dest_collection.grid(row=0, column=1, sticky='w', padx = (10,0))
        
        self.button_start_path = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Start Path", command= self.start_new_path)
        self.button_start_path.grid(row=1, column=0, columnspan =2, padx=5, pady=(5,10)) 
        
        self.button_revert_path = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Revert Path", command= self.revert_path)
        self.button_revert_path.grid(row=2, column=0, columnspan =2, padx=5, pady=(5,10))
        
        self.button_path_move_up = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Move Path Up", command= self.move_up_clicked)
        self.button_path_move_up.grid(row=3, column=0, columnspan =2, padx=5, pady=(25,10))       
        self.button_path_move_left = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Move Path Left", command = self.move_left_clicked)
        self.button_path_move_left.grid(row=4, column=0, padx=5, pady=(5,10), sticky="nsew")       
        self.button_path_move_right = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Move Path Right", command = self.move_right_clicked)
        self.button_path_move_right.grid(row=4, column=1, padx=5, pady=(5,10), sticky="nsew")       
        self.button_path_move_down = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Move Path Down", command = self.move_down_clicked)
        self.button_path_move_down.grid(row=5, column=0, columnspan =2, padx=5, pady=(5,10)) 
        
        self.button_save_path = customtkinter.CTkButton(self.tabview.tab("Path"), text = "Save Path",fg_color='#71c7ec', text_color = "#000000")
        self.button_save_path.grid(row=6, column=0, columnspan =2, padx=5, pady=(15,10))
        
        #UI Tab
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.tabview.tab("   UI  "), text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("   UI  "), values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))  
        self.scaling_label = customtkinter.CTkLabel(self.tabview.tab("   UI  "), text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("   UI  "), values=["80%", "90%", "100%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        self.button_update = customtkinter.CTkButton(self.configuration_tab,  height = 50,  fg_color='#ff0e0e', text_color = "#000000",  font=customtkinter.CTkFont(size=25, weight="bold"), text = "STOP",command=lambda m="STOP":threading.Thread(target=self.send_command,args=[m]).start())
        self.button_update.grid(row=8, column=0, padx=5, pady=(20,5))

        self.map_display_tab = customtkinter.CTkFrame(self, corner_radius=10)
        self.map_display_tab.grid(row=0, column=1, columnspan=3, sticky="nwse", pady=10, padx=(10, 0))
        self.map_display_tab.grid_rowconfigure((1, 2, 3, 4), weight=1)
        self.map_display_tab.grid_columnconfigure(0, weight=1)
        # self.map_display_tab.grid_columnconfigure(3, weight=1)

        # Elements inside MAP Tab END
        self.map_label = customtkinter.CTkLabel(self.map_display_tab, text="Home Screen", font=customtkinter.CTkFont(size=15, weight="bold"),anchor="w")
        self.map_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        
        self.dimen_label = customtkinter.CTkLabel(self.map_display_tab, text="Dimensions", font=customtkinter.CTkFont(size=12, weight="bold"),anchor="w")
        self.dimen_label.grid(row=0, column=1, padx=20, pady=(10, 0))
        
        self.map_display_grid_tab = customtkinter.CTkFrame(self.map_display_tab, corner_radius=10)
        self.map_display_grid_tab.grid(row=1, column=0, columnspan = 2, rowspan=4, sticky="news", pady=10, padx=(3, 3))

        self.canvas = tkinter.Canvas(self.map_display_grid_tab, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.y_scroll = tkinter.Scrollbar(self.map_display_grid_tab, orient='vertical', command=self.canvas.yview)
        self.y_scroll.grid(row=0, column=1, sticky='ns', pady=(0, GRID_SIZE))

        self.x_scroll = tkinter.Scrollbar(self.map_display_grid_tab, orient='horizontal', command=self.canvas.xview)
        self.x_scroll.grid(row=1, column=0, sticky='ew', padx=(0, GRID_SIZE))

        self.canvas.config(xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.map_display_grid_tab.rowconfigure(0, weight=1)
        self.map_display_grid_tab.columnconfigure(0, weight=1)

        self.frameDatabase = tkinter.Frame(self.canvas, bg='blue')
        self.frameDatabase.grid(row=0, column=0, sticky='news')

        self.map_display_grid_tab.grid_rowconfigure(0, weight=1)
        self.map_display_grid_tab.grid_columnconfigure(0, weight=1)
        # self.map_display_grid_tab.grid_columnconfigure(1, weight=1)
        # Bind the <Configure> event to the map_display_grid_tab widget
        self.map_display_grid_tab.bind("<Configure>", self.draw_grid)
        # self.map_display_status_tab = customtkinter.CTkFrame(self.map_display_tab, corner_radius=10)
        # self.map_display_status_tab.grid(row=5, column=0, rowspan=1, sticky="nwsee", pady=10, padx = (3,3))
        #elements inside MAP Tab EN
        """
        Bot display Tab
        """
        self.bot_display_tab = customtkinter.CTkFrame(self, corner_radius=10)
        self.bot_display_tab.grid(row=0, column=4, rowspan=1, sticky="nsew", pady=10, padx = (10,10))
        self.bot_display_tab.grid_rowconfigure(3, weight=0)
        self.bot_display_tab.grid_columnconfigure(0, weight=0)
        
        self.bot_label = customtkinter.CTkLabel(self.bot_display_tab, text="Bot Configuration", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.bot_label.grid(row=0, column=0, padx=140, pady=(20, 5))
        
        self.bot_display_tab = customtkinter.CTkScrollableFrame(self.bot_display_tab, label_text="Bot Status",  corner_radius=10)
        self.bot_display_tab.grid(row=5, column=0, rowspan=1, sticky="nwse", pady=20, padx = (3,3))
        self.bot_display_tab.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []        

        self.db_creation()
        self.get_existing_map_names()
        
        # =================== Camera Streaming =================== #
        # self.cameraFrame = customtkinter.CTkFrame(master=self.bot_label, width=950 )
        # self.cameraFrame.grid(row=7, column=0, sticky="nswe", padx=10, pady=10)
        # self.camera = customtkinter.CTkLabel(self.cameraFrame)
        # self.camera.grid()
            
    #Methods Start
    def db_creation(self):
                
        db_obj = DatabaseOperations(db_file_path)
        db_obj.create_connection()

        table1_name = "tbt_maps"
        columns1 = "map_id INTEGER PRIMARY KEY AUTOINCREMENT, map_name TEXT NOT NULL UNIQUE, x_value INTEGER, y_value INTEGER, grid_values  TEXT, units TEXT, resolution TEXT, created_by TEXT, created_dt DATE, updated_by TEXT,updated_dt DATE, remarks TEXT"
        db_obj.create_table_if_not_exists(table1_name, columns1)
        
        table2_name = "tbt_sources"
        columns2 = "source_id INTEGER PRIMARY KEY AUTOINCREMENT, source_name TEXT  NOT NULL , map_id INTEGER, position  TEXT, created_by TEXT, created_dt DATE, updated_by TEXT,updated_dt DATE, remarks TEXT, FOREIGN KEY (map_id) REFERENCES maps(map_id)"
        db_obj.create_table_if_not_exists(table2_name, columns2)

        table3_name = "tbt_destinations"
        columns3 = "dest_id INTEGER PRIMARY KEY  AUTOINCREMENT, dest_name TEXT NOT NULL , map_id INTEGER, position  TEXT, created_by TEXT, created_dt DATE, updated_by TEXT,updated_dt DATE, color TEXT, rotation INTEGER, remarks TEXT, FOREIGN KEY (map_id) REFERENCES maps(map_id)"
        db_obj.create_table_if_not_exists(table3_name, columns3)

        table4_name = "tbt_bots"
        columns4 = "bot_id INTEGER PRIMARY KEY AUTOINCREMENT, bot_name TEXT , dimen_x  INTEGER , dimen_y  INT, tolerance_x  INTEGER , tolerance_y  INTEGER , dimen_unit TEXT, tolerance_unit TEXT, remarks TEXT"
        db_obj.create_table_if_not_exists(table4_name, columns4)
       
        table5_name = "tbt_mst_config"
        columns5 = "config_id INTEGER  PRIMARY KEY AUTOINCREMENT, config_name TEXT NOT NULL UNIQUE, config_value  TEXT, created_by TEXT, created_dt DATE, updated_by TEXT,updated_dt DATE, remarks TEXT"
        db_obj.create_table_if_not_exists(table5_name, columns5)
        
        table6_name = "tbt_paths"
        columns6 = "path_id INTEGER PRIMARY KEY AUTOINCREMENT, map_id INTEGER,  path_to TEXT , path_value TEXT, created_by TEXT, created_dt DATE, updated_by TEXT, updated_dt DATE, remarks TEXT, FOREIGN KEY (map_id) REFERENCES maps(map_id)"
        db_obj.create_table_if_not_exists(table6_name, columns6)
        
        db_obj.close_connection()
        
        
    def start_new_path(self):
        global newMap_name
        print("start New Path")
        db_obj = DatabaseOperations(db_file_path)
        map_data = db_obj.get_map_data(newMap_name)
        #print(map_data)
        self.resize_grid_on_map_select(map_data)
        dest_data = db_obj.get_dest_data(newMap_name)
        print("Dest ",dest_data)
        self.set_destination_values(dest_data)
        self.populate_path_source()
        
        
    def populate_path_source(self):
        global y_axis_min,y_axis_max,x_axis_min,x_axis_max,mode
        db_obj = DatabaseOperations(db_file_path)
        source_pos = db_obj.get_source_data(newMap_name)
        print(source_pos)
        for row in source_pos:
            value = row[0] 
            y_value,x_value= value.split(":")
            y_axis_min,y_axis_max=y_value.split(",")
            x_axis_min,x_axis_max=x_value.split(",")
            x_axis_min = int(x_axis_min)
            x_axis_max = int(x_axis_max)
            y_axis_min = int(y_axis_min)
            y_axis_max = int(y_axis_max)
            print(y_axis_min," ", y_axis_max, " ",x_axis_min," ",x_axis_max)
            for col in range(int(y_axis_min),int(y_axis_max)):
                for row in range(int(x_axis_min),int(x_axis_max)): 
                    self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE, (row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE, fill="orange")
            self.update_map_header(newMap_name + " map : Mode - Path")
            mode = "path"

    def revert_path():
        print("")
        
    def get_existing_map_names(self):
        db_obj = DatabaseOperations(db_file_path)
        maps = db_obj.get_maps()
        map_names = []
        for row in maps:
            map_name = row[1] 
            map_names.append(map_name) 
        if len(map_names) > 0:
            self.button_map_collection.configure(values=map_names)

    #Open New Map Method
    def set_map(self, event: str):
        global mapName,map_data
        mapName = self.button_map_collection.get()
        db_obj = DatabaseOperations(db_file_path)
        map_data = db_obj.get_map_data(mapName)
        print(map_data)
        self.set_map_values(map_data)
        self.resize_grid_on_map_select(map_data)
        self.set_destination_dropdown()
        
    def set_destination_dropdown(self):
        global mapName, dest_data
        mapName = self.button_map_collection.get()
        db_obj = DatabaseOperations(db_file_path)
        print(mapName)
        dest_data = db_obj.get_dest_data(mapName)
        print("Dest ",dest_data)
        
        dest_names = []
        for row in dest_data:
            dest_name = row[0]+" : "+row[2]
            print(dest_name)
            dest_names.append(dest_name) 
            
        if len(dest_names) > 0:
            self.button_dest_collection.configure(values=dest_names)
        self.set_destination_values(dest_data)
        
    def new_map_mode(self):
        global mode, newMap_name
        if(self.button_addmap.cget("text") == "New Map"):
            res = messagebox.askquestion('Save Grid Size', 'Click Yes if GridSize, Unit and Resolution is fixed. Cannot be altered!')
            if res == 'yes':
                self.get_map_name()
        else:
            print("Save Map!")
    
    def get_map_name(self):
        global newMap_name,mode
        dialog = customtkinter.CTkInputDialog(text="Map Name :", title="Enter the Map Name")
        db_obj = DatabaseOperations(db_file_path)
        map_name = dialog.get_input()
        if(map_name and not db_obj.isDuplicateMapName(map_name)):
            newMap_name = map_name
            self.disable_grid_resize() 
            self.update_map_header(map_name + " map : Mode - none")
            self.save_empty_map()            
            #self.button_addmap.configure(text = "Update Map Grid")
            mode = "newMap"
        else:
            messagebox.showwarning('error', 'Map Name Exists!')
            mode = "home"
            newMap_name = None
            self.update_map_header("Home Screen")
            self.get_map_name()
            
    def start_source_mode(self):
        global mode
        if(self.button_add_source.cget("text") == "Add Source"):
            if(newMap_name is not None):
                self.populate_source()
                self.set_move_btn_names("Source")
                self.update_map_header(newMap_name + " map : Mode - Add Source")
                self.update_dimension_header("Top: 0 - Left : 0 - Right : "+str((GRID_WIDTH-x_axis_max)/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-y_axis_max)/resolution) +" ft")
                self.button_add_source.configure(text = "Save Source")
                mode = "addSource"
                    # elif res == 'no':
                    #     messagebox.showinfo('Response', 'Better to restart the software')
                    # else:
                    #     messagebox.showwarning('error', 'Better to restart the software')
            else:
                messagebox.showwarning('error', 'Add a new Map!')
        else:
            self.save_source()       
            
    def start_obstacles_mode(self):
        global mode
        if(self.button_add_obstacles.cget("text") == "Add Obstacle"):
            if(newMap_name is not None):
                self.update_map_header(newMap_name + " map : Mode - Add Obstacle")
                #self.update_dimension_header("Top: 0 - Left : 0 - Right : "+str((GRID_WIDTH-x_axis_max)/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-y_axis_max)/resolution) +" ft")
                self.button_add_obstacles.configure(text = "Save Obstacles")
                mode = "addObstacles"
            else:
                messagebox.showwarning('error', 'Add a new Map!')
        else:
            self.upgrade_map_grid()
            self.button_add_obstacles.configure(state="disabled")
            self.button_add_destination.configure(state="enabled")
    
    def start_destination_mode(self):
        global mode, dest_count
        if("Add Dest" in self.button_add_destination.cget("text")):
            if(newMap_name is not None):
                self.populate_destination()
                self.update_map_header(newMap_name + " map : Mode - Add Destination")
                self.button_add_destination.configure(text = "Save Dest "+str(dest_count+1))
                mode = "addDestination"
                self.button_move_up.configure(state="enabled")
                self.button_move_down.configure(state="enabled")
                self.button_move_right.configure(state="enabled")
                self.button_move_left.configure(state="enabled")
                self.set_move_btn_names("Dest")

            else:
                messagebox.showinfo('Issue', 'Please add new map')
        else:
            self.get_destination_name()
            
    def get_destination_name(self):
        global newMap_name,mode,destName
        dialog = customtkinter.CTkInputDialog(text="Destination Name :", title="Enter Destination Name")
        db_obj = DatabaseOperations(db_file_path)
        dest_name = dialog.get_input()
        if(dest_name and not db_obj.isDuplicateDestName(dest_name,map_id)):
            destName = dest_name
            self.save_desination()            
            mode = "newMap"
        else:
            messagebox.showwarning('error', 'Destination Name Exists!')
            destName = None
            self.get_destination_name()
    
    def populate_source(self):
        global y_axis_min,x_axis_min,y_axis_max,x_axis_max,grid
        y_axis_min = 0
        x_axis_min = 0
        y_axis_max = resolution*bot_len_Y
        x_axis_max = resolution*bot_len_X
        for y in range(x_axis_max):
            for x in range(y_axis_max):
                self.populate_grid(y,x,"Green")
                grid[x][y] = 1
                
    def populate_destination(self):
        global y_axis_min,x_axis_min,y_axis_max,x_axis_max,grid
        #print(grid)
        result = self.find_nearest_fit(grid, bot_len_X*resolution, bot_len_Y*resolution)
        if result is not None:
            y_axis_min, x_axis_min = result
            # print("Top-left corner coordinates of the object's bounding box:")
            # print("x_fit:", y_axis_min)
            # print("y_fit:", x_axis_min)
            y_axis_max = y_axis_min+((resolution*bot_len_Y))
            x_axis_max = x_axis_min+((resolution*bot_len_X))
            for y in range(x_axis_min,x_axis_max):
                for x in range(y_axis_min,y_axis_max):
                    self.populate_grid(y,x,dest_color_array[dest_count])
                    grid[x][y] = 2
            self.update_dimension_header("Top: "+str(y_axis_min/resolution)+" ft - Left : "+str(x_axis_min/resolution)+" ft - Right : "+str((GRID_WIDTH-x_axis_max)/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-y_axis_max)/resolution)+" ft")
        else:
            messagebox.showwarning('error', 'No place for destination!')
                
    def move_up_clicked(self):
        if(mode == "addSource"):
            self.move_bot("up","Green",1)
        elif(mode == "addDestination"):
            self.move_bot("up",dest_color_array[dest_count],2)
        elif(mode == "path"):
            self.move_path("up")
            
    def move_down_clicked(self):
        if(mode == "addSource"):
            self.move_bot("down","Green",1)
        elif(mode == "addDestination"):
            self.move_bot("down",dest_color_array[dest_count],2)
        elif(mode == "path"):
            self.move_path("down")
            
            
    def move_right_clicked(self):
        if(mode == "addSource"):
            self.move_bot("right","Green",1)
        elif(mode == "addDestination"):
            self.move_bot("right",dest_color_array[dest_count],2)
        elif(mode == "path"):
            self.move_path("right")
      
    def move_left_clicked(self):
        if(mode == "addSource"):
            self.move_bot("left","Green",1)
        elif(mode == "addDestination"):
            self.move_bot("left",dest_color_array[dest_count],2)
        elif(mode == "path"):
            self.move_path("left")
    
    def move_path(self, direction:str):
        global y_axis_min,x_axis_min,y_axis_max,x_axis_max,grid
        y_axis_min_old = y_axis_min
        y_axis_max_old = y_axis_max
        x_axis_min_old = x_axis_min
        x_axis_max_old = x_axis_max
        
        print("Before : x_min = ",x_axis_min," : x_max = ",x_axis_max," : y_min = ",y_axis_min," : y_max = ",y_axis_max)
        
        if(direction == "up"):
            if(y_axis_min>0):
                y_axis_min = y_axis_min-1
                y_axis_max = y_axis_max-1
            else:
                messagebox.showwarning('error', 'Cannot move UP anymore!')
        elif(direction == "down"):
            if(y_axis_max < GRID_HEIGHT):
                y_axis_min = y_axis_min+1
                y_axis_max = y_axis_max+1
            else:
                messagebox.showwarning('error', 'Cannot move DOWN anymore!')
        elif(direction == "right"):
            if(x_axis_max < GRID_WIDTH):
                x_axis_min = x_axis_min+1
                x_axis_max = x_axis_max+1
            else:
                messagebox.showwarning('error', 'Cannot move RIGHT anymore!')
        elif(direction == "left"):
            if(x_axis_min > 0):
                x_axis_min = x_axis_min-1
                x_axis_max = x_axis_max-1
            else:
                messagebox.showwarning('error', 'Cannot move LEFT anymore!')

        temp_grid = deepcopy(grid)
 
        print("GRID WIDTH = ",GRID_WIDTH,"  :  GRID HEIGHT = ",GRID_HEIGHT)
        print("x_min = ",x_axis_min," : x_max = ",x_axis_max," : y_min = ",y_axis_min," : y_max = ",y_axis_max)

        for y in range(x_axis_min_old,x_axis_max_old):
            for x in range(y_axis_min_old,y_axis_max_old):
                temp_grid[x][y] = 0
                
        # print("''''''")
        # print("GRID = ",grid)
        # print("TEMP_GRID = ",temp_grid)
        print("x_min_old = ",x_axis_min_old ," : x_max_old  = ",x_axis_max_old ," : y_min_old  = ",y_axis_min_old ," : y_max_old  = ",y_axis_max_old)
        
        if self.is_valid_path_move(temp_grid, x_axis_min,x_axis_max,y_axis_min,y_axis_max):
            temp_grid.clear()
            for y in range(x_axis_min_old,x_axis_max_old):
                for x in range(y_axis_min_old,y_axis_max_old):
                    if(grid[x][y] == 1):
                        self.populate_grid(y,x,"green")
                    elif(grid[x][y] == 2):
                        self.populate_grid(y,x,"red")
                    # elif(grid[x][y] == 4):
                    #      self.populate_grid(y,x,"white")

            for y in range(x_axis_min,x_axis_max):
                for x in range(y_axis_min,y_axis_max):
                    if(grid[x][y] == 2):
                        self.populate_grid(y,x,"midnightblue")
                    else:
                        self.populate_grid(y,x,"yellow1")
                        grid[x][y] = 4
                        self.update_dimension_header("Top: "+str(y_axis_min/resolution)+" ft - Left : "+str(x_axis_min/resolution)+" ft - Right : "+str((GRID_WIDTH-x_axis_max)/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-y_axis_max)/resolution)+" ft")
            #print("Post Update = ",grid)
        else:
            messagebox.showwarning('error', 'Cannot move due to source/Obstacle!')
            temp_grid.clear()
            y_axis_min = y_axis_min_old
            y_axis_max = y_axis_max_old
            x_axis_min = x_axis_min_old
            x_axis_max = x_axis_max_old
    
          
    def move_bot(self, direction:str, color:str, weight:int):
        global y_axis_min,x_axis_min,y_axis_max,x_axis_max,grid
        y_axis_min_old = y_axis_min
        y_axis_max_old = y_axis_max
        x_axis_min_old = x_axis_min
        x_axis_max_old = x_axis_max
        
        if(direction == "up"):
            if(y_axis_min>0):
                y_axis_min = y_axis_min-1
                y_axis_max = y_axis_max-1
            else:
                messagebox.showwarning('error', 'Cannot move UP anymore!')
        elif(direction == "down"):
            if(y_axis_max < GRID_HEIGHT):
                y_axis_min = y_axis_min+1
                y_axis_max = y_axis_max+1
            else:
                messagebox.showwarning('error', 'Cannot move DOWN anymore!')
        elif(direction == "right"):
            if(x_axis_max < GRID_WIDTH):
                x_axis_min = x_axis_min+1
                x_axis_max = x_axis_max+1
            else:
                messagebox.showwarning('error', 'Cannot move RIGHT anymore!')
        elif(direction == "left"):
            if(x_axis_min > 0):
                x_axis_min = x_axis_min-1
                x_axis_max = x_axis_max-1
            else:
                messagebox.showwarning('error', 'Cannot move LEFT anymore!')

        temp_grid = deepcopy(grid)
 
        
        for y in range(x_axis_min_old,x_axis_max_old):
            for x in range(y_axis_min_old,y_axis_max_old):
                temp_grid[x][y] = 0
                
        # print("''''''")
        # print("GRID = ",grid)
        # print("TEMP_GRID = ",temp_grid)
        # print("x_min = ",x_axis_min," : x_max = ",x_axis_max," : y_min = ",y_axis_min," : y_max = ",y_axis_max)
        # print("x_min_old = ",x_axis_min_old ," : x_max_old  = ",x_axis_max_old ," : y_min_old  = ",y_axis_min_old ," : y_max_old  = ",y_axis_max_old)
        
        if self.is_valid_move(temp_grid, x_axis_min,x_axis_max,y_axis_min,y_axis_max):
            temp_grid.clear()
            for y in range(x_axis_min_old,x_axis_max_old):
                for x in range(y_axis_min_old,y_axis_max_old):
                    self.populate_grid(y,x,"White")
                    grid[x][y] = 0
            for y in range(x_axis_min,x_axis_max):
                for x in range(y_axis_min,y_axis_max):
                    self.populate_grid(y,x,color)
                    grid[x][y] = weight
            self.update_dimension_header("Top: "+str(y_axis_min/resolution)+" ft - Left : "+str(x_axis_min/resolution)+" ft - Right : "+str((GRID_WIDTH-x_axis_max)/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-y_axis_max)/resolution)+" ft")
            #print("Post Update = ",grid)
        else:
            messagebox.showwarning('error', 'Cannot move due to source/Obstacle!')
            temp_grid.clear()
            y_axis_min = y_axis_min_old
            y_axis_max = y_axis_max_old
            x_axis_min = x_axis_min_old
            x_axis_max = x_axis_max_old

    def disable_grid_resize(self):
        self.button_refresh_map.configure(state="disabled")
        self.dropdown_si_unit.configure(state="disabled")
        self.dropdown_xy_resolution.configure(state="disabled")
        self.entry_x_coordinate.configure(state="disabled")
        self.entry_y_coordinate.configure(state="disabled")
        self.button_addmap.configure(state = "disabled")
        
    def set_map_items_state(self, condition:str):
        self.button_refresh_map.configure(state=condition)
        self.dropdown_si_unit.configure(state=condition)
        self.dropdown_xy_resolution.configure(state=condition)
        self.entry_x_coordinate.configure(state=condition)
        self.entry_y_coordinate.configure(state=condition)
        self.button_addmap.configure(state=condition)
        self.button_add_source.configure(state = condition)
        self.button_add_destination.configure(state = condition)
        self.button_add_obstacles.configure(state = condition)
        self.button_move_up.configure(state = condition)
        self.button_move_down.configure(state = condition)
        self.button_move_right.configure(state = condition)
        self.button_move_left.configure(state = condition)
        self.button_close_map.configure(state = condition)
    
    def set_map_values(self, data):
        global resolution_factor, GRID_WIDTH, GRID_HEIGHT
        self.set_map_items_state("normal")
        
        for map_data in data:       
            self.entry_x_coordinate.delete(0, tkinter.END)  # Remove the placeholder text
            self.entry_x_coordinate.insert(0, map_data[2])
            self.entry_y_coordinate.delete(0, tkinter.END)  # Remove the placeholder text
            self.entry_y_coordinate.insert(0, map_data[3])        
            self.dropdown_si_unit.set(map_data[5])
            self.dropdown_xy_resolution.set(map_data[6])
            self.set_map_items_state("disabled")
            print(self.entry_x_coordinate.get())

            resolution_factor = float(map_data[6])
            GRID_WIDTH =int(map_data[2])
            GRID_HEIGHT = int(map_data[3])
            
    def set_destination_color_main(self, event: str):
        global mapName
        mapName = self.button_map_collection.get()
        dest_name = self.button_dest_collection.get()
        db_obj = DatabaseOperations(db_file_path)
        dest_data = db_obj.get_dest_data(mapName)
        
        for row in dest_data:
            if(row[0]==dest_name.split(" : ")[0]):
                self.main_dest_box_canvas.create_rectangle(5, 5, 40, 40, fill=row[2])  # Added a slight offset for the rectangle
                
    def set_destination_color_path(self, event: str):
        global mapName
        dest_name = self.path_dest_collection.get()
        self.path_dest_box_canvas.create_rectangle(0, 0, 40, 40, fill=dest_name.split(" : ")[1])  # Added a slight offset for the rectangle
                

    def set_destination_values(self,dest_data):
        print("Set destination values")
        for row in dest_data:
            dest_name = row[1]
            color = row[2]
            
            x_value,y_value= dest_name.split(":")
            y_axis_min,y_axis_max=y_value.split(",")
            x_axis_min,x_axis_max=x_value.split(",")
            print(y_axis_min," ", y_axis_max, " ",x_axis_min," ",x_axis_max)
            for row in range(int(y_axis_min),int(y_axis_max)):
                for col in range(int(x_axis_min),int(x_axis_max)): 
                    self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE, (row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE, fill=color)
        
    def set_move_btn_names(self,name:str):
        self.button_move_up .configure(text="Move "+name+" Up")
        self.button_move_left .configure(text="Move "+name+" Left")
        self.button_move_right .configure(text="Move "+name+" Right")
        self.button_move_down .configure(text="Move "+name+" Down")
        
    def save_empty_map(self):
        global map_id
        table_name = "tbt_maps"
        columns = ["map_name","x_value","y_value","grid_values","units","resolution","created_by","created_dt","updated_by","updated_dt","remarks"]  # List of column names in the order of insertion
        data_to_insert = [newMap_name, (int(GRID_WIDTH)/resolution), (int(GRID_HEIGHT)/resolution), str(grid), str(self.dropdown_si_unit.get()), str(self.dropdown_xy_resolution.get()), user_name,   datetime.today(),user_name,  datetime.today(),'No Remarks']  # Use datetime.today() to get today's date
        db_obj = DatabaseOperations(db_file_path)
        map_id = db_obj.insert_data_into_table(table_name, columns, data=data_to_insert)
        
    def save_source(self):
        table_name = "tbt_sources"
        columns = ["source_name","map_id","position","created_by","created_dt","updated_by","updated_dt","remarks"]  # List of column names in the order of insertion
        data_to_insert = [newMap_name+"_source", map_id, (str(y_axis_min)+","+str(y_axis_max)+":"+str(x_axis_min)+","+str(x_axis_max)), user_name,   datetime.today(), user_name, datetime.today(),'No Remarks']  # Use datetime.today() to get today's date
        db_obj = DatabaseOperations(db_file_path)
        source_id = db_obj.insert_data_into_table(table_name, columns, data=data_to_insert)
        self.upgrade_map_grid()
        self.button_add_source.configure(state="disabled")
        self.button_move_up.configure(state="disabled")
        self.button_move_down.configure(state="disabled")
        self.button_move_right.configure(state="disabled")
        self.button_move_left.configure(state="disabled")
        self.button_add_obstacles.configure(state="enabled")
        
    def save_desination(self):
        global dest_count  
        table_name = "tbt_destinations"
        columns = ["dest_name","map_id","position","created_by","created_dt","updated_by","updated_dt","rotation","color","remarks"]  # List of column names in the order of insertion
        data_to_insert = [destName, map_id, (str(y_axis_min)+","+str(y_axis_max)+":"+str(x_axis_min)+","+str(x_axis_max)), user_name,   datetime.today(), user_name, datetime.today(),0,str(dest_color_array[dest_count]),"No Remark"]  # Use datetime.today() to get today's date
        db_obj = DatabaseOperations(db_file_path)
        dest_id = db_obj.insert_data_into_table(table_name, columns, data=data_to_insert)
        self.upgrade_map_grid()
        dest_count = dest_count+1
        self.button_add_destination.configure(text="Add Dest "+str(dest_count+1))
        self.update_path_destination_list(destName, str(dest_color_array[dest_count-1]))
    
    def update_path_destination_list(self, dest_name:str, color: str):
        print("Updating path destination List,")
        global path_dest_names
        dest_name = dest_name+" : "+color
        print(dest_name)
        path_dest_names.append(dest_name) 
    
        if len(path_dest_names) > 0:
            self.path_dest_collection.configure(values=path_dest_names)
        

    def upgrade_map_grid(self):
        global map_id
       # print("GRID to update = ",grid)
        table_name = "tbt_maps"
        column_name_to_update = "grid_values" 
        new_value_to_set = str(grid)
        condition = "map_id = ?"
        condition_params = (map_id,)
        db_obj = DatabaseOperations(db_file_path)
        db_obj.update_data(table_name, column_name_to_update, new_value_to_set, condition, condition_params)

    def draw_grid(self,event):
        canvas_width = GRID_WIDTH * GRID_SIZE
        canvas_height = GRID_HEIGHT * GRID_SIZE
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self.canvas.delete("grid_line")  # Clear previous grid lines
        # Draw the vertical grid lines
        for x in range(0, canvas_width+1, GRID_SIZE):
            self.canvas.create_line(x, 0, x, canvas_height, fill="black", tags="grid_line")
        # Draw the horizontal grid lines
        for y in range(0, canvas_height+1, GRID_SIZE):
            self.canvas.create_line(0, y, canvas_width, y, fill="black", tags="grid_line")
    
    def resize_draw_grid(self, width: int, height: int):
        canvas_width = width * GRID_SIZE
        canvas_height = height * GRID_SIZE
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self.canvas.delete("grid_line")  # Clear previous grid lines
        # Draw the vertical grid lines
        for x in range(0, canvas_width+1, GRID_SIZE):
            self.canvas.create_line(x, 0, x, canvas_height, fill="black", tags="grid_line")
        # Draw the horizontal grid lines
        for y in range(0, canvas_height+1, GRID_SIZE):
            self.canvas.create_line(0, y, canvas_width, y, fill="black", tags="grid_line")

    def resize_grid_on_refresh(self):
        new_width = self.entry_x_coordinate.get()
        new_height = self.entry_y_coordinate.get()
        factor = self.dropdown_xy_resolution.get()
        global resolution, GRID_WIDTH, GRID_HEIGHT
        # if new_width and new_height:
        try:
            if(float(factor) == 0.5):
                resolution = 2
            elif(float(factor) == 0.25):
                resolution = 4
            
            if new_width and new_height:
                GRID_WIDTH = int(new_width) * resolution
                GRID_HEIGHT = int(new_height) * resolution
            else:
                GRID_WIDTH = GRID_WIDTH * resolution
                GRID_HEIGHT = GRID_HEIGHT * resolution
            
            if GRID_WIDTH > 0 and GRID_HEIGHT > 0:
                self.canvas.config(width=GRID_WIDTH, height=GRID_HEIGHT)
                # Reset the grid and redraw
                self.initialize_grid(GRID_WIDTH,GRID_HEIGHT)
                print("Resize_Draw_grid_on_refresh width = ",GRID_WIDTH," : Height = ",GRID_HEIGHT)
                self.resize_draw_grid(GRID_WIDTH,GRID_HEIGHT)
                # Update the window layout
                self.update_idletasks()
                self.geometry(f"{GRID_WIDTH}x{GRID_HEIGHT}")
            else:
                messagebox.showerror("Invalid Grid Size", "Please enter positive values for width and height.")
        except ValueError:
            messagebox.showerror("Invalid Grid Size", "Please enter valid integer values for width and height.")
       
    def resize_grid_on_map_select(self,map_data):
        
        global resolution_factor, GRID_HEIGHT, GRID_WIDTH
        resolution=1
        try:
            if(float(resolution_factor) == 0.5):
                resolution = 2
            elif(float(resolution_factor) == 0.25):
                resolution = 4
            print("width = ",GRID_WIDTH," : Height = ",GRID_HEIGHT)

            GRID_WIDTH = int(GRID_WIDTH) * resolution
            GRID_HEIGHT = int(GRID_HEIGHT) * resolution
            
            
            if GRID_WIDTH > 0 and GRID_HEIGHT > 0:
                
                self.canvas.config(width=GRID_WIDTH, height=GRID_HEIGHT)
                # Reset the grid and redraw
                self.initialize_grid(GRID_WIDTH,GRID_HEIGHT)
                print("Resize_Draw_grid_on_refresh width = ",GRID_WIDTH," : Height = ",GRID_HEIGHT)
                self.resize_draw_grid(GRID_WIDTH,GRID_HEIGHT)
                # Update the window layout
                self.update_idletasks()
                self.geometry(f"{GRID_WIDTH}x{GRID_HEIGHT}")
            else:
                messagebox.showerror("Invalid Grid Size", "Please enter positive values for width and height.")
                
            self.populate_grid_on_map_select(map_data)
        except ValueError:
            messagebox.showerror("Invalid Grid Size", "Please enter valid integer values for width and height.")
            
    def convert_string_to_2d_matrix(self,input_string,width):
    # Remove the square brackets and split the string by comma and newline characters
        values = input_string.replace('[', '').replace(']', '').replace('\n', '').split(',')

        # Convert the extracted values to integers and group them into rows
        num_cols = width  # Assuming the matrix has a fixed size of 16x16 as per the given input string
        matrix = [int(val) for val in values]
        num_rows = len(matrix) // num_cols

        # Reshape the list into a 2D matrix
        matrix = [matrix[i:i+num_cols] for i in range(0, len(matrix), num_cols)]

        return matrix

    def populate_grid_on_map_select(self,map_data):
        global grid
        grid.clear()
        print(GRID_WIDTH," ",GRID_HEIGHT)
        for mapdata in map_data:
            
            grid= self.convert_string_to_2d_matrix(mapdata[4],GRID_WIDTH)
            #print(grid)
            for row in range(GRID_WIDTH):
                for col in range(GRID_HEIGHT):
                    color = "WHITE"
                    if grid[col][row] == 1:
                        color = "GREEN"
                    elif grid[col][row] == 3:
                        color = "Gray"
                    self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE, (row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE, fill=color,)
        
    def resize_grid_resolution(self, event: str):
        new_width = self.entry_x_coordinate.get()
        new_height = self.entry_y_coordinate.get()
        factor = self.dropdown_xy_resolution.get()
        global resolution, GRID_WIDTH, GRID_HEIGHT
        try:
            if(float(factor) == 0.5):
                resolution = 2
            elif(float(factor) == 0.25):
                resolution = 4
            elif(float(factor) == 1):
                resolution = 1
                
            if new_width and new_height:
                GRID_WIDTH = int(new_width) * resolution
                GRID_HEIGHT = int(new_height) * resolution
            else:
                GRID_WIDTH = GRID_WIDTH * resolution
                GRID_HEIGHT = GRID_HEIGHT * resolution

            if GRID_WIDTH > 0 and GRID_HEIGHT > 0:
                self.canvas.config(width=GRID_WIDTH, height=GRID_HEIGHT)
                # Reset the grid and redraw
                self.initialize_grid(GRID_WIDTH,GRID_HEIGHT)
                self.resize_draw_grid(GRID_WIDTH,GRID_HEIGHT)
                # Update the window layout
                self.update_idletasks()
                self.geometry(f"{GRID_WIDTH}x{GRID_HEIGHT}")
            else:
                messagebox.showerror("Invalid Grid Size", "Please enter positive values for width and height.")
        except ValueError:
            messagebox.showerror("Invalid Grid Size", "Please enter valid integer values for width and height.")
       
    # Mouse click event handler
    def on_canvas_click(self,event):
        global start_pos, end_pos, grid
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        row = int(x // GRID_SIZE)
        col = int(y // GRID_SIZE)
        #print(str(row)+","+str(col))
        
        if mode == "addObstacles":
            if grid[col][row] == 0:
                grid[col][row] = 3
                self.canvas.create_rectangle( row * GRID_SIZE,col * GRID_SIZE, (row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE, fill="gray")

            elif grid[col][row] == 3:
                grid[col][row] = 0
                self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE, (row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE, fill="white")
            self.update_dimension_header("Top: "+str(row/resolution)+" ft - Left : "+str(col/resolution)+" ft - Right : "+str((GRID_WIDTH-(col+1))/resolution)+" ft - Bottom : "+str((GRID_HEIGHT-(row+1))/resolution)+" ft")
            #self.draw_grid()
        
    def populate_grid(self, row: int, col: int, color: str):
        self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE,(row + 1) * GRID_SIZE, (col + 1) * GRID_SIZE,fill=color)

    # Draw the grid on the canvas
    def draw_grid_path(self):
        self.canvas.delete("all")
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                color = "WHITE"
                if grid[row][col] == 1:
                    color = "GREEN"
                elif grid[row][col] == 2:
                    color = "RED"
                elif grid[row][col] == -1:
                    color = "BLUE"
                elif grid[row][col] == -2:
                    color = "YELLOW"
                self.canvas.create_rectangle(row * GRID_SIZE, col * GRID_SIZE, (row + 1) * GRID_SIZE,(col + 1) * GRID_SIZE, fill=color,)
    
    # Initialize the grid with default values
    def initialize_grid(self,new_width: int,new_height: int):
        global grid        
        grid = []
        for i in range(new_height):
            row = []
            for j in range(new_width):
                row.append(0)
            grid.append(row)
    
        print("initialize  GRID LENGTH X = ",len(grid[0]))
        print("initialize  GRID LENGTH y = ",len(grid))

    def print_speed(self,event):
        self.label_speed.configure(text="Speed : "+str(self.speed_slider.get())+" m/min")
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def dijstras(self,start, end):
        print("DIJSTRAS")
        # Create a priority queue for the open set
        open_set = []
        # Create a dictionary to keep track of the previous nodes
        prev = {}
       # print("list1")
        # Create a dictionary to store the cost of reaching each node (initialize with infinity)
        cost = {}
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                cost[(row, col)] = float('inf')
        #print("list12")
        # Set the cost of the start node to 0
        cost[start] = 0
        # Add the start node to the open set with a priority of 0
        heapq.heappush(# The above code is declaring a variable named "open_set" in Python.
        open_set, (0, start))
        # Run the algorithm until the open set is empty
        while open_set:
            # Pop the node with the lowest priority from the open set
            current_cost, current_node = heapq.heappop(open_set)
            # Check if the current node is the end node
            if current_node == end:
                # Build the path by following the previous nodes
                path = []
                #print("list1278")
                while current_node in prev:
                    #print("list178")
                    path.append(current_node)
                    current_node = prev[current_node]
                path.append(start)
                path.reverse()
                return path
            # Get neighboring nodes
           # print("list15")
            neighbors = self.get_neighbors(current_node)
           # print("list14")
            # Iterate over the neighbors
            for neighbor in neighbors:
                neighbor_row, neighbor_col = neighbor
                # Calculate the tentative cost to reach the neighbor node
                tentative_cost = cost[current_node] + 1
                # Check if the tentative cost is lower than the current cost of the neighbor
                if tentative_cost < cost[neighbor]:
                    # Update the cost of the neighbor
                    cost[neighbor] = tentative_cost
                    # Set the previous node of the neighbor to the current node
                    prev[neighbor] = current_node
                    # Add the neighbor to the open set with the updated priority
                    heapq.heappush(open_set, (tentative_cost, neighbor))
        # No path found
        #print("list13")
        return []
    
    # Get neighboring nodes
    def get_neighbors(self,node):
        row, col = node
        neighbors = []
        if row > 0 and grid[row - 1][col] != -1:
            neighbors.append((row - 1, col))
        if row < GRID_HEIGHT - 1 and grid[row + 1][col] != -1:
            neighbors.append((row + 1, col))
        if col > 0 and grid[row][col - 1] != -1:
            neighbors.append((row, col - 1))
        if col < GRID_WIDTH - 1 and grid[row][col + 1] != -1:
            neighbors.append((row, col + 1))
        return neighbors
    
    def on_find_path_click(self):
        global start_pos, end_pos
        if start_pos and end_pos:
            path = self.dijstras(start_pos, end_pos)
            if path:
                for node in path:
                    row, col = node
                    if grid[row][col] == 0:
                        grid[row][col] = -2
                self.draw_grid_path()
            else:
                messagebox.showinfo("No Path Found", "There is no valid path between the start and end positions.")
        else:
            messagebox.showinfo("Missing Positions", "Please set both the start and end positions.")
            
    def update_map_header(self, heading: str):
        self.map_label.configure(text=heading)
    
    def update_dimension_header(self, heading: str):
        self.dimen_label.configure(text=heading)
  
    def streaming(self):
        ret, img = cap.read()
        cv2image= cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        ImgTks = ImageTk.PhotoImage(image=img)
        self.camera.imgtk = ImgTks
        self.camera.configure(image=ImgTks)
        self.after(20, self.streaming) 
         
    def is_valid_placement(self, grid, x, y, obj_size_x, obj_size_y):
        for i in range(obj_size_x):
            for j in range(obj_size_y):
                if grid[x + i][y + j] != 0:
                    return False
        return True
    
    def is_valid_move(self, grid, x1,x2,y1,y2):
        # print("valid move GRID LENGTH X = ",len(grid[0]))
        # print("valid move GRID LENGTH Y = ",len(grid))
        # print("valid move GRID = ",grid)
        
        for i in range(y1,y2):
            for j in range(x1,x2):
                #print("valid move i = ",i, " : j = ",j)
                if grid[i][j] != 0:
                    return False
        #print("''''''")
        return True
    
    def is_valid_path_move(self, grid, x1,x2,y1,y2):
        # print("valid move GRID LENGTH X = ",len(grid[0]))
        # print("valid move GRID LENGTH Y = ",len(grid))
        # print("valid move GRID = ",grid)
        for i in range(y1,y2):
            for j in range(x1,x2):
                #print("valid move i = ",i, " : j = ",j)
                if not(grid[i][j] == 0 or grid[i][j] == 1  or grid[i][j] == 2):
                    return False
        #print("''''''")
        return True

    def find_nearest_fit(self, grid, obj_size_x, obj_size_y):
        grid_width = len(grid)
        grid_height = len(grid[0])

        for x in range(grid_width - obj_size_x + 1):
            for y in range(grid_height - obj_size_y + 1):
                if self.is_valid_placement(grid, x, y, obj_size_x, obj_size_y):
                    return x, y
        return None
    
    def start_connection(self):
        global sock
        print("connecting")
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('192.168.1.8', 8)
            sock.connect(server_address)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("Socket connected")
            messagebox.showinfo("Connected","Connected")
            label = customtkinter.CTkLabel(self.bot_display_tab, text="Connected")
            #label.grid(row=App.send.counter, column=0, padx=20, pady=(0))
        else:
            print("Using existing connection")
            messagebox.showerror("Unable to Connect", "Please try again.")

            
    def send_command(self,direction):
        global sock
        
        #App.send_command.counter+=1
        # print(direction)

        if self.speed_slider.get()=="":
            speed=0
        else:
            speed=self.speed_slider.get()

        if self.entry_Duration.get()=="":
            parameter=0
        else:
            parameter=self.entry_Duration.get()
        
        if direction=='STOP':
            speed=0
            parameter=0
        print("Device ID",self.dropdown_Device_id.get(),"Speed= ",speed , "Parameters=",0)
        data=(self.dropdown_Device_id.get()+"_"+direction+"_"+str(parameter)+"_"+str(int(speed)))
        self.send(data)
        

    
    def send(self,data):
        global sock
        #App.send.counter+=1
        try:
            # Send data
            if sock is None:
                print("No connection")
                self.start_connection()
                
            sent_data = data
            print('sending ',(data))
            sock.sendall( bytes( data, encoding="utf-8" ) )
            label = customtkinter.CTkLabel(self.bot_display_tab, text=f"Sent data:{sent_data}")
            #label.grid(row=App.send.counter, column=0, padx=20, pady=(0))
            # self.scrollable_frame_switches.append(label)
            
            #recv data

            data = sock.recv(32)
            received_data=data.decode("utf-8")
            #  print('received',received_data)
            label = customtkinter.CTkLabel(self.bot_display_tab, text=f"{received_data}")
            #label.grid(row=App.send.counter+1, column=0, padx=20, pady=(0))
            # self.scrollable_frame_switches.append(label)
            #App.send.counter=App.send.counter+1    
        
        
        
        finally:
            print('done')
            # sock.close() 
            


    def close_connection(self):
        global sock
        if sock is not None:
            sock.close()
            sock = None
            print("Socket closed")       

if __name__ == "__main__":
    app = App()
  # app.state('zoomed')  # Maximize the window after mainloop
  # app.streaming()
    
    app.mainloop()  