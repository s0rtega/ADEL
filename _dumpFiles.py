#!/usr/bin/python
#

# Copyright (C) 2012 Michael Spreitzenbarth, Sven Schmitt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import hashlib
import sys

import _adel_log

def find_db_location(db_name):
    return subprocess.check_output('adb shell find /data/ -name '+ db_name +' -print').split("\r\n")[0].strip()
    
def dump_standard_databases(database, backup_dir, hash_value):
    database_location = find_db_location(database)

    try:
       dbprocess = subprocess.Popen(['adb', 'pull', database_location, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
       dbprocess.wait()
       _adel_log.log(database +" -> " + dbprocess.communicate()[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + "/" + database).hexdigest(), 3)
       hash_value.write(database + " -> " + hashlib.sha256(backup_dir + "/" + database).hexdigest() + " \n")
    except Exception,e:
       #print ("Error:         ----> " + str(e))
       _adel_log.log("dumpDBs:       ----> " + database + " doesn't exist!!", 2)
        
# Get database files through the android SDK
def get_SQLite_files(backup_dir, os_version, device_name):
    hash_value_file = backup_dir + "/hash_values.log"
    hash_value = open(hash_value_file, "a+")
    _adel_log.log("\n############  DUMP SQLite FILES  ############\n", 2)
   
    # Standard applications
    standard_application_db  = ["accounts.db", "contacts*.db", "mmssms.db", "calendar.db", "settings.db", "cache.cell", "cache.wifi"]
    for db in standard_application_db:
        dump_standard_databases(db, backup_dir, hash_value)
    
    # Optional applications and databases ----> analyzing is not implemented right now
    optional_applications_db = ["downloads.db", "user_dict.db", "telephony.db", "auto_dict.db", "weather.db", "WeatherClock", "EmailProvider.db", "alarms.db", "talk.db", "CachedGeoposition.db", "gesture.key", "password.key"]
    for db in optional_applications_db:
        dump_standard_databases(db, backup_dir, hash_value)
 
    # Twitter database ()
    try:
        for i in range(6):
            try:
                #accountdb_path = subprocess.Popen(['adb', 'shell', 'find / -name "databases" | grep twitter | xargs ls'], stdout=subprocess.PIPE).communicate(0)[0]
                file_name = subprocess.Popen(['adb', 'shell', 'ls', '/data/data/com.twitter.android/databases/'], stdout=subprocess.PIPE).communicate(0)[0].split()[i]
                if ".db" in file_name:
                    twitter_db = '/data/data/com.twitter.android/databases/' + file_name
                    twitter_db_name = subprocess.Popen(['adb', 'pull', twitter_db, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    twitter_db_name.wait()
                    _adel_log.log(file_name + " -> " + twitter_db_name.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + file_name).hexdigest(), 3)
                else:
                    continue
            except:
                continue
    except:
        _adel_log.log("dumpDBs:       ----> twitter.db doesn't exist!!", 2)

    # Search and download the Google-Mail mail database ()
    try:
        for i in range(6):
            file_name = subprocess.Popen(['adb', 'shell', 'ls', '/data/data/com.google.android.gm/databases/'], stdout=subprocess.PIPE).communicate(0)[0].split()[i]
            if file_name.startswith('mailstore'):
                mail_db = '/data/data/com.google.android.gm/databases/' + file_name
                emaildb = subprocess.Popen(['adb', 'pull', mail_db, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                emaildb.wait()
                _adel_log.log(file_name + " -> " + emaildb.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + file_name).hexdigest(), 3)
                break
            else:
                continue
    except:
        _adel_log.log("dumpDBs:       ----> Google-Mail database doesn't exist!!", 2)

    # Google+ database
    try:
        for i in range(6):
            try:
                file_name = subprocess.Popen(['adb', 'shell', 'ls', '/data/data/com.google.android.apps.plus/databases/'], stdout=subprocess.PIPE).communicate(0)[0].split()[i]
                if ".db" in file_name:
                    plus_db = '/data/data/com.google.android.apps.plus/databases/' + file_name
                    plus_db_name = subprocess.Popen(['adb', 'pull', plus_db, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    plus_db_name.wait()
                    _adel_log.log(file_name + " -> " + plus_db_name.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + file_name).hexdigest(), 3)
                else:
                    continue
            except:
                continue
    except:
        _adel_log.log("dumpDBs:       ----> Google+ database doesn't exist!!", 2)

    # Google-Maps database
    try:
        try:
            maps_file_name = subprocess.Popen(['adb', 'pull', '/data/data/com.google.android.apps.maps/databases/da_destination_history', backup_dir + "/da_destination_history.db"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            maps_file_name.wait()
            _adel_log.log("da_destination_history -> " + maps_file_name.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + "da_destination_history.db").hexdigest(), 3)
        except:
            _adel_log.log("dumpDBs:       ----> Google-Maps navigation history doesn't exist!!", 2)
        for i in range(6):
            try:
                file_name = subprocess.Popen(['adb', 'shell', 'ls', '/data/data/com.google.android.apps.maps/databases/'], stdout=subprocess.PIPE).communicate(0)[0].split()[i]
                if ".db" in file_name:
                    maps_db = '/data/data/com.google.android.apps.maps/databases/' + file_name
                    maps_db_name = subprocess.Popen(['adb', 'pull', maps_db, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    maps_db_name.wait()
                    _adel_log.log(file_name + " -> " + maps_db_name.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + file_name).hexdigest(), 3)
                else:
                    continue
            except:
                continue
    except:
        _adel_log.log("dumpDBs:       ----> Google-Maps database doesn't exist!!", 2)

    # Stored files (pictures, documents, etc.)
    if device_name != "local":
        # Pictures
        picture_dir = os.path.split(backup_dir)[0] + "/pictures/"
        print picture_dir
        os.mkdir(picture_dir)
        try:
            _adel_log.log("dumpDBs:       ----> dumping pictures (internal_sdcard)....", 0)
            pictures = subprocess.Popen(['adb', 'pull', '/sdcard/DCIM/Camera/', picture_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            _adel_log.log("dumpDBs:       ----> No pictures on the internal SD-card found !!", 2)
        try:
            _adel_log.log("dumpDBs:       ----> dumping pictures (external_sdcard)....", 0)
            pictures = subprocess.Popen(['adb', 'pull', '/sdcard/external_sd/DCIM/Camera/', picture_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            _adel_log.log("dumpDBs:       ----> No pictures on the external SD-card found !!", 2)
        try:
            _adel_log.log("dumpDBs:       ----> dumping screen captures (internal_sdcard)....", 0)
            pictures = subprocess.Popen(['adb', 'pull', '/sdcard/ScreenCapture/', picture_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            _adel_log.log("dumpDBs:       ----> No screen captures on the internal SD-card found !!", 2)
            
    hash_value.close()    

def get_twitter_sqlite_files(backup_dir, os_version):
    _adel_log.log("\n############  DUMP TWITTER SQLite FILES  ############\n", 2)
    twitterdbnamelist = []
    try:
        for i in range(6):
            try:
                file_name = subprocess.Popen(['adb', 'shell', 'ls', '/data/data/com.twitter.android/databases/'], stdout=subprocess.PIPE).communicate(0)[0].split()[i]
                if ".db" in file_name:
                    twitterdbnamelist.append(file_name)
                    twitter_db = '/data/data/com.twitter.android/databases/' + file_name
                    twitter_db_name = subprocess.Popen(['adb', 'pull', twitter_db, backup_dir], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    twitter_db_name.wait()
                    _adel_log.log(file_name + " -> " + twitter_db_name.communicate(0)[1].split("(")[1].split(")")[0] + " -> " + hashlib.sha256(backup_dir + file_name).hexdigest(), 3)
                else:
                    continue
            except:
                continue
    except:
        _adel_log.log("dumpDBs:       ----> twitter.db doesn't exist!!", 2)
    return twitterdbnamelist