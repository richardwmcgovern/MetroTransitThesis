# mainScript.py
# Will do everything
#
# 

import arcpy, math
from arcpy import env
import sqlite3, shutil, time

workspace = "H:\\metroFinal.gdb"
env.workspace = workspace
env.overwriteOutput = True

arcpy.CheckOutExtension("Network")

# Connect to sql table
finalSql = "H:\\metroFinal.gdb\\GTFS.sql"
conn = sqlite3.connect(finalSql)

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
# These will be referenced by origins when computing AVG_TT
arcpy.AddField_management(destLayer, "NEARBY_ONS", "FLOAT")
arcpy.AddField_management(destLayer, "NEARBY_OFFS", "FLOAT")
arcpy.AddField_management(destLayer, "JOBS", "DOUBLE")
arcpy.AddField_management(destLayer, "PERC_LOWSES", "DOUBLE")

# For each bgPt from the potential destinations, add it to the destLayer 
# and append its location i->ons,offs,jobs, and lowSES dicts.
destWhere = '"NEAR_OFFS" >= ' + str(157)
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "NEW_SELECTION", destWhere)
ons_dict = {}  # (int -> float)
offs_dict = {} # (int -> float)
jobs_dict = {} # (int -> double)
lowSES_dict = {} # (int -> double)

# The bgPts zone layer is used as a proxy
bgC = arcpy.da.SearchCursor("bgPtsZoneQuarterM_lyr", ["ORIG_FID", "NEAR_OFFS", "NUM_JOBS", "NEAR_ONS", "PERC_LOWSES"])
i = 1
TOTALOFFS = 0
TOTALJOBS = 0
for row in bgC:
	orig_fid = row[0]
	ons = row[3]
	offs = row[1]
	jobs = row[2]
	lowSES = row[4]
	TOTALOFFS += offs
	TOTALJOBS += jobs
	ons_dict[i] = ons
	offs_dict[i] = offs
	jobs_dict[i] = jobs
	lowSES_dict[i] = lowSES
	i += 1
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(orig_fid))
	arcpy.na.AddLocations(outNALayer, destLayerName, "bgPtsFinal_lyr", "", "", "", [["StreetsUseThisOne", "SHAPE_MIDDLE_END"]], "", "APPEND", "", "", "", "")
	arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "CLEAR_SELECTION")
del row
del bgC
arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "CLEAR_SELECTION")

# Make destinations a layer.
destLayer = arcpy.management.MakeFeatureLayer(destLayer, "TravelTimeMatrix_" + destLayerName)

# Compute ons, offs, jobs, and lowSES new fields
dC = arcpy.da.UpdateCursor(destLayer, ["Name", "NEARBY_OFFS", "JOBS", "NEARBY_ONS", "PERC_LOWSES"])
for row in dC:
	name = int(row[0].split(" ")[1])
	ons = ons_dict[name]
	offs = offs_dict[name]
	jobs = jobs_dict[name]
	lowSES = lowSES_dict[name]
	row[1] = offs
	row[2] = jobs
	row[3] = ons
	row[4] = lowSES
	dC.updateRow(row)
del row
del dC


print str(time.time() - start_time) + " seconds to create OD layer and add destinations."

              ## DESTINATIONS ARE COMPLETE ##

#Time it!
start_time = time.time()

# Big loop: Compute average trip time for each bgPtsFinal feature.
# Keep track of AVG_TT in bg_tt_dict: ORIG_FID -> AVG_TT 
# If you need more fields in the bgZone proxy cursor, add them to the end.
bg_tt_dict = {}
destCursor = arcpy.da.SearchCursor(destLayer, ["NEARBY_ONS", "NEARBY_OFFS", "JOBS", "PERC_LOWSES"])
for dest in destCursor:
  ORIG_FID = bgZone[0]
  originOns = bgZone[1]
  originLSP = bgZone[2]

  # Instead of all this. Increment over the already-added dests
  # and add them as origins with the field mappings
  arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(ORIG_FID))
  arcpy.na.AddLocations(outNALayer, originsLayerName, "bgPtsFinal_lyr", "", "", "", [["StreetsUseThisOne", "SHAPE_MIDDLE_END"]], "", "CLEAR", "", "", "", "")
  arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "CLEAR_SELECTION")
  #originsLayer = arcpy.management.MakeFeatureLayer(originsLayer, "TravelTimeMatrix_" + originsLayerName)
  try:
          
          arcpy.Solve_na(outNALayer)
          #linesLayer = arcpy.management.MakeFeatureLayer(linesLayer, "TravelTimeMatrix_" + linesLayerName)

          # Make travelTime_dict [name -> tt]. Compute maxTT.
          travelTime_dict = {}
          maxTT = 0
          lCursor = arcpy.da.SearchCursor(linesLayer, ["DestinationID", "Total_TravelTime"])
          for row in lCursor:
                  travelTime_dict[row[0]] = row[1]
                  if row[1] > maxTT:
                          maxTT = row[1]
          del row
          del lCursor

          # Compute Tau values: TT difference from maxTT / sum of differences
          # Compute diff = maxTT - TT for each destination
          # Store in tau_dict and keep track of the totalDiff
          tau_dict = {} #(long -> double) [name: tau_val]
          totalDiff = 0
          lCursor = arcpy.da.SearchCursor(linesLayer, ["DestinationID", "Total_TravelTime"])
          for row in lCursor:
                  diff = maxTT - row[1]
                  totalDiff += diff
                  tau_dict[row[0]] = diff
                  
          del row
          del lCursor
          
          # Compute tau_dict
          for name in tau_dict.keys():
                  tau_dict[name] = tau_dict[name] / totalDiff
                  
          # Compute beta and alpha (1-beta)
          # The higher the %lowSES, the lower beta gets.
          # Less LSP means more privileged ppl with more travel mode options.
          beta = 1 - math.sqrt(originLSP)
          alpha = 1 - beta

          # name->trip volume
          nameVol_dict = {}
          for name in tau_dict.keys():
                  # Trip_Volume equation
                  tripVol = originOns*((alpha*(jobs_dict[name]/TOTALJOBS)) + (beta*(tau_dict[name])))
                  nameVol_dict[name] = tripVol
                  
          tripVol_dict[ORIG_FID] = nameVol_dict
          
          # Compute AverageTripTime for this ORIG_FID
          averageTripTime = computeAvgTT(travelTime_dict, nameVol_dict)

          # Put the AVG_TT in the dictionary
          bg_tt_dict[ORIG_FID] = averageTripTime

          # Debug print avg trip time for orig fid
          print "DEBUG HERE. " + str(ORIG_FID) + "'s average trip time: " + str(averageTripTime)
	
  except Exception as e:
          import traceback, sys
          tb = sys.exc_info()[2]
          print "Yo an error happened on line %i" % tb.tb_lineno
          print str(e)
del dest
del destCursor

# Update AVG_TT fields in bgPtsFinal with bg_tt_dict
bgCursor = arcpy.da.UpdateCursor(r"metroFinal_FD\bgPts_final", ["ORIG_FID", "AVG_TT"])
for row in bgCursor:
  row[1] = bg_tt_dict[row[0]]
  bgCursor.updateRow(row)
del row
del bgCursor

print str(time.time() - start_time) + " seconds to finish big loop and update AVG_TT fields."
print "Good work man!"

# Compute Average Trip Times
#..

#############################################################
# The following is for computing change in avg trip time ####
#############################################################

# use the 1/4-mile buffer layer as a proxy for bgPts_final
# ORIG_FID, RT_LIST, NEAR_ONS
#bgC = arcpy.da.SearchCursor("bgPtsZoneQuarterM_lyr", ["ORIG_FID", "RT_LIST", "NEAR_ONS"])

# The mega-loop over all bgPts_zone origins
# for row in bgC:
	# orig_fid = row[0]
	# rt_list = row[1]
	# near_ons = row[2]
	#Select the corresponding bgPts_final feature
	# arcpy.SelectLayerByAttribute_management("bgPtsFinal_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(orig_fid))
	
	#Add the selected bgPts_final feature to origins (1)
	# arcpy.na.AddLocations(outNALayer, originsLayer, "bgPtsFinal_lyr", "", "", "", [["StreetsUseThisOne", "SHAPE_MIDDLE_END"]], "", "CLEAR", "", "", "", "")
	
	# servicingRoutes = rt_list.split(",")
	# for testRoute in servicingRoutes


		#Fetch the route_id of the testRoute
		# c = conn.cursor()
		# routeIDAsList = []
		# for row in c:
			
		# del row
		# del c
		#Fetch the trips to select as a subset from tempTST
		# c = conn.cursor()
		# getGoodTrips = "SELECT trip_id FROM trips WHERE route_id <> " + str(routeToBlock)
		# c.execute(getGoodTrips)
		# goodTrips = c.fetchall()
		# del c
# del row
# del bgC



# arcpy.Delete_management(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\metroFinal.gdb\TransitScheduleTable", "Table")

# tripWhere = "\"trip_id\" = 'googletransitmetro:11367651'"
# arcpy.TableToTable_conversion(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\TableStorage.gdb\tempTST", r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\metroFinal.gdb", "TransitScheduleTable", where)

conn.close()

#######################################################################################################################
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # #          F U N C T I O N S          # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#######################################################################################################################


