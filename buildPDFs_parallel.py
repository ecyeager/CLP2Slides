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
from multiprocessing import Pool
import os
import subprocess
import shutil
from tqdm import tqdm


#################################################################
# SLIDE COMPILATION CHOICES
#################################################################
## There are three versions possible for each file: beamer, handout, and prep.
## To choose which to print, set the following to True or False:

print_lecture = True
print_handout = True
print_full = True

## There are also miscellaneous files: CLP2StudentWorkbook, NotesOnly, and ReadMe
## To choose which to print, set the following to True or False:

print_sections = True
print_readme = True
print_studentworkbook = True
print_notesonly = True #to compile this, make sure you also compile ALL sections

## Delete the auxiliary files makes the src directory cleaner
## To keep the aux files, set the following to False; to delete them, set it to True:

delete_aux = True

# a list of extensions of auxillary files to clean up
cleanup_ext = [
    ".aux",
    ".fls",
    ".gz",
    ".idx",
    ".ilg",
    ".ind",
    ".log",
    ".nav",
    ".out",
    ".snm",
    ".toc",
    ".fdb_latexmk",
    ".vrb"  
]

#################################################################
# BUILD PROCESS OPTIONS
#################################################################
# Set the following to True to see what files will be generated
# without actually generating them
dry_run = False

# If build_quiet is set to true, then all latex output is hidden.
# useful for long builds
build_quiet = False

# Set the number of build processes. Leave set to 'None' to let the
# system choose how many to use. Else set to a specific (small) integer
# if you know what you are doing.
number_of_processes = None


#################################################################
## LISTS OF SECTIONS
#################################################################
## If you would like to omit some sections from the list of
## files to compile, then
## comment out the corresponding lines in the lists below.
## If print_sections is set to False, all sections will be omitted whether or not
## they are in the list.

# section number, section name
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
# Make list of types to print (beamer, handout, prep)
#################################################################

type_list = []
if print_full:
    type_list.append("full")
if print_lecture:
    type_list.append("lecture")
if print_handout:
    type_list.append("handout")


#################################################################
# Build function
## Given a filename in the scr directory:
## build, put PDF in pdf file, clean up extraneous files
#################################################################

SOURCE_DIR = "src"
PDF_DIR = "pdfs"
cleanup_file_list = [] #list of files to delete (after NotesOnly has been compiled)

def build_pdf_parallel(task):
    build_pdf(task[0], remove_tex_after=task[1])


def build_pdf(base_filename, remove_tex_after=False):
    if dry_run:
        print("Build ", base_filename)
        return

    # go into source directory
    os.chdir(SOURCE_DIR)
    # use latexmk to build pdf - it knows how to rebuild when needed
    if build_quiet:
        # redirect output to dev null - no errors will show.
        subprocess.run(
            ["latexmk", "-pdf", base_filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(["latexmk", "-pdf", base_filename])

    # move the resulting pdf to the PDF directory
    shutil.move(
        base_filename + ".pdf", os.path.join("..", PDF_DIR, base_filename + ".pdf")
    )

    if remove_tex_after:
        os.unlink(base_filename + ".tex")
    # go back into parent directory
    os.chdir("..")



#################################################################
# Build individual sections
## Given a section number, section title, and slide type, generate a .tex file
## build it using build_pdf
#################################################################


def onesection(sectionnumber, sectionname, slidetype):
    # create the new .tex file named with section number, name, and type
    # if it already exists, overwrite
    very_base_filename = f"{sectionnumber}{sectionname}"
    if slidetype == "lecture" or slidetype == "l":
        base_filename = very_base_filename + "_lecture"
        texFile = open(os.path.join("src", base_filename) + ".tex", "w")
        texFile.write("\\documentclass[10pt]{beamer} \n\n\\usepackage{header101} \n\\usepackage{header_maps}\n \\settoggle{spoiler}{false}")
    elif slidetype == "handout" or slidetype == "h":
        base_filename = very_base_filename + "_handout"
        texFile = open(os.path.join("src", base_filename + ".tex"), "w")
        texFile.write("\\documentclass[10pt,handout]{beamer}  \n\n\\usepackage{header101} \n\\usepackage{header_maps}\n\\settoggle{spoiler}{false}")
    elif slidetype == "full" or slidetype == "f":
        base_filename = very_base_filename + "_full"
        texFile = open(os.path.join("src", base_filename + ".tex"), "w")
        texFile.write("\\documentclass[10pt]{beamer} \n\n\\usepackage{header101} \n\\usepackage{header_maps}")
    else:
        print(
            'second argument should be "beamer" or "b" for slides to show in class, "handout" or "h" for slides to give to students, or "prep" or "p" for slides with scripts and other instructor notes'
        )
        return (None, None)

    # packages and begin{document} common to all types
    texFile.write(
        " \n\n\\begin{document}\n\n"
    )
    # input the section contents
    texFile.write("\\input{sections/" + sectionnumber + ".tex}\n")
    # end tex file
    texFile.write("\\LastPage  \n\n\\end{document}")
    texFile.close()

    if delete_aux:
        return (base_filename, True)
    else:
        return (base_filename, False)


#################################################################
# Everything defined, time to get started
# put things in main to fix a mac error, as per
# https://stackoverflow.com/questions/60691363/runtimeerrorfreeze-support-on-mac
#################################################################

if __name__ == "__main__":
    # A list of files to build and then clean-up
    tasks = []

    # Make PDFs for all sections
    if print_sections:
        for type in type_list:
            for section in section_names_list:
                tasks.append(onesection(section[0], section[1], type))

    
    # Make PDFs for miscellaneous files
    if print_studentworkbook:
        tasks.append(("CLP2StudentWorkbook", False)) #never delete the .tex file
    
    # Now that we have the jobs, actually do them
    # thanks to https://stackoverflow.com/questions/41920124/multiprocessing-use-tqdm-to-display-a-progress-bar
    with Pool(number_of_processes) as p:
        list(tqdm(p.imap(build_pdf_parallel, tasks), total=len(tasks)))
    
    # Make PDF for readme - not in parallel
    if print_readme:
        PDF_DIR = "."  # ReadMe.pdf goes in the main directory
        build_pdf("ReadMe", False)
        PDF_DIR = "pdfs"  # reset the pdf directory
    
    # Make PDf for notesonly --  aux files from full version need to be present
    if print_notesonly:
        tasks=[] # in case we need to recompile
        #if there are missing aux files, compile sections to generate them
        for section in section_names_list:
            if not os.path.isfile(os.path.join(SOURCE_DIR,section[0]+section[1]+"_full.aux")):
                tasks.append(onesection(section[0], section[1], "full"))
        with Pool(number_of_processes) as p:
            list(tqdm(p.imap(build_pdf_parallel, tasks), total=len(tasks)))
        build_pdf("NotesOnly", False)

    
    # Clean up aux files
    all_base_filenames=['CLP2StudentWorkbook','NotesOnly','ReadMe']
    os.chdir(SOURCE_DIR)
    if delete_aux:
        for section in section_names_list:
            for type in type_list:
                all_base_filenames.append(section[0]+section[1]+"_"+type)
        for base_filename in all_base_filenames:
            for ext in cleanup_ext:
                if os.path.isfile(base_filename+ext):
                    os.unlink(base_filename+ext)
