import csv
import io
import operator

inpfilename = "./out/data/Milet_Bibliography_CSV.csv"
#inpfilename = "2022_02_16_Bibliographie.csv"
inpnewfilename = "./out/milet-bibliography-html-tablerows"

print("Converting file: ", inpfilename)

# Import in dictionary
with io.open(str(inpfilename), encoding="utf-8") as impfile:
	dict_list = []
	reader = csv.DictReader(impfile, delimiter=',')
	for row in reader:
		dict_list.append(row)

dict_list = sorted(dict_list, key=lambda k: (k['Publication Year'], k['Author']), reverse=True)

#Schreibt alles in eine Datei, iteriert über die Listeneinträge / Reihen
file = io.open(str(inpnewfilename+".txt"), "w", encoding="utf-8") 



for i in range(len(dict_list)):
	file.write("<tr>\n")
	file.write("<td>"+str(dict_list[i]['Title'])+"</td>\n")
	if str(dict_list[i]['Author']) == "":
		file.write("<td>"+str(dict_list[i]['Editor'])+"</td>\n")
	else: 
		file.write("<td>"+str(dict_list[i]['Author'])+"</td>\n")
	file.write("<td>"+str(dict_list[i]['Publication Year'])+"</td>\n")

	file.write("<td>")
	if str(dict_list[i]['Item Type']) == "journalArticle":
		file.write(str(dict_list[i]['Publication Title']))
	elif str(dict_list[i]['Series']) != "":
		file.write(str(dict_list[i]['Series']))
	file.write("</td>\n")


	file.write("<td>\n")
	if str(dict_list[i]['Item Type']) == "book":
		if str(dict_list[i]['Author']) == "":
			file.write(str(dict_list[i]['Editor']))
		else:
			file.write(str(dict_list[i]['Author']))
		file.write(", ")
		file.write(str(dict_list[i]['Title']))
		file.write(" ("+str(dict_list[i]['Place'])+" "+str(dict_list[i]['Publication Year'])+")")
	elif str(dict_list[i]['Item Type']) == "bookSection":
		file.write(str(dict_list[i]['Author']))
		file.write(", ")
		file.write(str(dict_list[i]['Title']))
		file.write(", in: ")
		file.write(str(dict_list[i]['Editor']))
		file.write(", ")
		file.write(str(dict_list[i]['Publication Title']))
		file.write(" ("+str(dict_list[i]['Place'])+" "+str(dict_list[i]['Publication Year'])+")")
		file.write(", "+str(dict_list[i]['Pages']))
	elif str(dict_list[i]['Item Type']) == "journalArticle":
		file.write(str(dict_list[i]['Author']))
		file.write(", ")
		file.write(str(dict_list[i]['Title']))
		file.write(", ")
		file.write(str(dict_list[i]['Publication Title'])+" "+str(dict_list[i]['Volume']))
		file.write(", ")
		file.write(str(dict_list[i]['Publication Year']))
		file.write(", ")
		file.write(str(dict_list[i]['Pages']))
	elif str(dict_list[i]['Item Type']) == "thesis":
		file.write(str(dict_list[i]['Author']))
		file.write(", ")
		file.write(str(dict_list[i]['Title']))
		file.write(" (")
		file.write(str(dict_list[i]['Type'])+" "+str(dict_list[i]['Publisher'])+" "+str(dict_list[i]['Publication Year']))
		file.write(")")
	elif str(dict_list[i]['Item Type']) == "dictionaryEntry":
		file.write(str(dict_list[i]['Publication Title'])+" "+str(dict_list[i]['Volume']))
		file.write(" ("+str(dict_list[i]['Publication Year'])+") "+str(dict_list[i]['Pages']))
		file.write(" s.v. "+str(dict_list[i]['Title']))
		file.write(" ("+str(dict_list[i]['Author'])+")")
		
	file.write("")
	if str(dict_list[i]['DOI']) != "":
		file.write(" <br> <a href=\"https://doi.org/"+str(dict_list[i]['DOI'])+"\">Online verfügbar (DOI)</a>")
	elif str(dict_list[i]['Url']) != "":
		file.write(" <br> <a href=\""+str(dict_list[i]['Url'])+"\">Online verfügbar (Link)</a>")
	file.write("</td>\n")
#	file.write("<td>"+str(dict_list[i]['Publication Title']))
#	if str(dict_list[i]['Volume']) != "":
#		file.write(" "+str(dict_list[i]['Volume']))
#	if str(dict_list[i]['Pages']) != "":
#		file.write(", Seiten "+str(dict_list[i]['Pages']))
#	if str(dict_list[i]['Editor']) != "":
#		file.write(" (Hrsg.: "+str(dict_list[i]['Editor'])+") ")
	file.write("</td>\n")
	file.write("<td>"+str(dict_list[i]['Manual Tags'])+"</td>\n")
	file.write("<td>"+str(dict_list[i]['Abstract Note'])+"</td>\n")
	file.write("</tr>\n\n")
print("Done. Saved as "+str(inpnewfilename)+".txt")
file.close() 
