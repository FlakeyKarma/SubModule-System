#!/bin/python3
from os import listdir,\
        path as PATH
from sys import path
from hashlib import sha256

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
    def __init__(self, SMSPath):
        #Path to find plugin configs
        self.SMSPath = SMSPath
        #Plugin information from configs
        self.SMSPlugins = {}
        #Validate all fields are full
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
        #Select all .cfg files in the SMSPath variable
        for config in listdir("%s/configs" % self.SMSPath):
            if config.endswith('.cfg'):
                #Create a hashtable that exists to said plugin configuration file
                self.SMSPlugins[config] = {}
                configPath = "%s/configs/%s" % (self.SMSPath, config) 
                with open(configPath, 'r') as config_file:
                    #Object with array of each line within config file
                    txt = config_file.read().split("\n")
                    self.SMSPlugins[config]['CONFIG_PATH'] = "%s/configs" % configPath
                    for line in txt:
                        if line == '':
                            continue
                        split_content = line.split(':')
                        #Fill hashtable object
                        if split_content[0] == 'PATH':
                            self.SMSPlugins[config][split_content[0]] = split_content[1].replace('\\', '/') if '\\' in list(split_content[1]) else split_content[1]
                        else:
                            self.SMSPlugins[config][split_content[0]] = split_content[1]


    '''
        Call on selected plugin
    '''
    def Call(self, module_name, arguments=None):
        plugin = self.SMSPlugins[module_name]
        path.insert(0, "%s/plugins/%s" % (self.SMSPath, plugin['PATH']))
        #File is named 'main' in plugin's path
        imported_module = __import__('main')
        imported_module.run()

    '''
        List plugin details
    '''
    def List(self):
        for config in self.SMSPlugins.keys():
            plugin = self.SMSPlugins[config]
            print("%s:\n\t- %s\n\t- %s" % (plugin['NAME'], plugin['DESC'], plugin['PATH']))

    '''
        Validate plugins based on .cfg files
    '''
    def Check(self, plugin=None):
        all_plugins = plugin if plugin is not None else self.SMSPlugins.keys()

        for config in all_plugins:
            for field in self.fields:
                if field != 'INTP':
                    if self.SMSPlugins[config][field] is None or self.SMSPlugins[config][field] == '':
                        print_error("Error: '%s' from '%s' does not exist." % (field, config))


            pluginPath = "%s/plugins/%s" % (self.SMSPath, self.SMSPlugins[config]['PATH'])

            #Check if plugin file exists
            if not PATH.exists(pluginPath):
                print_error("Error: '%s' from '%s' does not exist." % (pluginPath, config))

            #Check if SHA256 matches plugin
            stated_hash = self.SMSPlugins[config]['CHCK']
            plugin_hash = hash_file("%s/main.py" % pluginPath)
            
            if stated_hash != plugin_hash:
                print_error("Error: Check validitiy. Config file hash is '%s', actual hash is '%s' does not exist." % (stated_hash, plugin_hash))
