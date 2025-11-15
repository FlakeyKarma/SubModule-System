#!/usr/bin/env python3

from os import listdir,\
        path as PATH,\
        chdir as cd,\
        getcwd as pwd,\
        system
from sys import path
from hashlib import sha256
import sys
import csv
import threading

def print_error(errorString):
    print(errorString)
    exit(1)

#Return hash of file
def hash_file(file_path):
    #Help from this 'https://stackoverflow.com/questions/22058048/hashing-a-file-in-python'
    sha256_obj = sha256()

    buffer_size = 65536

    with open(file_path, 'rb') as raw_file:
        while True:
            raw_data = raw_file.read(buffer_size)
            if not raw_data:
                break
            sha256_obj.update(raw_data)

    return sha256_obj.hexdigest()

'''
    Object to run all SuMoS functions
'''
class SUMOS:
    def __init__(self, base):
        #   Path to find plugin detail CSV
        self.SMSPath = base
        #   Plugin information from configs
        self.SMSPlugins = []
        #   Imported modules
        self.SMSImported = []
        #   Running modules
        self.SMSRunning = []
        #   CSV Path
        self.module_csv = f"{self.SMSPath}/listing.csv"
        #   Validate all fields are full
        self.fields = [
            #Name of plugin
            'NAME',
            #Original creator(s), separated by commas
            'CRET',
            #Description of plugin
            'DESC',
            #Arguments to pass to plugin
            'ARGS',
            #Path to plugin file
            'PATH',
            #Contributors, separated by commas
            'CONT',
            #256 Checksum
            'CHCK',
            #Interpreter (optional)
            'INTP'
        ]
        self.Preview()


    '''
        Preview module metadata
    '''
    def Preview(self):
        headers = []
        with open(self.module_csv, newline='') as c:
            full = csv.reader(c, delimiter=',', quotechar='"')
            for i,line in enumerate(full):
                raw_module = {}
                if i:
                    for j,attribute in enumerate(line):
                        raw_module[headers[j]] = attribute
                    self.SMSPlugins.append(raw_module)

                else:
                    headers = line

    '''
        Execute
    '''
    def Execute(self, plugin):
        if int(plugin['Standalone']):
            cd(f"{self.SMSPath}/plugins/{plugin['Path']}")
            system(f"{plugin['Interpreter']} {plugin['Path']}.py")
        else:
            imported_module = [mod for mod in self.SMSImported if mod['Name'] == plugin['Name']][0]['Module']
            imported_module.run()

    '''
        Call on selected plugin
    '''
    def Call(self, plugin, arguments=None):
        if [present_plugin for present_plugin in self.SMSPlugins if present_plugin['Name'] == plugin['Name']] == []:
            print(f"ERROR: '{plugin['Name']}' not imported.")
        else:
            new_process = {
                        'Name': plugin['Name'],
                        'Process':threading.Thread(target=self.Execute, args=(plugin,))
                    }
            new_process['Process'].start()
            self.SMSRunning.append(new_process)

    '''
        Import selected plugin
    '''
    def Import(self, plugin):
        cd(f"{self.SMSPath}/plugins/{plugin['Path']}")
        path.insert(0, f"{self.SMSPath}/plugins/{plugin['Path']}")
        new_module = {
                    'Name':plugin['Name'],
                    'Module':None if int(plugin['Standalone']) else __import__(plugin['Path'])
                }
        self.SMSImported.append(new_module)

    '''
        Remove module from RAM
    '''
    def Remove(self, plugin):
        if int(plugin['Standalone']):
            A = None
        else:
            sys.modules.pop(plugin['Path'])

        module = [mod for mod in self.SMSImported if mod['Name'] == plugin['Name']][0]
        self.SMSImported.remove(module)

    '''
        List plugin details
    '''
    def List(self, plugin=None):
        all_plugins = [plugin] if plugin else self.SMSPlugins

        for plugin in all_plugins:
            print("(%s) %s\t- %s" % (plugin['Path'], plugin['Name'], plugin['Description']))

    '''
        Check for issues pertaining to plugins
    '''
    def Check(self, plugin=None):
        all_plugins = [plugin] if plugin else self.SMSPlugins

        for plugin in all_plugins:
            for field in plugin.keys():
                if field != 'Interpreter':
                    if plugin[field] is None:
                        print_error("Error: '%s' from '%s' does not exist." % (field, config))


            pluginPath = "%s/plugins/%s" % (self.SMSPath, plugin['Path'])

            #Check if plugin file exists
            if not PATH.exists(pluginPath):
                print_error("Error: '%s' from '%s' does not exist." % (pluginPath, plugin['Path']))

            #Check if SHA256 matches plugin
            stated_hash = plugin['SHA256']
            plugin_hash = hash_file(f"{pluginPath}/{plugin['Path']}.py")

            if stated_hash != plugin_hash:
                print_error("Error: Check validitiy. Config file hash is '%s', actual hash is '%s' does not exist." % (stated_hash, plugin_hash))

    '''
        Return specific plugin, queried by 'Path'
    '''
    def Query(self, plugin):
        all_plugins = [plugin for plugin in self.SMSPlugins if plugin['Path'] == plugin['Path']]
        return all_plugins[0]
