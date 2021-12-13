'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Mon Dec 13 2021
File : report_artifacts_html.py
'''
import logging
import os
import base64

import _version

logger = logging.getLogger(__name__)

#------------------------------------------------------------------#
def generate_html_report(reportData):
    logger.info("    Entering generate_html_report")

    reportName = reportData["reportName"]
    projectName = reportData["projectName"]
    reportFileNameBase = reportData["reportFileNameBase"]
    reportTimeStamp =  reportData["reportTimeStamp"] 
    takeAction = reportData["takeAction"]
    stringsToClaim = reportData["stringsToClaim"]
    inventoryItemForClaimedFiles = reportData["inventoryItemForClaimedFiles"]
    claimableFiles = reportData["claimableFiles"]
    nonclaimableFiles = reportData["nonclaimableFiles"]
   
    scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    cssFile =  os.path.join(scriptDirectory, "report_branding/css/revenera_common.css")
    logoImageFile =  os.path.join(scriptDirectory, "report_branding/images/logo_reversed.svg")
    iconFile =  os.path.join(scriptDirectory, "report_branding/images/favicon-revenera.ico")
    statusApprovedIcon = os.path.join(scriptDirectory, "report_branding/images/status_approved_selected.png")
    statusRejectedIcon = os.path.join(scriptDirectory, "report_branding/images/status_rejected_selected.png")
    statusDraftIcon = os.path.join(scriptDirectory, "report_branding/images/status_draft_ready_selected.png")

    logger.debug("cssFile: %s" %cssFile)
    logger.debug("imageFile: %s" %logoImageFile)
    logger.debug("iconFile: %s" %iconFile)
    logger.debug("statusApprovedIcon: %s" %statusApprovedIcon)
    logger.debug("statusRejectedIcon: %s" %statusRejectedIcon)
    logger.debug("statusDraftIcon: %s" %statusDraftIcon)

    #########################################################
    #  Encode the image files
    encodedLogoImage = encodeImage(logoImageFile)
    encodedfaviconImage = encodeImage(iconFile)

    htmlFile = reportFileNameBase + ".html"
    logger.debug("htmlFile: %s" %htmlFile)
    
    #---------------------------------------------------------------------------------------------------
    # Create a simple HTML file to display
    #---------------------------------------------------------------------------------------------------
    try:
        html_ptr = open(htmlFile,"w")
    except:
        logger.error("Failed to open htmlfile %s:" %htmlFile)
        raise

    html_ptr.write("<html>\n") 
    html_ptr.write("    <head>\n")

    html_ptr.write("        <!-- Required meta tags --> \n")
    html_ptr.write("        <meta charset='utf-8'>  \n")
    html_ptr.write("        <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'> \n")

    html_ptr.write(''' 
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.1/css/bootstrap.min.css" integrity="sha384-VCmXjywReHh4PwowAiWNagnWcLhlEJLA5buUprzK8rxFgeH0kww/aWY76TfkUoSX" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
    ''')


    html_ptr.write("        <style>\n")

    # Add the contents of the css file to the head block
    try:
        f_ptr = open(cssFile)
        logger.debug("Adding css file details")
        for line in f_ptr:
            html_ptr.write("            %s" %line)
        f_ptr.close()
    except:
        logger.error("Unable to open %s" %cssFile)
        print("Unable to open %s" %cssFile)


    html_ptr.write("        </style>\n")  

    html_ptr.write("    	<link rel='icon' type='image/png' href='data:image/png;base64, {}'>\n".format(encodedfaviconImage.decode('utf-8')))
    html_ptr.write("        <title>%s</title>\n" %(reportName))
    html_ptr.write("    </head>\n") 

    html_ptr.write("<body>\n")
    html_ptr.write("<div class=\"container-fluid\">\n")

    #---------------------------------------------------------------------------------------------------
    # Report Header
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN HEADER -->\n")
    html_ptr.write("<div class='header'>\n")
    html_ptr.write("  <div class='logo'>\n")
    html_ptr.write("    <img src='data:image/svg+xml;base64,{}' style='width: 400px;'>\n".format(encodedLogoImage.decode('utf-8')))
    html_ptr.write("  </div>\n")
    html_ptr.write("<div class='report-title'>%s</div>\n" %reportName)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END HEADER -->\n")

    #---------------------------------------------------------------------------------------------------
    # Body of Report
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN BODY -->\n") 

    html_ptr.write("<div class=\"container-fluid\">\n")
    if takeAction:
        html_ptr.write("<h2>String evidence that has been claimed</h2>\n")
    else:
        html_ptr.write("<h2>String evidence that is claimable</h2>\n")
    html_ptr.write("<ul>\n")
    
    for string in stringsToClaim:
        html_ptr.write("<li>%s</li>\n"%string)
    html_ptr.write("</ul'>\n")
    html_ptr.write("</div>\n")

    html_ptr.write("<hr class='small'>")

    html_ptr.write("<table id='claimableFiles' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    if takeAction:
        html_ptr.write("            <th colspan='10' class='text-center'><h4>%s - Files claimed and added to %s</h4></th>\n" %(projectName, inventoryItemForClaimedFiles))
    else:
        html_ptr.write("            <th colspan='10' class='text-center'><h4>%s - Files that are claimable</h4></th>\n" %projectName) 

    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th style='width: 50%' class='text-left text-nowrap'>File Path</th>\n") 
    if takeAction:
        html_ptr.write("            <th style='width: 10%' class='text-center'>Claimed Copyright</th>\n") 
        html_ptr.write("            <th style='width: 10%' class='text-center'>Claimed Email/URL</th>\n") 
    else:
        html_ptr.write("            <th style='width: 10%' class='text-center'>Claimable Copyright</th>\n") 
        html_ptr.write("            <th style='width: 10%' class='text-center'>Claimable Email/URL</th>\n")
    html_ptr.write("            <th style='width: 10%' class='text-center'>Search Terms</th>\n")
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  

    for filePath in sorted(claimableFiles):

        filelink = claimableFiles[filePath]["filelink"]

        html_ptr.write("        <tr> \n")
        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(filelink, filePath))

        for evidence in ["copyright", "emailURL", "searchTerm"]:
            # See if the evidence exists.  If the key is not there that type was not found
            if evidence in claimableFiles[filePath]["claimableEvidence"]:
                html_ptr.write("            <td class='text-center text-nowrap' style='vertical-align: middle;'><span class='dot dot-%s'></span></td>\n" %evidence)
            else:
                html_ptr.write("            <td>&nbsp</td>\n")

        html_ptr.write("        </tr>\n") 

    html_ptr.write("    </tbody>\n")
    html_ptr.write("</table>\n")  
    
    html_ptr.write("<hr class='small'>")

    html_ptr.write("<table id='nonclaimableFiles' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='10' class='text-center'><h4>%s - Files with Claimable and Other Evidence</h4></th>\n" %projectName) 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th style='width: 50%' class='text-left text-nowrap'>File Path</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>Claimable Copyright</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>Claimable Email/URL</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>Other Copyright</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>Other Email/URL</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>License</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>Search Terms</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>Exact File Match</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>Source Code Match</th>\n")
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  

    for filePath in sorted(nonclaimableFiles):

        filelink = nonclaimableFiles[filePath]["filelink"]
        
        html_ptr.write("        <tr> \n")
        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(filelink, filePath))

        for evidence in ["copyright", "emailURL"]:
            # See if the evidence exists.  If the key is not there that type was not found
            if evidence in nonclaimableFiles[filePath]["claimableEvidence"]:
                html_ptr.write("            <td class='text-center text-nowrap' style='vertical-align: middle;'><span class='dot dot-%s'></span></td>\n" %evidence)
            else:
                html_ptr.write("            <td>&nbsp</td>\n")
        
        for evidence in ["copyright", "emailURL", "license",  "searchTerm", "sourceMatch", "exactFile"]:
            # See if the evidence exists.  If the key is not there that type was not found
            if evidence in nonclaimableFiles[filePath]["nonclaimableEvidence"]:
                html_ptr.write("            <td class='text-center text-nowrap' style='vertical-align: middle;'><span class='dot dot-%s'></span></td>\n" %evidence)
            else:
                html_ptr.write("            <td>&nbsp</td>\n")

        html_ptr.write("        </tr>\n") 

    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n")  




    html_ptr.write("<!-- END BODY -->\n")  

    #---------------------------------------------------------------------------------------------------
    # Report Footer
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN FOOTER -->\n")
    html_ptr.write("<div class='report-footer'>\n")
    html_ptr.write("  <div style='float:right'>Generated on %s</div>\n" %reportTimeStamp)
    html_ptr.write("<br>\n")
    html_ptr.write("  <div style='float:right'>Report Version: %s</div>\n" %_version.__version__)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END FOOTER -->\n")    

    html_ptr.write("</div>\n")    

    #---------------------------------------------------------------------------------------------------
    # Add javascript 
    #---------------------------------------------------------------------------------------------------

    html_ptr.write('''

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>  
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script> 
    ''')

    html_ptr.write("<script>\n")
    # Add the js for inventory datatable
    html_ptr.write('''
        
            var table = $('#claimableFiles').DataTable();

            $(document).ready(function() {
                table;
            } );
    ''')

    html_ptr.write('''
        
            var table = $('#nonclaimableFiles').DataTable();

            $(document).ready(function() {
                table;
            } );
    ''')
    html_ptr.write("</script>\n")

    html_ptr.write("</body>\n") 
    html_ptr.write("</html>\n") 
    html_ptr.close() 

    logger.info("    Exiting generate_html_report")
    return htmlFile

####################################################################
def encodeImage(imageFile):

    #############################################
    # Create base64 variable for branding image
    try:
        with open(imageFile,"rb") as image:
            logger.debug("Encoding image: %s" %imageFile)
            encodedImage = base64.b64encode(image.read())
            return encodedImage
    except:
        logger.error("Unable to open %s" %imageFile)
        raise