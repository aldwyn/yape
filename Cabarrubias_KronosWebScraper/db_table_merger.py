import sqlite3

con = sqlite3.connect('kronos_sites_for_consolidation.db')
with con:
	cur = con.cursor()
	print con

	cur.execute("SELECT * FROM kronos_google")
	to_consolidated = cur.fetchall()

	cur.execute("DROP TABLE IF EXISTS consolidated")
	cur.execute("CREATE TABLE consolidated (URL TEXT, Date_Processed TEXT, Team TEXT)")

	cur.executemany("INSERT INTO consolidated VALUES (?, ?, ?)", to_consolidated)

	cur.execute("SELECT * FROM kronos_yahoo WHERE URL NOT IN (SELECT URL FROM consolidated)")
	to_consolidated = cur.fetchall()

	cur.executemany("INSERT INTO consolidated VALUES (?, ?, ?)", to_consolidated)

	cur.execute("SELECT * FROM kronos_bing WHERE URL NOT IN (SELECT URL FROM consolidated)")
	to_consolidated = cur.fetchall()

	cur.executemany("INSERT INTO consolidated VALUES (?, ?, ?)", to_consolidated)