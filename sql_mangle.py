#!/usr/bin/python

import sqlite3
import sqlize_csv
import hms
import arcgisscripting
import arcpy
from arcpy import env
import shutil, os, errno

gp = arcgisscripting.create()

gdb = "C:\\Users\\Richard McGovern\\Desktop\\Thesis Working Folder\\metroStuff.gdb"
#gdbSQL = "C:\\Users\\Richard McGovern\\Desktop\\Thesis Working Folder\\metroStuff.gdb\\GTFS.sql"
practice = "C:\\Users\\Richard McGovern\\Desktop\\GTFS.sql"
transitScheduleTable = "C:\\Users\\Richard McGovern\\Desktop\\Thesis Working Folder\\metroStuff.gdb\\TransitScheduleTable"
#conn = sqlite3.connect(transitScheduleTable) # Can be accessed in the functions
#c = conn.cursor()
conn = sqlite3.connect(gdb)
c = conn.cursor()
GetTblNamesStmt = "SELECT name FROM sqlite_master WHERE type='table';"
c.execute(GetTblNamesStmt)
tableNames = c.fetchall()
TblNameList = []
for table in tableNames:
	TblNameList.append(table)
print TblNameList[0]

### This is it! This is it!
#
# arcpy.TableToTable_conversion("C:\\Users\\Richard McGovern\\Desktop\\Thesis Working Folder\\TableStorage.gdb\\tView", r"C:\Users\Richard McGovern\Desktop\Thesis Working Folder\metroStuff.gdb", "tSubset", "\"trip_id\" = 'googletransitmetro:11367651'")
###



# c = conn.cursor()

# routeIDs = "SELECT route_id, route_short_name FROM routes"
# c.execute(routeIDs)
# routes = c.fetchall()
# for rt in routes:
	# print rt[0] + " is " + rt[1]

# route_id's contain 'googletransitmetro:' before the number
# 100228 is the 48

# Block use of the given route by deleting all trips with that route_id
# from the TransitScheduleTable. NOT TXT.
# A copy of the TransitScheduleTable will be made.
def blockRoute(routeID):
	c = conn.cursor()
	# Be careful. Need 'quotes' around value in WHERE.
	sqlStmt = "SELECT trip_id FROM trips WHERE route_id = 'googletransitmetro:" + str(routeID) + "'"
	c.execute(sqlStmt)
	blockedTrips = c.fetchall()
	for trip in blockedTrips:
		print trip[0]
	del c
#blockRoute(100228) # works!

#env.workspace = "C:\\Users\\Richard McGovern\\Desktop\\Thesis Working Folder\\metroStuff.gdb"

#cur = arcpy.da.UpdateCursor("TransitScheduleTable", ["trip_id"])

#del cur

# arcpy.da.MakeODCostMatrixLayer_na(INPUT NETWORK DATASET, OUT NA LAYER, 
#								IMPEDANCE ATTR, default_cutoff, "", "", "", "",
#								hierarchy, NO_LINES or STRAIGHT_LINES)

# About deleting...
# For feature classes, use Make Feature Layer (with a SQL expression), followed by Delete Features.
# For tables, use Make Table View (with a SQL expression), followed by Delete Rows.

	
print "Operation done successfully";
conn.close()

#tripTable = practice + ".trips"
#conn = sqlite3.connect(tripTable)