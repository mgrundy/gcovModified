 #    Copyright (C) 2014 MongoDB Inc.
 #
 #    This program is free software: you can redistribute it and/or  modify
 #    it under the terms of the GNU Affero General Public License, version 3,
 #    as published by the Free Software Foundation.
 #
 #    This program is distributed in the hope that it will be useful,
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #    GNU Affero General Public License for more details.
 #
 #    You should have received a copy of the GNU Affero General Public License
 #    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import string
import os
import sys
import optparse
import json
import datetime 

import pymongo
import tornado.httpclient

def do_json_import():
    """Insert all JSON files from root directory and below into database."""

    parser = optparse.OptionParser(usage="""\
                                   %prog [git_hash] [rootPath]
                                   [build_id] [connectionstring]
                                   [testname] [branch] [platform]""")

    # add in command line options.
    parser.add_option("-g", "--git-hash", dest="ghash",
                      help="git hash of code being tested",
                      default=None)
    parser.add_option("-b", "--build-id", dest="build", 
                      help="build ID of code being tested",
                      default=None)

    parser.add_option("-c", "--connection-string", dest="connectstr",
                      help="URL that will be connected to",
                      default=None)

    parser.add_option("-t", "--test-name", dest="tname",
                      help="name of the test",
                      default=None)

    parser.add_option("-a", "--branch", dest="branch",
                      help="name of the branch",
                      default=None)

    parser.add_option("-p", "--platform", dest="pform",
                      help="build platform",
                      default=None)

    parser.add_option("-r", "--root-dir", dest="root",
                      help="root directory of JSON files",
                      default=None)

    parser.add_option("-d", "--date", dest="date",
                      help="date of build",
                      default=None)

    (options, args) = parser.parse_args()
    
    if options.ghash is None:
        print "\nERROR: Must specify git hash \n"
        sys.exit(-1)
    
    if options.build is None:
        print "\nERROR: Must specify build ID \n"
        sys.exit(-1)
 
    if options.connectstr is None:
        print "\nERROR: Must specify connection string \n"
        sys.exit(-1)
   
    if options.tname is None:
        print "\nERROR: Must specify test name \n"
        sys.exit(-1)

    if options.branch is None:
        print "\nERROR: Must specify branch name \n"
        sys.exit(-1)

    if options.pform is None:
        print "\nERROR: Must specify platform \n"
        sys.exit(-1)

    if options.root is None:
        print "\nERROR: Must specify root directory \n"
        sys.exit(-1)

    if options.date is None:
        print "\nERROR: Must specify date \n"
        sys.exit(-1)

    http_client = tornado.httpclient.HTTPClient()

    # Check if date is properly formatted 
    date = datetime.datetime.strptime(options.date, "%Y-%m-%dT%H:%M:%S.%f")
 
    # Gather meta info
    meta_record = {}
    meta_record["_id"] = {"build_id": options.build,
                         "git_hash": options.ghash}
    meta_record["date"] = options.date 
    meta_record["branch"] = options.branch
    meta_record["platform"] = options.pform
       
    request = tornado.httpclient.HTTPRequest(url=options.connectstr + "/meta", 
                                             method="POST", 
                                             request_timeout=600.0,
                                             body=json.dumps(meta_record))
    try:
        response = http_client.fetch(request)
        print response.body
    except tornado.httpclient.HTTPError as e:
        print "Error: ", e

    http_client.close()



do_json_import()
