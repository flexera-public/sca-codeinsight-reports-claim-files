'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Fri Mar 19 2021
File : report_data.py
'''
import logging

import CodeInsight_RESTAPIs.project.get_project_information
import CodeInsight_RESTAPIs.project.get_project_evidence


logger = logging.getLogger(__name__)

#-------------------------------------------------------------------#
def gather_data_for_report(baseURL, projectID, authToken, reportName, reportOptions):

    projectInformation = CodeInsight_RESTAPIs.project.get_project_information.get_project_information_summary(baseURL, projectID, authToken)
    projectName = projectInformation["name"]

    claimedFilePaths = [] # List to hold the file paths that contain only the evidence to be claimed
    unclaimedFilePaths = [] # List to hold the file paths that has other evidience

    # Parse report options
    takeAction = reportOptions["takeAction"] 
    evidence = reportOptions["evidence"]  
    inventoryItem = reportOptions["inventoryItem"] 

    # Get the evidence gathered
    projectEvidence = CodeInsight_RESTAPIs.project.get_project_evidence.get_project_evidence(baseURL, projectID, authToken)
    for fileEvidence in projectEvidence["data"]:
        nonClaimedEvidenceFiles = 0
        fileName = fileEvidence["fileName"]
        filePath = fileEvidence["filePath"]
        remote = fileEvidence["remote"]
        scannedFileId = fileEvidence["scannedFileId"]
        copyRightMatches = fileEvidence["copyRightMatches"]
        emailUrlMatches = fileEvidence["emailUrlMatches"]
        licenseMatches =  fileEvidence["licenseMatches"]
        searchTextMatches =  fileEvidence["searchTextMatches"]
        exactFileMatches =  fileEvidence["exactFileMatches"]
        sourceMatches =  fileEvidence["sourceMatches"]

        # See if there was any evidence at all and if so then look further
        if len(copyRightMatches) or len(emailUrlMatches) or len(licenseMatches):
            hasEvidence = True
        
            # For each file see if there is something other than what we are looking for
            # if so this file would need review since there is more too it
            for copyright in copyRightMatches:
                if evidence.lower() not in copyright.lower():
                    nonClaimedEvidenceFiles +=1
                    break

            for emailURL in emailUrlMatches:
                if evidence.lower() not in emailURL.lower():
                    nonClaimedEvidenceFiles +=1
                    break

            for license in licenseMatches:
                if evidence.lower() not in license.lower():
                    nonClaimedEvidenceFiles +=1
                    break      
        
        else:
            hasEvidence = False        
        

        # If it is just what we want to claim add it to the filePath list
        if nonClaimedEvidenceFiles == 0 and hasEvidence:
            claimedFilePaths.append(filePath)
        else:
            unclaimedFilePaths.append(filePath)


    if takeAction.lower() == "true":
        # First see if there is already an inventory item to assign the files to


        # Add the files to it
        for file in claimedFilePaths:
            logger.debug("Adding %s to %s" %(file, inventoryItem))

    
    
    # Build up the data to return for the report generation
    reportData = {}
    reportData["reportName"] = reportName
    reportData["projectName"] = projectName
    reportData["takeAction"] = takeAction
    reportData["claimedFilePaths"] = claimedFilePaths
    reportData["unclaimedFilePaths"] = unclaimedFilePaths
    
    
    return reportData