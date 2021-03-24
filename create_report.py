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
import json

import _version
import report_data
import report_artifacts


###################################################################################
# Test the version of python to make sure it's at least the version the script
# was tested on, otherwise there could be unexpected results
if sys.version_info <= (3, 5):
    raise Exception("The current version of Python is less than 3.5 which is unsupported.\n Script created/tested against python version 3.8.1. ")
else:
    pass

logfileName = os.path.dirname(os.path.realpath(__file__)) + "/_claim-evidence_report.log"

###################################################################################
#  Set up logging handler to allow for different levels of logging to be capture
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', filename=logfileName, filemode='w',level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
    baseURL = args.baseURL

    # Create a dictionary for the report options
    # since argparse removes quotes json.load won't work
    # Split and remove the passed {} as well
    reportOptions = {}
    for keyValuePair in args.reportOptions[1:-1].split(','):
        key, value = keyValuePair.split(':')
        reportOptions[key] = value


   
    #verifyOptions(reportOptions) 

    logger.debug("Custom Report Provided Arguments:")	
    logger.debug("    projectID:  %s" %projectID)	
    logger.debug("    reportID:   %s" %reportID)	
    logger.debug("    baseURL:  %s" %baseURL)	
    logger.debug("    reportOptions:  %s" %reportOptions)	


    reportData = report_data.gather_data_for_report(baseURL, projectID, authToken, reportName, reportOptions)
    reports = report_artifacts.create_report_artifacts(reportData)

    

#----------------------------------------------------------------------# 
def verifyOptions(reportOptions):
    '''
    Expected Options for report:
        takeAction - True/False
        evidence - String Value
    '''

    takeAction = str(reportOptions["options"]["takeAction"])

    if takeAction.lower() not in ["true", "false"]:
        print("No good")





#----------------------------------------------------------------------#    
if __name__ == "__main__":
    main()  