import os
import sys
import subprocess

# recorded folder to be copied and rewritten
recorded_folder = sys.argv[1]
rewritten_folder = sys.argv[2]

# temp folder to store rewritten protobufs
os.system("rm -rf rewritten")
os.system( "cp -r " + recorded_folder + " rewritten" )

files = os.listdir("rewritten")

# iterate through files to get top-level HTML (must do this before processing files!)
top_level_html = ''
top_file = ""
for filename in files:
    top_cmd = "protototext rewritten/" + filename + " top_level_temp"
    proc_top = subprocess.Popen([top_cmd], stdout=subprocess.PIPE, shell=True)
    (out_top, err_top) = proc_top.communicate()
    out_top = out_top.strip("\n")
    if ( "type=htmlindex" in out_top ): # this is the top-level HTML
        top_level_html = out_top.split("na--me=")[1]
        top_file = filename
    os.system("rm top_level_temp")

if ( top_level_html == '' ): # didn't find top level HTML file
    print "Didn't find top-level HTML file in: " + recorded_folder
    exit()


for filename in files:
    print filename

    #os.system("changeheader rewritten/" + filename + " Access-Control-Allow-Origin *")


    # convert response in protobuf to text (ungzip if necessary)
    command = "protototext rewritten/" + filename + " rewritten/tempfile"
    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return_code = proc.returncode
    out = out.strip("\n")
    print out
    res_type = out.split("*")[0].split("=")[1]
    gzip = out.split("*")[2].split("=")[1]
    chunked = out.split("*")[1].split("=")[1]
    # need to still handle if response is chunked and gzipped (we can't just run gzip on it)!
    if ( ("html" in res_type) or ("javascript" in res_type) ): # html or javascript file, so rewrite
        if ( "true" in chunked ): # response chunked so we must unchunk
            os.system( "python unchunk.py rewritten/tempfile rewritten/tempfile1" )
            os.system( "mv rewritten/tempfile1 rewritten/tempfile" )
            # remove transfer-encoding chunked header from original file since we are unchunking
            os.system( "removeheader rewritten/" + filename + " Transfer-Encoding" )
        if ( "false" in gzip ): # html or javascript but not gzipped
            if ( "javascript" in res_type ):
                os.system('cp get_unimportant_urls.js rewritten/prependtempfile')
                os.system('cat rewritten/tempfile >> rewritten/prependtempfile')
                os.system('mv rewritten/prependtempfile rewritten/tempfile')

            if ( "html" in res_type ): # rewrite all inline js in html files
                if ( filename == top_file ):
                    os.system('python html_rewrite.py rewritten/tempfile rewritten/htmltempfile "' + top_level_html + '"')
                    os.system('mv rewritten/htmltempfile rewritten/tempfile')

            # get new length of response
            size = os.path.getsize('rewritten/tempfile') - 1

            # convert modified file back to protobuf
            os.system( "texttoproto rewritten/tempfile rewritten/" + filename )

            # add access control header to response
            #os.system("changeheader rewritten/" + filename + " Access-Control-Allow-Origin *")

            # add new content length header
            os.system( "changeheader rewritten/" + filename + " Content-Length " + str(size) )
        else: # gzipped
            os.system("gzip -d -c rewritten/tempfile > rewritten/plaintext")
            if ( "javascript" in res_type ):
                os.system('cp get_unimportant_urls.js rewritten/prependtempfile')
                os.system('cat rewritten/plaintext >> rewritten/prependtempfile')
                os.system('mv rewritten/prependtempfile rewritten/plaintext')

            if ( "html" in res_type ): # rewrite all inline js in html files
                if ( filename == top_file ):
                    os.system('python html_rewrite.py rewritten/plaintext rewritten/htmltempfile "' + top_level_html + '"')
                    os.system('mv rewritten/htmltempfile rewritten/plaintext')

            # after modifying plaintext, gzip it again (gzipped file is 'finalfile')
            os.system( "gzip -c rewritten/plaintext > rewritten/finalfile" )

            # get new length of response
            size = os.path.getsize('rewritten/finalfile')

            # convert modified file back to protobuf
            os.system( "texttoproto rewritten/finalfile rewritten/" + filename )

            # add new content length header to the newly modified protobuf (name is filename)
            os.system( "changeheader rewritten/" + filename + " Content-Length " + str(size) )

            # add access control header to response
            #os.system("changeheader rewritten/" + filename + " Access-Control-Allow-Origin *")

            # delete temp files
            os.system("rm rewritten/plaintext")
            os.system("rm rewritten/finalfile")
        
    # delete original tempfile
    os.system("rm rewritten/tempfile")

os.system("mv rewritten " + rewritten_folder)

for filename in files:
    os.system("changeheader " + rewritten_folder + "/" + filename + " Access-Control-Allow Origin *")
    os.system("changeheader " + rewritten_folder + "/" + filename + " Access-Control-Allow-Headers Access-Control-Expose-Headers")
    os.system("changeheader " + rewritten_folder + "/" + filename + " Access-Control-Expose-Headers 'Link, x-systemname-unimportant'")
