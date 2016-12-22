# Add rt_list to bgPts
#
import arcpy

bgCursor = arcpy.da.UpdateCursor("bgPts", ["ORIG_FID", "RT_LIST"])
counter = 0
for row in bgCursor:
	
	if row[1] is None and counter < 100:
		counter += 1
		arcpy.SelectLayerByAttribute_management("bgPts_zone", "NEW_SELECTION", '"ORIG_FID" = ' + str(row[0]))
		arcpy.SelectLayerByLocation_management("Stops", "WITHIN", "bgPts_zone", "", "NEW_SELECTION")
		matchcount = int(arcpy.GetCount_management("Stops").getOutput(0))
		arcpy.SelectLayerByAttribute_management("bgPts_zone", "CLEAR_SELECTION")
		if matchcount > 0:
			stopsC = arcpy.da.SearchCursor("Stops", ["ROUTE_LIST"])
			rt_list = []
			for s in stopsC:
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