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

bgCursor = arcpy.da.UpdateCursor(r"metroFinal_FD\bgPts_final", ["ORIG_FID", "RT_LIST", "NEAR_OFFS"])
counter = 0
for row in bgCursor:
		
	arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "NEW_SELECTION", '"ORIG_FID" = ' + str(row[0]))
	arcpy.SelectLayerByLocation_management("Stops_lyr", "WITHIN", "bgPtsZoneQuarterM_lyr", "", "NEW_SELECTION")
	matchcount = int(arcpy.GetCount_management("Stops_lyr").getOutput(0))
	arcpy.SelectLayerByAttribute_management("bgPtsZoneQuarterM_lyr", "CLEAR_SELECTION")
	if matchcount > 0:
		#counter += 1
		stopsC = arcpy.da.SearchCursor("Stops_lyr", ["ROUTE_LIST", "TotalOffs"])
		rt_list = []
		totalOffs = 0
			
		for s in stopsC:
			
			if s[1] is not None:
				totalOffs += s[1]
			row[2] = totalOffs
			bgCursor.updateRow(row)
			
			if s[0] is not None:
				tempList = s[0].split(",")
				for rt in tempList:
					if rt not in rt_list:
						rt_list.append(rt)
		del s
		del stopsC
		servicingRts = ""
		for rt in rt_list:
			servicingRts += rt + ","
		if len(servicingRts) > 0:
			servicingRts = servicingRts[:len(servicingRts)-1]
		row[1] = servicingRts
		bgCursor.updateRow(row)
del row
del bgCursor
#arcpy.CopyFeatures_management("bgPtsFinal_lyr", r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\metroFinal.gdb\metroFinal_FD\bgPts_final")
# mxd = arcpy.mapping.MapDocument(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\MetroFinal_2.mxd")
# mxd.saveACopy(r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\MetroFinal_2copy.mxd")
# del mxd