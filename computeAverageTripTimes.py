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



# Connect to sql table
#finalSql = "H:\\metroFinal.gdb\\GTFS.sql"
#conn = sqlite3.connect(finalSql)



# Compute Trip Volumes
# ..


# Compute Average Trip Times
# Store in bgPts_final.shp
# ..

# Jobs at each destination and totalJobs
destID_Jobs_dict = {}
totalJobs = 0
dC = arcpy.da.SearchCursor("destinations_lyr", ["Name", "JOBS"])
for row in dC:
    destID = row[0].split(" ")[1]
    jobs = row[1]
    totalJobs += jobs
    destID_Jobs_dict[destID] = jobs
del row
del dC

oC = arcpy.da.UpdateCursor("origins_lyr", ["ORIG_FID", "NEARBY_ONS", "PERC_LOWSES", "Name", "AVG_TT"])
for row in oC:
    if row[4] is None:
        orig_fid = row[0]
        ons = row[1]
        lowSES = row[2]
        OriginID = row[3].split(" ")[1]

        # Coefficients
        beta = 1 - math.sqrt(lowSES)
        alpha = 1 - beta
        
        arcpy.SelectLayerByAttribute_management("lines_lyr", "NEW_SELECTION", '"OriginID" = ' + OriginID)
        matchcount = int(arcpy.GetCount_management("lines_lyr").getOutput(0))
        if matchcount > 0:
            linesC = arcpy.da.SearchCursor("lines_lyr", ["DestinationID", "Total_TravelTime"])
            maxTT = 0
            timeDict = {} # (destID) -> tt
            for line in linesC:
                DestinationID = str(line[0])
                TT = line[1]
                timeDict[DestinationID] = TT
                if TT > maxTT:
                    maxTT = TT
                
            del line
            del linesC

            sumTau = sum([maxTT - TT for TT in timeDict.values()])
            
            # Compute average trip time
            weightedSum = 0
            totalVol = 0
            for dest in timeDict.keys():
                # Trip volume equation
                 trip_vol = ons*((alpha*(destID_Jobs_dict[dest]/totalJobs)) + (beta*((maxTT - timeDict[dest])/sumTau)))
                 totalVol += trip_vol
                 weightedSum += (trip_vol*timeDict[dest])

            if totalVol != 0:
                avg_tt = weightedSum / totalVol
                print str(avg_tt)

                row[4] = avg_tt
                oC.updateRow(row)
    
    
del row
del oC


# For each route resolve TravelTimeMatrix.lyr?




#conn.close()
