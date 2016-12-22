# Add rt_list to bgPts
#
import arcpy
from arcpy import env

env.workspace = r"H:\metroFinal.gdb"
env.overwriteOutput = True
# Make layers
arcpy.MakeFeatureLayer_management(r"metroFinal_FD\bgPts_final", "bgPtsFinal_lyr")
arcpy.MakeFeatureLayer_management(r"bgPts_zone_quarterM", "bgPtsZoneQuarterM_lyr")
arcpy.MakeFeatureLayer_management(r"metroFinal_FD\Stops", "Stops_lyr")

bgCursor = arcpy.da.UpdateCursor(r"metroFinal_FD\bgPts_final", ["ORIG_FID", "NEAR_ONS"])
counter = 0
for row in bgCursor:
		
	arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(row[0]))
	arcpy.SelectLayerByLocation_management("Stops_lyr", "INTERSECT", "bgPtsZoneQuarterM_lyr", "", "NEW_SELECTION")
	matchcount = int(arcpy.GetCount_management("Stops_lyr").getOutput(0))
	arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "CLEAR_SELECTION")
	if matchcount > 0:
		#counter += 1
		stopsC = arcpy.da.SearchCursor("Stops_lyr", ["ROUTE_LIST", "TotalOns"])
		totalOns = 0
			
		for s in stopsC:
			if s[1] is not None:
				totalOns += s[1]
		del s
		del stopsC
		
		row[1] = totalOns
		bgCursor.updateRow(row)
del row
del bgCursor
#arcpy.CopyFeatures_management("bgPtsFinal_lyr", r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\metroFinal.gdb\metroFinal_FD\bgPts_final")
# mxd = arcpy.mapping.MapDocument(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\MetroFinal_2.mxd")
# mxd.saveACopy(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\MetroFinal_2copy.mxd")
# del mxd