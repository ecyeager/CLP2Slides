#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Elyse Yeager, Andrew Rechnitzer, Joel Feldman"
__copyright__ = "Copyright (C) 2021-2024 Elyse Yeager, Andrew Rechnitzer, and Joel Feldman"
__credits__ = ["Elyse Yeager, Andrew Rechnitzer"]
__license__ = "GPL-3.0-or-later"

#################################################################
# PYTHON MODULE IMPORTS - do not change
#################################################################

from glob import glob
import os
import subprocess
import shutil

#################################################################
# DEBUG
#################################################################
# Set the following to True to see what files will be generated
# without generating them
dry_run = False

#################################################################
# COMPILATION CHOICES
#################################################################
## There are three versions possible for each file: lecture, handout, and full. 
## To choose which to print, set the following to True or False:

print_lecture=True
print_handout=True
print_full=True


## There are also miscellaneous files: StudentWorkbook, NotesOnly, and ReadMe
## To choose which to print, set the following to True or False:

print_sections=True
print_readme=True
print_studentworkbook=True
print_notesonly=True



#################################################################
## LISTS OF SECTIONS 
#################################################################
## If you would like to omit some sections from the list of 
## files to compile, then
## comment out the corresponding lines in the lists below.
## If print_sections is set to False, all sections will be omitted whether or not
## they are in the list.

#section number, section name
section_names_list = [
	["1_1","Definition"],
    ["1_1_7","OptionalDefinition"],
    ["1_2","Properties"],
    ["1_3","FundamentalTheorem"],
    ["1_4","Substitution"],
    ["1_5","AreaBetweenCurves"],
    ["1_6","Volumes"],
    ["1_7","IntegrationByParts"],
    ["1_8","TrigIntegrals"],
    ["1_8_3","OptionalTrigIntegrals"],
    ["1_9","TrigSubstitution"],
    ["1_10","PartialFractions"],
    ["1_11","NumericalIntegration"],
    ["1_11_5","OptionalErrorMidpoint"],
    ["1_12","ImproperIntegrals"],
    ["2_1","Work"],
    ["2_2","Averages"],
    ["2_3","CentreOfMass"],
    ["2_4","SeparableDiffEq"],
    ["2_4_2-2_4_6","OptionalDEApplications"],
    ["3_1","Sequences"],
    ["3_2","Series"],
    ["3_3_1-3_3_3","ConvergenceTests"],
    ["3_3_4-3_3_6","ConvergenceTests"],
    ["3_4_1","AbsoluteConvergence"],
    ["3_4_2","OptionalConditionalConvergence"],
    ["3_5","PowerSeries"],
    ["3_6","TaylorSeries"]
]



#################################################################
# End of compilation choices
#################################################################

#################################################################
# Make list of types to print (lecture, handout, full)
#################################################################

type_list=[]
if print_lecture:
	type_list.append("lecture")
if print_handout:
	type_list.append("handout")
if print_full:
	type_list.append("full")



#################################################################
# Build function
## Given a filename in the src directory: 
## build, put PDF in pdf file
#################################################################

SOURCE_DIR = "src"
PDF_DIR = "pdfs"

def build_pdf(base_filename):
	if dry_run==True:
		print("Build ",base_filename)
		return
	#change directory
	os.chdir(SOURCE_DIR)
 	# run latex
	subprocess.run(["pdflatex", "-interaction=nonstopmode", base_filename])
	# # move the resulting pdf to the PDF directory
	shutil.move(
        base_filename + ".pdf", os.path.join("..", PDF_DIR, base_filename + ".pdf")
    )
 #    # go back into parent directory
	os.chdir("..")

#################################################################
# Build individual sections
## Given a section number, section title, and slide type, generate a .tex file
## build it using build_pdf
#################################################################

def onesection(sectionnumber,sectionname,slidetype):
	#create the new .tex file named with section number, name, and type
	#if it already exists, overwrite
	if slidetype=='lecture' or slidetype=='l':
		base_filename=sectionnumber+sectionname+'_lecture'
		texFile=open(os.path.join('src',base_filename)+'.tex','w')
		texFile.write("\\documentclass[10pt]{beamer} \n\n\\usepackage{header101} \n\\usepackage{header_maps}\n \\settoggle{spoiler}{false}")
	elif slidetype=='handout' or slidetype=='h':
		base_filename=sectionnumber+sectionname+'_handout'
		texFile=open(os.path.join('src',base_filename+'.tex'),'w')
		texFile.write("\\documentclass[10pt,handout]{beamer}  \n\n\\usepackage{header101} \n\\usepackage{header_maps}\n\\settoggle{spoiler}{false}")
	elif slidetype=='full' or slidetype=='f':
		base_filename=sectionnumber+sectionname+'_full'
		texFile=open(os.path.join('src',base_filename+'.tex'),'w')
		texFile.write("\\documentclass[10pt]{beamer} \n\n\\usepackage{header101} \n\\usepackage{header_maps}")
	else:
		print('second argument should be "lecture" or "l" for slides to show in class, "handout" or "h" for slides to give to students, or "full" or "f" for slides with solutions')

	#packages and begin{document} common to all types
	texFile.write(' \n\n\\begin{document} \n\n')
	#input the section contents
	texFile.write('\\input{sections/'+sectionnumber+'.tex}\n')	
	#end tex file
	texFile.write('\\LastPage  \n\n\\end{document}')
	texFile.close()

	#build
	build_pdf(base_filename)




#################################################################
# Make PDFs for all sections
#################################################################
if print_sections:
	for type in type_list:
		for section in section_names_list:
			onesection(section[0],section[1],type)


#################################################################
# Make PDFs for miscellaneous files
#################################################################
if print_studentworkbook:
	build_pdf('StudentWorkbook')

if print_notesonly:
	#check whether aux files exist; if not, make them
	for section in section_names_list:
		if not os.path.isfile(os.path.join(SOURCE_DIR,section[0]+section[1]+"_full.aux")):
			onesection(section[0],section[1],"full")
	build_pdf('NotesOnly')


if print_readme:
	PDF_DIR = "." # ReadMe.pdf goes in the main directory
	build_pdf("ReadMe")
	PDF_DIR = "pdfs" #reset the pdf directory

