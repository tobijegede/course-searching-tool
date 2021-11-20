#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:40:44 2020

@author: tobijegede
"""

#importing all of the required modules
import pandas as pd 
import json
import requests
from bs4 import BeautifulSoup
import re
import sys

#Used to check if a file already exists
import os.path
from os import path
pd.set_option('display.max_columns', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)

#Trial Course Numbers to Use: 
    #90-717 (Writing for Public Policy)
    #90-718 (Strategic Presenttation Skills)
    #90-777 (Intermediate Statistic)
    

#This function take the csv of course evaluation that the user should already have on their computer
#and reads it in to a dataframe
def csv_func(course_num):
    
    #Checks to see if the file is on the computer; if so, it reads it into a dataframe called eval:
    try:
        eval= pd.read_csv('Course_Evaluation_Results.csv', encoding= 'unicode_escape')
    except FileNotFoundError:
        print('Course_Evaluation_Results.csv not found')
        sys.exit()
    
    code=int(course_num)
    
    #Renames the columns in the eval dataframe:
    eval=eval.rename(columns={'Sem':'Semester','Num':'Course_Code',
                              'CourseName':'Course_Name',
                              'Clearly explain course requirements':'Clearly explains course requirements',
                              'Clear learning objectives & goals':'Explicit Learning Objectives & Goal',
                              'Instructor provides feedback to students to improve':'Constructive Feedback from Instructor', 
                              'Demonstrate importance of subject matter':'Demonstrates importance of subject matter',
                              'Explains subject matter of course':'Explanation of Course Content',
                              'Show respect for all students':'Shows respect for all students'})
   
    eval=eval.dropna(subset=['Course_Code','Division','Year'])      #https://www.w3resource.com/pandas/dataframe/dataframe-dropna.php
    eval['Course_Code']=eval['Course_Code'].astype(int)
    #Makes the course_code the index:
    eval=eval.set_index('Course_Code')                        
    #Reorders the columns:
    eval=eval[['Course_Name','Year', 'Semester', 'Instructor', 'Dept',
               'Hrs Per Week',
               'Overall teaching rate', 'Overall course rate']]
    #Converts all faculty names to upper case:
    eval['Instructor'] = eval['Instructor'].str.upper()
    eval['Year']=eval['Year'].astype(int)
    eval= eval.loc[eval['Year']>=2017]
    op=eval.loc[code]
    
    #print(op)
    return op


   
#This function webscarpes the Heinz Course Catalog and returns a list that contains 
#course number, course name, number of unity, course description, course outcomes, prerequisites, and any syllabi by professor
def getHeinzCourseCatalog(course_num):
       
    #Go to the url 
    course_website = 'https://api.heinz.cmu.edu/courses_api/course_detail/' + course_num
    page = requests.get(course_website)
   
    #Scraping:
    
    #Parse the page
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Pulls the entire html file for the specific course number 
    course_page = soup.find(id="container-fluid")
  

    #Checks if the course number is a real course number
    if course_page == None: 
        return None
       
    #Pulls the section header html code for Units, Description, Learning Outcomes, Prereqs and Syllabus
    course_elements= course_page.find_all("p")
    course_features = []
    for element in course_elements:
        header = element.get_text()
        course_features.append(header)
    
    #Assigning the list to variable names
    class_name = course_features[0]
    #removing class name from course_features
    course_features = course_features[1:]
    
    desc_pattern = r'^(Description:)'
    course_units = ''
    course_loutcomes = 'None'
    course_prereqs = 'None'
    course_syl = 'None'
    syllabi = {} #empty dictionary for courses with syllabi
    pattern = '\([-0-9a-zA-z\s]*' #pattern for finding Professor names
    
    #Extracts the relevant information from the html code
    for feature in course_features:
        if 'Units' in feature:
            course_units = feature[-2:]
            course_units = int(course_units)
        elif re.search(desc_pattern,feature) != None:
           course_desc = feature[13:]
        elif 'Learning Outcomes:' in feature:
            course_loutcomes = feature[19:]
        elif 'Prerequisites Description:' in feature:
            course_prereqs = feature[26:]
            
        else:
            course_syl = feature
           
        
    #Finds the information contained about syllabus on the course_page
    syllabus = course_page.select('a')
    
    
    #Sets the syllabi dictionary where the key is the instructor and the value is the link tot he syllabi
    if len(syllabus) == 0: #no syllabi on the course page
        syllabi[None] = 'None'
    if len(syllabus) == 1: #one syllabi on the course page
        syllabus_link = 'https://api.heinz.cmu.edu' + syllabus[0].get('href')
        str_syllabus = str(syllabus)
        syllabus_prof = re.findall(pattern, str_syllabus)
        string = syllabus_prof[0]
        string = string[1:-1]
        string = string.split(' ')
        string = string[1] + ', ' + string[0] #reorganizes the name so the instructor last name is first (Ex: Lastname, Firstname)
        syllabi[string] = syllabus_link
    if len(syllabus) > 1: #many syllabi on the course page
        for syl in syllabus:
            syllabus_link = 'https://api.heinz.cmu.edu' + syl.get('href')
            str_syl = str(syl)
            syllabus_prof = re.findall(pattern, str_syl)

            string = syllabus_prof[0]
            string = string[1:-1]
            string = string.split(' ')
            string = string[1] + ', ' + string[0] #reorganizes the name so the instructor last name is first (Ex: Lastname, Firstname)
          
            syllabi[string] = syllabus_link
    
   
    #Pulls together all of the information generated in this function into a list and returns that list
    course_details = [course_num, class_name, course_units, course_desc, course_loutcomes, course_prereqs, course_syl, syllabi]
    return course_details



#Assuming that the user has already inputted a course number, this function gets the number of the menu option that the user inputs, 
#converts that input into an integer and makes sure it's valid before returning the menu option selected
def menu():

 
    #Prompts the user for menu option number:
    request = input('''Please type in the number for the menu item that you want:
                    0: Quit 
                    1: Course Time & Instructor for Each Time
                    2: Department Code for the Course
                    3: Course Evaluation Information
                    4: Course Overview (Course Name, Description, and # of Units)
                    5: All Course Information
                    6: Course Syllabi
                    7: Request a New Course Number
                    8: Comparison of Two Different Course
                    ''' )

    #Change the inputted string value to an integer value:
    request_code = int(request)

    #Creates a list of integers with the range of allowable values for the menu
    #creates list of allowable menu options:
    menu_options = [i for i in range(9)]

    #Checks to see if the user input is valid and prints an error message if not:
    while request_code not in menu_options:
        print("Error - please enter a valid menu option.")
        request = input('''Please type in the number for the menu item that you want:
                        0: Quit 
                        1: Course Time & Instructor for Each Time
                        2: Course Department
                        3: Course Evaluation Information
                        4: Course Overview (Course Name, Description, and # of Units)
                        5: All Available Course Information
                        6: Course Syllabi
                        7: Request a New Course Number
                        8: Comparison of Two Different Course
                        ''' )
        request_code = int(request)




    return request_code



#This function takes the menu option and the course_num selected and returns the desired information
def menu_execution(course_num,request_code):

    #Allows the user to quit:
    if request_code == 0:
        print("\n Thanks for using our platform! Have a good day!")
        return 
    
    #Executes request1 function to print the section, day, time, instructor, class room, and campus:
    if request_code == 1: 
        request1(course_num)
        #Repeats menu options:
        option = menu()
        menu_execution(course_num,option)
    
    #Executes request2 function to print the department code of the course:
    if request_code == 2: 
        request2(course_num)
        #Repeats menu options:
        option = menu()
        menu_execution(course_num,option)
    
    #Executes request3 function and prints Faculty course evaluation information for the requested course number:
    if request_code == 3: 
        request3(course_num)
        option = menu()
        menu_execution(course_num,option)
    
    #Prints Course Overview with course name, description, and number of units:
    if request_code == 4:
        course_catalog_info = getHeinzCourseCatalog(course_num)
        if course_catalog_info == None:
            print('Sorry, the course you requested information for does not exist')
        if course_catalog_info != None:
            course_overview = [course_catalog_info[1], course_catalog_info[3], course_catalog_info[2]]
            print('''Course Overview:
                 Course Number: %s
                 Course Name: %s
                 Course Description: %s
                 Course Units: %d
              ''' % (course_num, course_overview[0], course_overview[1], course_overview[2]))
        #Repeats menu options:
        option = menu()
        menu_execution(course_num,option)
    
    #Prints all available course information:
    if request_code == 5:
        course_catalog_info = getHeinzCourseCatalog(course_num)
           
        #Checks to make sure course catalog information exists and prints an error message if not
        if course_catalog_info == None:
            print('Sorry, the course you requested information for does not exist')
            #Repeats menu options:
            option = menu()
            menu_execution(course_num,option)
        else:
            print('All Available Course Information:')
            for i in range(len(course_catalog_info)-1): #prints all information associated with request 4 except the syllabi
                print(course_catalog_info[i])
            syllabi_pull(course_num) #exectues syllabi_pull function and prints syllabi information by professor
            print()
            request2(course_num) #exectes request2 function to print department code
            print()
            request1(course_num) #exectues request1 function to print the section, day, time, instructor, class room, and campus
            print()
            request3(course_num) #executes request3 function to print faculty evaluation information
            #Repeats menu options:
            option = menu()
            menu_execution(course_num,option)
    
    #Prints all available syllabi by professor
    if request_code == 6: 
        course_catalog_info = getHeinzCourseCatalog(course_num)
        #Checks to make sure the course is in the Heinz catalog
        if course_catalog_info == None:
            print('Sorry, the course you requested information for does not exist')
            menu()
        #Get the syllabi dictionary out of course_catalog_info
        if course_catalog_info != None: 
            syllabi = course_catalog_info[-1]
            #Checks to see of the the dictionary has any syllabi and if so prints the syllabi link by professor
            if None in syllabi.keys():
                print('There are no available syllabi for this course')
            else:
                print('''\n Here is a list of all available syllabi for this course, and the corresponding professors: \n''')
                for key in syllabi:
                    print(key + ': ' + syllabi[key])
        #Repeats menu options:
        option = menu()
        menu_execution(course_num,option)
        
    #Allows the user to utlize the menu with a new course number
    if request_code == 7:  # Enter a new course number
        main()
    
    #Allows the user to compare the factulty of evaluation with another course
    if request_code == 8:
        #Asks the user for a second course_number for which they want to compare
        course_num2 = input('Enter another course number in the valid format (XX-XXX) whose evaluations you would like to compare with the course ' + course_num + ': ')
        #Prints the facutly evaluation of the course number already in the system:
        request3(course_num)
        print() #gives a space between the evaluations
        #Prints the factuly evalution of the second course number:
        request3(course_num2)
        #Repeats menu options:
        option = menu()
        menu_execution(course_num,option)
 



#Defines menu request functions used in menu_execution function:
 
#Request 1 pulls section info (time, instructor, location, etc.) from Schedule of Classes (fall 2019)
def request1(course_num):
    if course_num not in schedule.index:
        print('Sorry, there is no schedule information for this course in Fall 2019')
    else:
        name = schedule.loc[course_num]['name']
        lectures = schedule.loc[course_num]['lectures']
        days_dict= {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
        print('Times and Instructor(s) for %s:' %(name))
        for lecture in lectures:
            print(lecture['instructors'][0])
            print('\t Section: %s' %(lecture['name']))
            for time in lecture['times']:
                print('\t Day(s): %s' %((', ').join(list(map(lambda x: days_dict[x], time['days'])))))
                print('\t Time: %s - %s' %(time['begin'], time['end']))
                print('\t Location: %s %s' %(time['building'], time['room']))
                print('\t Campus: %s' %(time['location']))
    
    
#Request 2 pulls department name from Schedule of Classes (fall 2019)
def request2(course_num):
    if course_num not in schedule.index:
        print('Sorry, there is no department information for this course')
    else:
        department = schedule.loc[course_num]['department']
        print('Course Department:')
        print(department)
        
#Request 3 pulls all the Faculty course evaluation information for the requested course number 
def request3(course_num):
    #removes the “-” character in the course number 
    new_course_num = course_num[0:2] + course_num[3:]
    try:
        eval = csv_func(new_course_num)  
        #Semester, Year, Instructor, Overall Course Rate
        print('Faculty Course Evaluation')
        print(eval)
    except KeyError:
        print('Sorry, the information you requested does not exist')

# Pulls the syllabi dictionary out of the list returned from getHeinzCourseCatalog functions and prints syllabi link by professor      
def syllabi_pull(course_num):
    course_catalog_info = getHeinzCourseCatalog(course_num)
    if course_catalog_info == None:
        print('Sorry, the course you requested information for does not exist')
        menu()
    syllabi = course_catalog_info[-1]
    if None in syllabi.keys():
        print('There are no available syllabi for this course')
    else:
        print('''\n Here is a list of all available syllabi for this course, and the corresponding professors: \n''')
        for key in syllabi:
            print(key + ': ' + syllabi[key])


def main():
    
    #Ask the user for a course number:
    course_num = input('''Welcome to the Golden Girls Course Searching Platform! To get started, please enter a course number (XX-XXX): ''')


    #Checks to see if the course number is in the correct format:            
    pattern = r'^([0-9][0-9])\-([0-9]{3})$'
    while re.search(pattern, course_num) == None:        
        print('Error - Please enter a valid format for a course number')
        course_num = input('''Welcome to the Golden Girls Course Searching Platform! To get started, please enter a course number (XX-XXX): ''')
        
    #Executes the menu_execution function which will get the desired information of the course based on the menu option selected
    menu_execution(course_num,menu())
    
   
  
    
#Controls the number of times that this code is run by checking if the .json already exists
if path.exists("filtered_courses.json") == False:
    
          
    #Connect to ScottyLabs API - This should only be done as few times as possible!
    response = requests.get("https://apis.scottylabs.org/course/courses")
    print(response.status_code)

    all_courses = json.loads(response.text)

    #Retrieve only courses that start with the number 9
    filtered_courses = [course for course in all_courses if course['courseID'].startswith('9')]

    with open("filtered_courses.json", "w") as f:
        json.dump(filtered_courses, f) 
    #Read json file into dataframe    
    schedule = pd.read_json("filtered_courses.json")
    
    #Keep only Heinz courses (course numbers prefixes between 90 and 95)
    pattern= r'^[9][0-5]'   
    schedule_filtered = schedule[schedule['courseID'].str.contains(pattern)]
 
    ##Deleting unnecessary columns
    #drop co-reqs column
    schedule_filtered.drop('coreqs', axis=1, inplace=True)
    #drop description
    schedule_filtered.drop('desc', axis=1, inplace=True)
    #drop prereqs
    schedule_filtered.drop('prereqs', axis=1, inplace=True)
    #drop units
    schedule_filtered.drop('units', axis=1, inplace=True)
    
    #Set index to Course ID
    schedule = schedule_filtered.set_index('courseID') 
else: 
    
    #Read json file into dataframe    
    schedule = pd.read_json("filtered_courses.json")
    
    #Keep only Heinz courses (course numbers prefixes between 90 and 95)
    pattern= r'^[9][0-5]'   
    schedule_filtered = schedule[schedule['courseID'].str.contains(pattern)]
 
    ##Deleting unnecessary columns
    #drop co-reqs column
    schedule_filtered.drop('coreqs', axis=1, inplace=True)
    #drop description
    schedule_filtered.drop('desc', axis=1, inplace=True)
    #drop prereqs
    schedule_filtered.drop('prereqs', axis=1, inplace=True)
    #drop units
    schedule_filtered.drop('units', axis=1, inplace=True)
    
    #Set index to Course ID
    schedule = schedule_filtered.set_index('courseID') 
    

    
    
if __name__ == '__main__': 
    main() 