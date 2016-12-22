 

import arcpy, math
from arcpy import env
import sqlite3, shutil, time

workspace = "H:\\metroFinal.gdb"
env.workspace = workspace
env.overwriteOutput = True

arcpy.CheckOutExtension("Network")

# Layers
#'bgPtsFinal_lyr'
arcpy.MakeFeatureLayer_management(r"metroFinal_FD\bgPts_final", "bgPtsFinal_lyr")
#'bgPtsZoneQuarterM_lyr'
arcpy.MakeFeatureLayer_management(r"bgPts_zone_quarterM", "bgPtsZoneQuarterM_lyr")

## Very important:
tripVol_dict = {} # ORIG_FID -> dict_{destination name: volume}

# Initialize route score dictionaries
# ..

# Local & GLOBAL variables
# ..


#
####
###### BEGIN FUNCTIONS
def computeSD(list):
  n = len(list)
  return math.sqrt(sum([dev*dev for dev in [x-(sum(list)/n) for x in list]]) / (n-1) )

def computeAvgTT(timeDict, volDict):
  weightedSum = 0          
  for name in timeDict.keys():
    weightedSum += (volDict[name]*timeDict[name])
  return weightedSum / sum(volDict.values())
  

###### END FUNCTIONS
####
#

start_time = time.time()

# Build OD Cost Matrix Layer
outNALayer = arcpy.na.MakeODCostMatrixLayer(r"metroFinal_FD\metroFinal_FD_ND", "TravelTimeMatrix", "TravelTime", "", "", "", "", "", "", "", "NO_LINES", "1/1/1900 8:00 AM")
# Get the layer object from the result object. The OD cost matrix layer can 
# now be referenced using the layer object.
outNALayer = outNALayer.getOutput(0)
# Get layer names.
subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
originsLayerName = subLayerNames["Origins"]
destLayerName = subLayerNames["Destinations"]
linesLayerName = subLayerNames["ODLines"]

# Set destLayer and originsLayer object pointers.
originsLayer = ""
destLayer = ""
linesLayer = ""

# Get layer objects so we can make layers out of them later.
# Not to be confused with the layer names.
for layer in arcpy.mapping.ListLayers(outNALayer)[1:]:
	
    if layer.datasetName == "Destinations":
        destLayer = layer
    if layer.datasetName == "Origins":
	originsLayer = layer
for layer in arcpy.mapping.ListLayers(outNALayer)[1:]: # Indents messed up.
    if layer.datasetName == "ODLines":
	linesLayer = layer
	break
else:
	raise Exception("Failed to get lines")

# Add fields to the destinations layer.
arcpy.AddField_management(destLayer, "ORIG_FID", "LONG")
arcpy.AddField_management(destLayer, "JOBS", "DOUBLE")

# Add fields to the origins layer.
arcpy.AddField_management(originsLayer, "ORIG_FID", "LONG")
arcpy.AddField_management(originsLayer, "NEARBY_ONS", "FLOAT")
arcpy.AddField_management(originsLayer, "PERC_LOWSES", "DOUBLE")
arcpy.AddField_management(originsLayer, "AVG_TT", "DOUBLE")


# For each bgPt from the potential destinations, add it to the destLayer 
# and append its location i->ons,offs,jobs, and lowSES dicts.
destWhere = '"NEAR_OFFS" >= ' + str(157)
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "NEW_SELECTION", destWhere)

# These all map dest names to stuff
origfid_dict = {}
jobs_dict = {} # (int -> double)

# Build destinations layer
bgC = arcpy.da.SearchCursor("bgPtsZoneQuarterM_lyr", ["ORIG_FID", "NUM_JOBS"])
i = 1
for row in bgC:
	orig_fid = row[0]
	jobs = row[1]
	
	origfid_dict[i] = orig_fid
	jobs_dict[i] = jobs
	i += 1
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(orig_fid))
	arcpy.na.AddLocations(outNALayer, destLayerName, "bgPtsFinal_lyr", "", "", "", [["StreetsUseThisOne", "SHAPE_MIDDLE_END"]], "", "APPEND", "", "", "", "")
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "CLEAR_SELECTION")
del row
del bgC
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "CLEAR_SELECTION")

# Make destinations a layer.
destLayer = arcpy.management.MakeFeatureLayer(destLayer, "TravelTimeMatrix_" + destLayerName)

# Compute destination fields
dC = arcpy.da.UpdateCursor(destLayer, ["Name", "ORIG_FID", "JOBS"])
for row in dC:
	name = int(row[0].split(" ")[1])
	orig_fid = origfid_dict[name]
	jobs = jobs_dict[name]
	row[1] = orig_fid
	row[2] = jobs
	dC.updateRow(row)
del row
del dC

# Export destLayer to layer file?


#                                          #
# #######################################  #
#                                          #

# Repeat for origins:
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "NEW_SELECTION", '"ORIG_FID" IS NOT NULL')

# These all map dest names to stuff
origfid_dict = {}
ons_dict = {}  # (int -> float)
lowSES_dict = {} # (int -> double)

# Build origins layer
bgC = arcpy.da.SearchCursor("bgPtsZoneQuarterM_lyr", ["ORIG_FID", "NEAR_ONS", "PERC_LOWSES"])
i = 1
for row in bgC:
	orig_fid = row[0]
	ons = row[1]
	lowSES = row[2]
	
	origfid_dict[i] = orig_fid
	ons_dict[i] = ons
	lowSES_dict[i] = lowSES
	i += 1
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(orig_fid))
	arcpy.na.AddLocations(outNALayer, originsLayerName, "bgPtsFinal_lyr", "", "", "", [["StreetsUseThisOne", "SHAPE_MIDDLE_END"]], "", "APPEND", "", "", "", "")
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "CLEAR_SELECTION")
del row
del bgC
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "CLEAR_SELECTION")

# Make origins a layer.
originsLayer = arcpy.management.MakeFeatureLayer(originsLayer, "TravelTimeMatrix_" + originsLayerName)

# Compute origin fields
dC = arcpy.da.UpdateCursor(originsLayer, ["Name", "ORIG_FID", "NEARBY_ONS", "PERC_LOWSES"])
for row in dC:
	name = int(row[0].split(" ")[1])
	orig_fid = origfid_dict[name]
	ons = ons_dict[name]
	lowSES = lowSES_dict[name]
	
	row[1] = orig_fid
	row[2] = ons
	row[3] = lowSES
	dC.updateRow(row)
del row
del dC

# Export originsLayer to layer file?


              ## ORIGINS & DESTINATIONS ARE COMPLETE ##


try:       
    arcpy.Solve_na(outNALayer)
    arcpy.SaveToLayerFile_management(outNALayer, r"H:\metroFinal.gdb\TravelTimeMatrix.lyr", "RELATIVE")

# OHMYFUCKINGGODWHYDIDNTISEETHISEARLIER????
# http://proceedings.esri.com/library/userconf/proc11/tech-workshops/tw_1029.pdf
# Cntrl+F for Processing sublayers in scripts

# Gist:
# originsSubLayer = outNALayer + os.sep + "Origins"
# outFeatureClass = "..."
# arcpy.CopyFeatures_management(originsSubLayer, outFeatureClass)


except Exception as e:
    import traceback, sys
    tb = sys.exc_info()[2]
    print "Yo an error happened on line %i" % tb.tb_lineno
    print str(e)


print str(time.time() - start_time) + " seconds."
print "Good work man!"


