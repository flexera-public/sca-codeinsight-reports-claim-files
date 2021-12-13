'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Tue Mar 16 2021
File : create_report.py
'''
import sys
import logging
import argparse
import os
import zipfile
import json
from datetime import datetime
import re


import _version
import report_data
import report_artifacts
import report_errors
import CodeInsight_RESTAPIs.project.upload_reports

###################################################################################
# Test the version of python to make sure it's at least the version the script
# was tested on, otherwise there could be unexpected results
if sys.version_info <= (3, 5):
    raise Exception("The current version of Python is less than 3.5 which is unsupported.\n Script created/tested against python version 3.8.1. ")
else:
    pass

propertiesFile = "../server_properties.json"  # Created by installer or manually
propertiesFile = logfileName = os.path.dirname(os.path.realpath(__file__)) + "/" +  propertiesFile
logfileName = os.path.dirname(os.path.realpath(__file__)) + "/_claim-files_report.log"

###################################################################################
#  Set up logging handler to allow for different levels of logging to be capture
logging.basicConfig(format='%(asctime)s,%(msecs)-3d  %(levelname)-8s [%(filename)-30s:%(lineno)-4d]  %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', filename=logfileName, filemode='w',level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Disable logging for requests module


####################################################################################
# Create command line argument options
parser = argparse.ArgumentParser()
parser.add_argument('-pid', "--projectID", help="Project ID")
parser.add_argument("-rid", "--reportID", help="Report ID")
parser.add_argument("-authToken", "--authToken", help="Code Insight Authorization Token")
parser.add_argument("-baseURL", "--baseURL", help="Code Insight Core Server Protocol/Domain Name/Port.  i.e. http://localhost:8888 or https://sca.codeinsight.com:8443")
parser.add_argument("-reportOpts", "--reportOptions", help="Options for report content")

#----------------------------------------------------------------------#
def main():

    reportName = "Claimed Files Report"

    logger.info("Creating %s - %s" %(reportName, _version.__version__))
    print("Creating %s - %s" %(reportName, _version.__version__))

    # See what if any arguments were provided
    args = parser.parse_args()
    projectID = args.projectID
    reportID = args.reportID
    authToken = args.authToken
    reportOptions = args.reportOptions

    fileNameTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    #####################################################################################################
    #  Code Insight System Information
    #  Pull the base URL from the same file that the installer is creating
    if os.path.exists(propertiesFile):
        try:
            file_ptr = open(propertiesFile, "r")
            configData = json.load(file_ptr)
            baseURL = configData["core.server.url"]
            file_ptr.close()
            logger.info("Using baseURL from properties file: %s" %propertiesFile)
        except:
            logger.error("Unable to open properties file: %s" %propertiesFile)
    else:
        baseURL = "http://localhost:8888"   # Required if the core.server.properties files is not used
        logger.info("Using baseURL from create_report.py")


    # Based on how the shell pass the arguemnts clean up the options if on a linux system:w
    if sys.platform.startswith('linux'):
        reportOptions = reportOptions.replace('""', '"')[1:-1]

    reportOptions = json.loads(reportOptions)
   
    reportOptions = verifyOptions(reportOptions) 

    logger.debug("Custom Report Provided Arguments:")	
    logger.debug("    projectID:  %s" %projectID)	
    logger.debug("    reportID:   %s" %reportID)	
    logger.debug("    baseURL:  %s" %baseURL)	
    logger.debug("    reportOptions:  %s" %reportOptions)	

    if "errorMsg" in reportOptions.keys():
        reportFileNameBase = reportName.replace(" ", "_") + "-Creation_Error-" + fileNameTimeStamp

        reportData = {}
        reportData["errorMsg"] = reportOptions["errorMsg"]
        reportData["reportName"] = reportName
        reportData["reportTimeStamp"] = datetime.strptime(fileNameTimeStamp, "%Y%m%d-%H%M%S").strftime("%B %d, %Y at %H:%M:%S")
        reportData["reportFileNameBase"] = reportFileNameBase

        reports = report_errors.create_error_report(reportData)
        print("    *** ERROR  ***  Error found validating report options")
    else:
        reportData = report_data.gather_data_for_report(baseURL, projectID, authToken, reportName, reportOptions)
        print("    Report data has been collected")
        
        projectName = reportData["projectName"]
        projectNameForFile = re.sub(r"[^a-zA-Z0-9]+", '-', projectName )  # Remove special characters from project name for artifacts
        
        reportFileNameBase = projectNameForFile + "-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp

        reportData["projectNameForFile"] = projectNameForFile
        reportData["reportTimeStamp"] = datetime.strptime(fileNameTimeStamp, "%Y%m%d-%H%M%S").strftime("%B %d, %Y at %H:%M:%S")
        reportData["reportFileNameBase"] = reportFileNameBase

        if "errorMsg" in reportData.keys():
            reports = report_errors.create_error_report(reportData)
            print("    Report artifacts have been created")
        else:
            reports = report_artifacts.create_report_artifacts(reportData)
            print("    Report artifacts have been created")

    
    print("    Create report archive for upload")
    uploadZipfile = create_report_zipfile(reports, reportFileNameBase)
    print("    Upload zip file creation completed")
    CodeInsight_RESTAPIs.project.upload_reports.upload_project_report_data(baseURL, projectID, reportID, authToken, uploadZipfile)
    print("    Report uploaded to Code Insight")
    
	#########################################################
	# Remove the file since it has been uploaded to Code Insight
    try:
        os.remove(uploadZipfile)
    except OSError:
        logger.error("Error removing %s" %uploadZipfile)
        print("Error removing %s" %uploadZipfile)

    logger.info("Completed creating %s" %reportName)
    print("Completed creating %s" %reportName)


#----------------------------------------------------------------------# 
def verifyOptions(reportOptions):
    '''
    Expected Options for report:
        takeAction - True/False
        stringsToClaim
        isSearchTermClaimable
        inventoryItemForClaimedFiles
    '''
    reportOptions["errorMsg"] = []
    trueOptions = ["true", "t", "yes", "y"]
    falseOptions = ["false", "f", "no", "n"]

    takeAction = reportOptions["takeAction"]

    if takeAction.lower() in trueOptions:
        reportOptions["takeAction"] = "true"
    elif takeAction.lower() in falseOptions:
        reportOptions["takeAction"] = "false"
    else:
        reportOptions["errorMsg"].append("Invalid option for taking action: <b>%s</b>.  Valid options are <b>True/False</b>" %takeAction)
    
    isSearchTermClaimable = reportOptions["isSearchTermClaimable"]

    if isSearchTermClaimable.lower() in trueOptions:
        reportOptions["isSearchTermClaimable"] = "true"
    elif isSearchTermClaimable.lower() in falseOptions:
        reportOptions["isSearchTermClaimable"] = "false"
    else:
        reportOptions["errorMsg"].append("Invalid options for claiming items with search terms: <b>%s</b>.  Valid options are <b>True/False</b>" %isSearchTermClaimable)


    if not reportOptions["errorMsg"]:
        reportOptions.pop('errorMsg', None)

    return reportOptions


#---------------------------------------------------------------------#
def create_report_zipfile(reportOutputs, reportFileNameBase):
    logger.info("Entering create_report_zipfile")

    allFormatZipFile = reportFileNameBase + ".zip"
    # create a ZipFile object
    allFormatsZip = zipfile.ZipFile(allFormatZipFile, 'w', zipfile.ZIP_DEFLATED)


    logger.debug("    Create downloadable archive: %s" %allFormatZipFile)
    print("        Create downloadable archive: %s" %allFormatZipFile)
    for format in reportOutputs["allFormats"]:
        print("            Adding %s to zip" %format)
        logger.debug("        Adding %s to zip" %format)
        allFormatsZip.write(format)

    allFormatsZip.close()
    logger.debug("    Downloadable archive created")
    print("        Downloadable archive created")

    # Now create a temp zipfile of the zipfile along with the viewable file itself
    uploadZipflle = allFormatZipFile.replace(".zip", "_upload.zip")
    print("        Create zip archive containing viewable and downloadable archive for upload: %s" %uploadZipflle)
    logger.debug("    Create zip archive containing viewable and downloadable archive for upload:")
    logger.debug("        %s" %uploadZipflle)
    
    zipToUpload = zipfile.ZipFile(uploadZipflle, 'w', zipfile.ZIP_DEFLATED)

    zipToUpload.write(reportOutputs["viewable"])
    zipToUpload.write(allFormatZipFile)
    zipToUpload.close()
    logger.debug("    Archive zip file for upload has been created")
    print("        Archive zip file for upload has been created")

    # Clean up the items that were added to the zipfile
    try:
        os.remove(allFormatZipFile)
    except OSError:
        logger.error("Error removing %s" %allFormatZipFile)
        print("Error removing %s" %allFormatZipFile)
        return -1

    for fileName in reportOutputs["allFormats"]:
        try:
            os.remove(fileName)
        except OSError:
            logger.error("Error removing %s" %fileName)
            print("Error removing %s" %fileName)
            return -1    

    logger.info("Exiting create_report_zipfile")
    return uploadZipflle



#----------------------------------------------------------------------#    
if __name__ == "__main__":
    main()  