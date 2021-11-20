# Course Searching Tool 


This project was the final project for the course 90-819 "Intermediate Programming with Python". 

This project provides source code that can sift through potential courses conducted at Heinz
college and return critical information such as: course catalog information, faculty evaluation
information, and course scheduling information. This will allow students to access information
that is normally in three different locations in one place. The code utilizes three sources of
information: Heinz Course Catalog (webscraped), ScottyLabs Course API, and a CSV of Heinz
faculty evaluations from the last 3 years. Our functions pull information from these sources and
allow the user a multitude of options to request particular information by course number as well
as compare evaluation information between two different course numbers. To do this analysis
we used the following libraries: pandas, BeautifulSoup, json, re (regular expression), requests,
os.path.


## Individual Contribution to this Project

I specificially worked on developing the "getHeinzCourseCatalog", "menu", "menu_execution" and "main" functions found in the .py file. For more information on the functionality provided by the aforementioned functions, please visit the "Documentation.pdf" file.
