# sml.py  (smOIDlabeler)

"""
Provide a means to select and label mask images created by SAM
01/26/24: new version: multiView.py has been incorporated here
"""

#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import os
import sys
import argparse
import cv2
import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_image_select import image_select
from PIL import Image
from PIL import ImageColor
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

st.set_page_config( layout="wide" )
classes = [ "bacteria", "fungi", "nematode_Bacterivore", "nematode_Fungivore", "nematode_Herbivore", "nematode_Omnivore", "nematode_Predator", "organicMatter", "protozoa_Amoeba", "protozoa_Ciliate", "protozoa_Flagellate" ]
yellow           = ( 255, 255, 0 )
red                 = ( 255, 0, 0 )
green              = ( 0, 128, 0 )
limegreen       = ( 50, 205, 50 )
chartreuse      = ( 127, 255, 0 )
darkseagreen  = ( 143, 188, 143 )
greenyellow   = ( 173, 255, 47 )
brown            = ( 165, 42, 42 )
aqua               = ( 0, 255, 255 )
blue                = ( 0, 0, 255 )
darkturquoise = ( 0, 206, 209 )
white              = ( 255, 255, 255 )
nuLine            = "\n"
mskJson         = []
srcPath           = ""
mskDir           = ""
theOS             = ""
maskClass      = None
maskColor      = None
lblMask          = False
classColors    = []                     # List of the class&color for each object
sbContainer    = st.empty()
slash               = ""
picList            = []
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def log( txt, outPutFileName=None ):

    # 02/03/20
    if ( outPutFileName == None ):
        outPutFileName = "logFile.txt"

    if ( "bytes" in str( type( txt ) ) ):
        with open( outPutFileName, "ab" ) as lF:
            lF.write( txt )

    else:
        with open( outPutFileName, "a",  encoding="utf-8" ) as lF:
    
            if ( "list" in str( type( txt ) ) ):
                rng  = range(0,len( txt ))
                for i in rng:
                    toWrite = str( txt[i] )
                    lF.write( toWrite )
                    lF.write( nuLine )

            elif ( "dict" in str( type( txt ) ) ):
                for key in txt:
                    lF.write( key + ": " + str( txt[key] ) )
                    lF.write( nuLine )

            elif ( "str" in str( type( txt ) ) ):
                lF.write( txt )
                lF.write( nuLine )

            elif ( "bool" in str( type( txt ) ) ):
                if ( txt ):
                    lF.write( "True" )
                else:
                    lF.write( "False" )

            elif ( "int" in str( type( txt ) ) ) or ( "float" in str( type( txt ) ) ):
                lF.write( str( txt ) )
                lF.write( nuLine )

    lF.close()
    return                        # log()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def getInfo( fullImgName ):                                             #  D:\\Projects\\SoilLifeConsultant\\SAMtest1\\mskFiles\malena2_fung2\1.png

    # parses the fullImgName string into its components and returns those components
    # eg: fileName, fName, fldrName = getInfo( thisMsk ) [in colorMask()]
    # eg: fullImgName = "D:\\Projects\\SoilLifeConsultant\\SAMtest1\\mskFiles\malena2_fung2\1.png"

    fileName  = os.path.basename( fullImgName )                                 # fileName == "1.png"
    firstName = fileName[ :fileName.find(".") ]                                     # firstName == "1"
    subFolder = fullImgName[ :fullImgName.find(fileName) -1]           # D:\\Projects\\SoilLifeConsultant\\SAMtest1\\mskFiles\malena2_fung2\
    subFolder = subFolder[ subFolder.rfind(slash)+1: ]                           # subFolder == malena2_fung2
    return fileName, firstName, subFolder
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def fillClassColors():

    classColors.append( "bacteria,yellow" )
    classColors.append( "fungi,red" )
    classColors.append( "nematode_Bacterivore,green" )
    classColors.append( "nematode_Fungivore,limegreen" )
    classColors.append( "nematode_Herbivore,chartreuse" )
    classColors.append( "nematode_Omnivore,darkseagreen" )
    classColors.append( "nematode_Predator,greenyellow" )
    classColors.append( "organicMatter,brown" )
    classColors.append( "protozoa_Amoeba,aqua" )
    classColors.append( "protozoa_Ciliate,blue" )
    classColors.append( "protozoa_Flagellate,darkturquoise" )
    return classColors                       # fillClassColors()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def getColorName( theClass ):

    for cls in classColors:
        if ( theClass in cls.split(",")[0] ):
            theColor = cls.split(",")[1]
            exit

    return theColor                               # getColorName()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def overLayPix( theImgName, thisMsksList, theMsk, fldrName, thePixel ):

    fileName = os.path.basename( theMsk )                              # '100.png'
    fName     = fileName[:fileName.find(".")]

    ovrLdDir       = fldrName
    ovrLdSubDir = fldrName + slash + "OverLd" + slash

    if ( not os.path.exists( ovrLdDir ) ):
        try:
            os.mkdir( ovrLdDir )
        except Exception as ex:
            print( "Unable to create the 'OverLaid' sub-folder " + ovrLdDir )
            sys.exit()

    if ( not os.path.exists( ovrLdSubDir ) ):
        try:
            os.mkdir( ovrLdSubDir )
        except Exception as ex:
            print( "Unable to create the 'OverLaid' sub-sub-folder " + ovrLdSubDir )
            sys.exit()

    lastMskSlash = ( theMsk.rfind(slash) + 1 )
    mskNumbr = theMsk[lastMskSlash:theMsk.find(".")]

    # Load the images
    image1 = np.array( Image.open(theImgName) )
    image2 = np.array( Image.open(theMsk) )

    # Create a mask to identify black or white pixels in image 2
    if    ( thePixel == 0 ):
        mask = (image2 == 0)
    elif ( thePixel == 1 ):
        mask = (image2 != 255)

    plt.imshow(image1)
    plt.imshow( mask, alpha=0.5 )
    plt.axis('off')

    plt.savefig( ovrLdSubDir+mskNumbr+"_OV.png", bbox_inches='tight', pad_inches = 0 ) 

    return ( ovrLdSubDir+mskNumbr+"_OV.png" )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def colorMask( thisSrcPath, thisMsk, theClass, theColor ):

    """
    called from run():  clrdImg = colorMask ( theSrcPath, theMsk, mskClass, mskColor )
    filePath   = thisMsk                                                              # 'D:\\Projects\\SoilLifeConsultant\\SAMtest1\\mskFiles\\malena2_fung2\\100.png'
    fileName = os.path.basename( filePath )                             # '100.png'
    fName     = fileName[:fileName.find(".")]                          # '100'
    fldrName = filePath[:filePath.find(fileName)-1]
    fldrName = fldrName[fldrName.rfind(slash)+1:]                # malena2_fung2
    """

    fileName, fName, fldrName = getInfo( thisMsk )
    maskDir  = thisSrcPath + slash + fldrName
    maskSubDir = maskDir + slash + "Masked"

    try:
        if ( not os.path.exists( maskDir ) ):
            os.mkdir( maskDir )
    except Exception as ex:
        print( "Unable to create the 'Masked' sub-folder: ", maskDir )
        sys.exit()

    try:
        if ( not os.path.exists( maskSubDir ) ):
            os.mkdir( maskSubDir )
    except Exception as ex:
        print( "Unable to create the 'Masked' sub-sub-folder: " + maskSubDir )
        sys.exit()

    with Image.open( thisMsk ) as maskImage:

        maskImage.load()
        if ( not isinstance(maskImage, Image.Image) ):            # verify I got it - error message otherwise
            print( "Error in colorMask(): can't open the thisMsk file " + thisMsk )
            log( "Error in colorMask(): can't open the thisMsk file " + thisMsk, "colorMaskERRORS.txt" )
            modImg = None
            return modImg

        maskImage = maskImage.convert( "RGBA" )
        nuImg = np.array( maskImage )                                             # "nuImg" is a height x width x 4 numpy array
        maskImage.close()

    if ( isinstance(maskImage, Image.Image) ):                              # verify it's closed - error message otherwise
        maskImage.close()

    red, green, blue, alpha = nuImg.T                                         # Temporarily unpack the bands for readability
    whitePixels = (red == 255) & (blue == 255) & (green == 255)
    nuImg[..., :-1][whitePixels.T] = theColor
    
    # Save the modified image
    modImg = maskSubDir + slash + fName + "_LBL.png"
    plt.imsave( modImg, nuImg )
    return modImg                                 # colorMask()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def classChanged():
    #maskClass = st.session_state["orgClass"]
    st.session_state["orgClass"] = maskClass
    return maskClass                      # classChanged()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitMaskColor( thisClass ):

    for cls in classColors:

        if ( thisClass in cls.split(",")[0] ):
            theColor = cls.split(",")[1]
            break

    return theColor                               # gitMaskColor()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def makeMask( theMaskClass, theSrcPath, theSrcImg, theMsk, thisMsksList ):

    global mskJson, maskClass, maskColor

    if ( theMaskClass != None ):
        maskClass = theMaskClass
        if ( "orgClass" not in st.session_state ):
            st.session_state["orgClass"] = maskClass

    if ( maskClass != None ):
        maskColor  = gitMaskColor( maskClass  )

    if ( maskColor != None ):
        maskColor  = ImageColor.getcolor( maskColor, "RGB" ) 

    if ( maskClass != None ) and  ( maskColor != None ):
        theLbl = {"SourceImage": theSrcImg, "maskID": theMsk, "maskClass": maskClass, "maskColor": maskColor}
        mskJson.append( theLbl )
        log( mskJson, "mskJson.json" )   # jsonLog
        clrdImg = colorMask ( theSrcPath, theMsk, maskClass, maskColor  )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doCompile( srcImgName ):

    fileName, fName, fldrName = getInfo( srcImgName )
    maskDir       = srcPath + fName
    maskSubDir = maskDir + slash + "asked"
    compileDir  = maskDir + slash + "Compiled"
    didCompile  = False
    thisFile         = srcImgName
    mskdFiles    = os.listdir( maskSubDir )

    try:
        if ( not os.path.exists( compileDir ) ):
            os.mkdir( compileDir )
    except Exception as ex:
        print( "Unable to create the 'Compile' folder for this image", compileDir + " - " + srcImgName )
        sys.exit()

    compImg = cv2.imread( thisFile )                                                  # reads an image in the BGR format
    compImg = cv2.cvtColor( compImg, cv2.COLOR_BGR2RGB )   # BGR -> RGB

    for ele in mskdFiles:
        tmpEle = cv2.imread( maskSubDir + slash +ele )
        tmpEle = cv2.cvtColor( tmpEle, cv2.COLOR_BGR2RGB )   # BGR -> RGB

        # Create a mask of non-black pixels in tmpEle
        mask    = (tmpEle != 0)
        compImg[mask] = tmpEle[mask]

        compPix = Image.fromarray( compImg )
        fileName = fName + "_COMP.png"

        try:
            compPix.save( compileDir + "//" + fileName )
        except:
            return False

        didCompile = True
        if ( picList.count(srcImgName) > 0 ):
            picList.remove( srcImgName )
            st.session_state["imgList"] = picList

    cv2.destroyAllWindows()
    return didCompile                                  # doCompile()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def makeMasksList( imgMskDir ): 

    tmpMskList     = [imgMskDir+file for file in os.listdir( imgMskDir ) if file.endswith( ('png', 'jpg') ) ]
    DoneDirList   = os.listdir( srcPath )
    doneMaskList = []
    toRemove       = []

    for theDir in DoneDirList:
        if ( "." in theDir ) or ( "mskFiles" in theDir ):
            continue
        doneMaskList.extend( [srcPath+theDir + slash + "Masked" + slash + file for file in os.listdir( srcPath+theDir + slash + "Masked" + slash ) if file.endswith( ('png', 'jpg') ) ] )

    for ele in tmpMskList:

        fileName, fName, fldrName = getInfo( ele )
        lblName   = fldrName + slash + "Masked" + slash + fileName[:fileName.find(".")]  + "_LBL.png"

        # ele == "D:\\Projects\\SoilLifeConsultant\\SAMtest1\\mskFiles\malena2_fung2\6.png"
        # lblName == "malena2_fung2\\Masked\6_LBL.png"
        # dml ==  "D:\\Projects\\SoilLifeConsultant\\SAMtest1\malena2_fung2\Masked\6_LBL.png"

        for dml in doneMaskList:                  # doneMaskList DoneDirList

            if ( lblName in dml ) or ( lblName == dml ):
                toRemove.append( ele )

    for tr in toRemove:
        if ( tmpMskList.count(tr) > 0 ):
            tmpMskList.remove( tr )

    masksList = [" "] + tmpMskList
    return masksList
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def getPic( thePicList ):

    header    = "Choose an image"
    with sbContainer.container():
        picName = st.selectbox( header, st.session_state["imgList"], index=0 )
        st.session_state["ovImg"] = picName
    return picName
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def run( srcPath, mskDir, theOS  ):

    msk             = None
    imgName    = None
    header         = "Choose an image"

    imgName    = getPic( st.session_state["imgList"] )

    fileName    = os.path.basename( imgName )             # st.session_state["ovImg"] )
    subFldr       = fileName[:fileName.find(".")]
    fldrName    = srcPath  + slash + subFldr
    picMskDir  = mskDir + subFldr + slash

    # 02/10/24: streamlit will automatically run the imgName=image_select() and select the 1st mask image, & create new sub-&sub-sub folders & a new image :: track where those are located
    # 02/12/24: I've inserted a "blank" image at the top of msksList[] with the result that the sourceImage is shown on the right at startUp
    msksList     = makeMasksList( picMskDir )
    st.session_state["msksList"] = msksList

    fillClassColors()

    with st.sidebar:
        hdr  = "Click on a mask image - see it in purple in the right colored image"
        st.write( hdr )
        msk = image_select( "", images = msksList, index=0, return_value="original", use_container_width=False )   # return_value="original" index

        if ( msk != None ) and ( msk != " " ):
            # last parameter => test for white pixels (0), or black pixels (1)
            ovImg = overLayPix( st.session_state["ovImg"], msksList, msk, fldrName, 0 )
            st.session_state["ovImg"] = ovImg

    col1a, col2a = st.columns(2)
    with col1a:
        Srcpic = Image.open( imgName )             # st.session_state["ovImg"] )
        st.image( Srcpic, use_column_width="always" )
    with col2a:
        tmpPic = st.session_state["ovImg"]
        OVpic = Image.open( tmpPic )
        st.image( OVpic, use_column_width="always" )

    col3a, col3b, col3c = st.columns(3)
    with col3a:

        lblMask = False
        if ( "lblMask" not in st.session_state ):
            st.session_state["lblMask"] = lblMask
        lblMask = st.checkbox( "Label this mask", value=False )

        if lblMask:
            maskClass = selectbox( "Choose an organism class", classes, key="orgClass" )        #, on_change=classChanged() )
            makeMask( maskClass, srcPath, fldrName, msk , msksList )
            lblMask = False
            maskClass = None
            maskColor = None
            msksList = makeMasksList( picMskDir )
            st.session_state["msksList"] = msksList
            st.session_state["ovImg"] = imgName
            st.session_state["lblMask"] = lblMask
    with col3b:
        compMasks = st.checkbox( "Compile ALL Masks" )
    with col3c:
        st.write(
            """
            Author:  Baruch Bashan
            gaiagrower77@gmail.com
            """
            )

    if compMasks and ( st.session_state["ovImg"] != None ):

        if ( not doCompile( st.session_state["ovImg"] ) ):
            print( "Compiling this image DIDN'T work", st.session_state["ovImg"] )
            log( "Compiling this image DIDN'T work: " + st.session_state["ovImg"], "CompileErrors.txt" )
        else:
            st.session_state["imgList"] = picList
            imgName = getPic( st.session_state["imgList"] )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    st.title( "smOID Labeler" )

    parser = argparse.ArgumentParser( description="smOID Labeler")
    parser.add_argument( "--src", help="Folder with Source Images" )
    parser.add_argument( "--mskDir", help="Folder with Source Image Masks" )
    parser.add_argument( "--os", help="Operating System being used" )
    args = parser.parse_args()

    if (not args.src):                     # from CLI
        # test for url-based src parameter
        try:
            srcPath = request.args.get( "src" )
        except:
            print( "Please enter the images 'Source' folder" )
            sys.exit()
    else:
        srcPath = args.src
        try:
            if ( not os.path.exists( srcPath ) ):
                os.mkdir( srcPath )
        except Exception as ex:
            print( "Unable to create the 'Source' folder " + srcPath )
            sys.exit()

    if (not args.mskDir):
        # test for url-based src parameter
        try:
            mskDir = request.args.get( "mskDir" )
        except:
            print( "Please enter the Masks image folder" )
            sys.exit()
    else:
        mskDir = args.mskDir
        try:
            if ( not os.path.exists( mskDir ) ):
                os.mkdir( mskDir )
        except Exception as ex:
            print( "Unable to create the 'Masks' folder " + mskDir )
            sys.exit()

    if (not args.os):
        try:
            theOS = request.args.get( "os" )
        except:
            print( "Please enter the Operating System being used: 'w'in, 'm'ac, or 'c'loud" )
            sys.exit()
    else:
        theOS = args.os

    if ( "imgList" not in st.session_state ):
        picList = [srcPath+file for file in os.listdir( srcPath ) if file.endswith( ('png', 'jpg') ) ]
        st.session_state["imgList"] = picList
    else:
        picList = st.session_state["imgList"]

    if    ( theOS.lower() == "w" ):
        slash = "\\"
    elif ( theOS.lower() == "m" ):
        slash = "/"
    elif ( theOS.lower() == "c" ):
        slash = "/"

    #app = mainApp( srcPath, mskDir, theOS )

    # The main app
    run( srcPath, mskDir, theOS )
#-------------------------------------------------------------------------------------------
