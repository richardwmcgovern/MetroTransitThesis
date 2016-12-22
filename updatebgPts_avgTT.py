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
arcpy.MakeFeatureLayer_management(r"metroFinal_FD\bgPts_final", "bgPtsFinal_lyr")

# Store avg_tt's in bgPts_final
oC = arcpy.da.SearchCursor("origins_lyr", ["ORIG_FID", "AVG_TT"])
origfid_tt_dict = {}
for row in oC:
    origfid_tt_dict[row[0]] = row[1]
del row
del oC
bgC = arcpy.da.UpdateCursor(r"H:\metroFinal.gdb\metroFinal_FD\bgPts_final", ["ORIG_FID", "AVG_TT"])
for row in bgC:
    row[1] = origfid_tt_dict[row[0]]
    bgC.updateRow(row)
del row
del bgC


