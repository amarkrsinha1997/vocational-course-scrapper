# -*- coding: utf-8 -*-
#!python3
# Script to get Information about the vocational courses available in India from the site https://www.youngbuzz.com/

import requests, bs4 , csv, json
from selenium import webdriver

#Functions that return the parsed web data in Soup form
def getUrl(url):
	try:
		return bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
	except Exception as e:
		raise e

#Write the whole data in csv format
def createCsv(dataSet):
	csvFile = open('course.csv','w+')
	#Write the details abouts the course
	csvWriter = csv.writer(csvFile)
	
	#Write the details about the colleges
	fields = ['college-name','college-address', 'college-phone']
	csvDictWriter = csv.DictWriter(csvFile,fieldnames=fields)

	for data in dataSet:
		csvWriter.writerow(data['course-eligibilty'],data['course-name'],data['course-duration'])
		csvDictWriter.writeheader()
		for college in data['colleges-info']:
			csvDictWriter.writerow(college)

	csvFile.close()

#gets the college using it's link
def getCollegeInfo(collegeLink):
	collegeDetail = {}
	#gets the parse page of the college
	collegePage = getUrl(collegeLink)
	#scrape the name of the college
	collegeName = collegePage.find('',{'class':'institute-header'}).find('h2').text
	print('Scarpping data from the college {0}.......'.format(collegeName))

	#scrape Contact and Address of the college
	collegeAddress = collegePage.find('',{'class':'contact-section'}).find('p').text
	collegePhone = [phone.text for phone in collegePage.find_all('', {'class':'phone'})]

	#Saving it in dictionary format
	collegeDetail['college-name'] = collegeName
	collegeDetail['college-address'] = collegeAddress
	collegeDetail['college-phone'] = collegePhone

	return collegeDetail

#get the details about the courses
def getCoursesDetail(course):
	
	#Scrape the name, duration of the course
	courseName = course.find('h5').text.lower()
	courseDuration = course.find('strong').text
	print('Scrapping course {0}...........'.format(courseName))
	
	#scrapes the eligiblity of the course from another link
	eligibiltyUrl = 'https://www.youngbuzz.com/iti-category/'+ '-'.join(courseName.split(' '))
	eligibiltyPage = getUrl(eligibiltyUrl)
	courseEligibilty = eligibiltyPage.find('',{'class':'info-row'}).find('p').text

	#parse the course details page for getting info about all the colleges offering the course
	courseDetailUrl = course.get('href')
	courseDetailPage = getUrl(courseDetailUrl)

	allCollegeInfo = []

	#scraping the college details and converting it in a lists
	print('Scarpping for the college details for the course {0}...........'.format(courseName))
	collegeLinks = [college.get('href') for college in courseDetailPage.find_all(class_='plain')]

	#getting the details the college that offer this course
	for collegeLink in collegeLinks:
		collegeDetail = getCollegeInfo(collegeLink)
		allCollegeInfo.append(collegeDetail)

	courseDetail = {}

	#Saving all the scrape data in dict format
	courseDetail['course-name'] = courseName
	courseDetail['course-duration'] = courseDuration
	courseDetail['course-eligibilty'] = courseEligibilty
	courseDetail['colleges-info'] = allCollegeInfo

	return courseDetail

#creating a Json file for the data
def createJson(data):
	jsonFile = open('course.json','w+')
	for jsonData in data:
		jsonFile.write(json.dump(jsonData))
	jsonFile.close()

#start function for initalizing the process
def start():

	city = input('Write the name of the city(Please mention the top city names)').lower()
	url = 'https://www.youngbuzz.com/iti/courses/'+city
	#getting the Page source when Engeering tab is active
	courseDelhiPage = getUrl(url)
	allEngineeringCourse = courseDelhiPage.find_all('', {'class':'plain'})

	#getting the Page source when Non Engeering tab is active using seleinum
	driver = webdriver.Chrome('./chromedriver')
	driver.get(url)
	driver.find_element_by_link_text('Non Engineering').click()
	allNonEngineeringCourse = bs4.BeautifulSoup(driver.page_source,'html.parser').find_all('',{'class':'plain'})
	driver.close()

	data = []

	#scrape all the courses from the website 
	print('Scarpping all Engineering courses.........')
	for course in allEngineeringCourse:
		data.append(getCoursesDetail(course))
	print('Scarpping all Non-Engineering courses.........')	
	for course in allNonEngineeringCourse:
		data.append(getCoursesDetail(course))

	print('Createing the Json file for the data.......')
	createJson(data)

	print('Createing the CSV file for the data.......')
	createCsv(data)

start()