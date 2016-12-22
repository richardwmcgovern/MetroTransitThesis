import arcpy, math
from arcpy import env
from array import array
import sqlite3, shutil, time

workspace = "H:\\metroFinal.gdb"
env.workspace = workspace
env.overwriteOutput = True

arcpy.CheckOutExtension("Network")

# Make TTM layers
arcpy.MakeFeatureLayer_management(r"H:\metroFinal.gdb\TravelTimeMatrix_origins", "origins_lyr")
arcpy.MakeFeatureLayer_management(r"H:\metroFinal.gdb\TravelTimeMatrix_destinations", "destinations_lyr")
arcpy.MakeFeatureLayer_management(r"H:\metroFinal.gdb\TravelTimeMatrix_lines", "lines_lyr")

# Other layers
# bgPtsFinal_lyr
arcpy.MakeFeatureLayer_management(r"metroFinal_FD\bgPts_final", "bgPtsFinal_lyr")

# Try loading origins_lyr and destinations_lyr into an NA layer
# .. nah

# Plan: Iterate over each route in RT_LIST!

# Build the master route list
MASTER_RT_LIST = [] # list of string route numbers
bgC = arcpy.da.SearchCursor("bgPtsFinal_lyr", ["RT_LIST"])
for row in bgC:
    if row[0] != "":
        rtlist = row[0].split(",")
        for rt in rtlist:
            if rt not in MASTER_RT_LIST:
                MASTER_RT_LIST.append(rt)
    
del row
del bgC



# Connect to sql table
#finalSql = "H:\\metroFinal.gdb\\GTFS.sql"
#conn = sqlite3.connect(finalSql)
