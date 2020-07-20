#!/usr/bin/env python
# This script scrapes property type by address from Century21

from csv import reader, writer
from getopt import getopt, GetoptError
from os import path
from random import randint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sys import argv, exit


def usage():
    print (
        "Usage:\n"
        "-h, --help\tPrint help info\n"
        "-f, --filename\tInput CSV filename\n"
    )


def getOpts():
    try:
        opts, args = getopt(argv[1:], "hf:", ["help", "filename="])
    except GetoptError as err:
        print (err)
        usage()
        exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit(0)
        elif opt in ("-f", "--filename"):
            filename = arg
        else:
            assert False, "unhandled option"
    # Make sure filename is specified and file exists
    if "filename" not in locals() or not path.exists(filename):
        usage()
        exit(1)
    return filename


def getPropertyType(address):
    print "\nChecking address: %s" % address
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(chrome_options=options)
        driver.get("https://www.century21.com/")
        # Mimic human behavior by randomizing movement interval
        driver.implicitly_wait(randint(2, 5))
        driver.find_element_by_id("searchText").clear()
        driver.implicitly_wait(randint(2, 5))
        driver.find_element_by_id("searchText").send_keys(address)
        driver.implicitly_wait(randint(2, 5))
        driver.find_element_by_id("free-text-search-button").click()
        # Wait needed in headless mode to ensure page rendered
        driver.implicitly_wait(8)
        try:
            description = driver.find_element_by_id("propertyDescCollapse").text
            res = description.split(" - ")[0]
        # Most errors are caused by obsolete properties which are no longer listed
        except NoSuchElementException:
            if (
                "We do not have any results matching"
                in driver.find_element_by_id("dropDownNotification").text
            ):
                res = "Not Found"
        driver.quit()
        print res
        return res
    except Exception as ex:
        print ex
        return "Error"


def processFile(filename):
    outputFilename = "output_" + filename
    if path.exists(outputFilename):
        bookmark = len(open(outputFilename).readlines())
    else:
        bookmark = 0
    with open(filename, "r") as fileReader:
        csvReader = reader(fileReader)
        for row in csvReader:
            # Resume from where left at during last run
            if csvReader.line_num <= bookmark:
                continue
            # Save output file line by line
            with open(outputFilename, "a") as fileWriter:
                csvWriter = writer(fileWriter)
                # Write header
                if csvReader.line_num == 1:
                    row.append("Property Type")
                else:
                    # 2nd col street address, 3rd col zip code
                    address = row[1] + ", " + row[2]
                    row.append(getPropertyType(address))
                csvWriter.writerow(row)


def main():
    filename = getOpts()
    processFile(filename)


if __name__ == "__main__":
    main()
