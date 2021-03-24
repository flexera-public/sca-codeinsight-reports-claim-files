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

    fileEvidence = {} # Dict to hold evidience information for each file (claimable or not)

    # Parse report options
    takeAction = reportOptions["takeAction"] 
    stringsToClaim = reportOptions["stringsToClaim"]  
    inventoryItem = reportOptions["inventoryItem"] 
    isSearchtermClaimable = reportOptions["isSearchtermClaimable"] 
   
    # Get the evidence gathered
    projectEvidence = CodeInsight_RESTAPIs.project.get_project_evidence.get_project_evidence(baseURL, projectID, authToken)
    for evidence in projectEvidence["data"]:

        fileName = evidence["fileName"]
        filePath = evidence["filePath"]
        remote = evidence["remote"]
        scannedFileId = evidence["scannedFileId"]
        copyrightEvidienceFound = evidence["copyRightMatches"]
        emailUrlEvidenceFound = evidence["emailUrlMatches"]
        licenseEvidenceFound =  evidence["licenseMatches"]
        searchTextMatchEvidenceFound =  evidence["searchTextMatches"]
        exactFileMatchEvidenceFound =  evidence["exactFileMatches"]
        sourceMatchEvidenceFound =  evidence["sourceMatches"]

        fileEvidence[filePath] = {} # Dict to hold the data for each file
        fileEvidence[filePath]["filelink"] =  baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectID) + "&tab=workbench&view=file&fileid=" + str(scannedFileId) + "&remote=" + str(remote)

        # See if there was any evidence at all and if so then look further
        if len(copyrightEvidienceFound) or len(emailUrlEvidenceFound) or len(licenseEvidenceFound):
            fileEvidence[filePath]["hasEvidence"] = True
            fileEvidence[filePath]["claimableEvidence"] = {} # Dict to hold the data for each file
            fileEvidence[filePath]["nonclaimableEvidence"] = {} # Dict to hold the data for each file
        
            # For each file see if there is something other than what we are looking for
            # if so this file would need review since there is more too it
            for copyright in copyrightEvidienceFound:
                if stringsToClaim.lower() in copyright.lower():
                    fileEvidence[filePath]["claimableEvidence"]["copyright"] = True
                else:
                    fileEvidence[filePath]["nonclaimableEvidence"]["copyright"] = True

            for emailURL in emailUrlEvidenceFound:
                if stringsToClaim.lower() in emailURL.lower():
                    fileEvidence[filePath]["claimableEvidence"]["emailURL"] = True
                else:
                    fileEvidence[filePath]["nonclaimableEvidence"]["emailURL"] = True
      
            for license in licenseEvidenceFound:
                if stringsToClaim.lower() in license.lower():
                    fileEvidence[filePath]["claimableEvidence"]["license"] = True
                else:
                    fileEvidence[filePath]["nonclaimableEvidence"]["license"] = True

            if searchTextMatchEvidenceFound:
                fileEvidence[filePath]["searchTerm"] = True
            else:
                fileEvidence[filePath]["searchTerm"] = False 

            # With an exact match or a source match we want to make sure the file
            # cannot be claimed automatically
            if exactFileMatchEvidenceFound:
                fileEvidence[filePath]["nonclaimableEvidence"]["exactFile"] = True

            if sourceMatchEvidenceFound:
                fileEvidence[filePath]["nonclaimableEvidence"]["sourceMatch"] = True
                         
        else:
            fileEvidence[filePath]["hasEvidence"] = False


    # Now create seperate dictionaries to hold the data for each catagory
    claimableFiles = {}
    nonclaimableFiles = {}

    # Only worry about the files that contain the evidience to be claimed
    for filePath in fileEvidence:
        if fileEvidence[filePath]["hasEvidence"]:

            # Does the file contain both claimable and nonclaimable evidence?
            if fileEvidence[filePath]["claimableEvidence"] and fileEvidence[filePath]["nonclaimableEvidence"]:
                if fileEvidence[filePath]["searchTerm"]: 
                    fileEvidence[filePath]["nonclaimableEvidence"]["searchTerm"] = True
                nonclaimableFiles[filePath] = fileEvidence[filePath]
            elif fileEvidence[filePath]["claimableEvidence"]:

                # For a serach team check to see if the user wants these to be considered or not
                # prior to claiming.  If True then a search term match will not prevent the file
                # from being claimed.  Files need to be compared to see if they can be claimed 
                # already and then check against this criteria

                if isSearchtermClaimable.lower() == "true":
                    if fileEvidence[filePath]["searchTerm"]: 
                        fileEvidence[filePath]["claimableEvidence"]["searchTerm"] = True
                    claimableFiles[filePath] = fileEvidence[filePath]
                else:
                    if fileEvidence[filePath]["searchTerm"]:
                        fileEvidence[filePath]["nonclaimableEvidence"]["searchTerm"] = True
                        nonclaimableFiles[filePath] = fileEvidence[filePath]
                    else:
                        claimableFiles[filePath] = fileEvidence[filePath]
                    

    if takeAction.lower() == "true":
        # First see if there is already an inventory item to assign the files to
        takeAction = True
        for filePath in claimableFiles:
            print("Claiming %s" %filePath)
    else:
        takeAction = False

    
    # Build up the data to return for the report generation
    reportData = {}
    reportData["reportName"] = reportName
    reportData["projectName"] = projectName
    reportData["takeAction"] = takeAction
    reportData["stringsToClaim"] = stringsToClaim
    reportData["inventoryItem"] = inventoryItem
    reportData["claimableFiles"] = claimableFiles
    reportData["nonclaimableFiles"] = nonclaimableFiles
    
    
    return reportData