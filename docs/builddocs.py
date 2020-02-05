import os
import shutil
import subprocess
import argparse

'''
This script generates documentation based on the content of the current
repo, for the current master HEAD (if run with '--version dev' argument or
without arguments), all available tags (if run with the '--version all' argument), 
or the latest available tag (if the '--version stable' argument is used)

The script file should be located in the documentation folder (with sphinx files
under ./source folder)

You can specify the output folder in which docs are to be produced, by using the 
'--output [path]' argument. If not used, the documentation will be created under the 
./build folder. 
'''

NAME = "bridge4"

def sh(commands):
    if isinstance(commands, str):
        commands = commands.split(" ")
    out = subprocess.Popen(commands, stdout=subprocess.PIPE)
    stdout, stderr = out.communicate()
    return stdout.decode("utf-8")

def builddocs(version, folder):
    if folder is None:
        folder = os.path.join(os.getcwd(), "build")
    if version == "dev":
        buildref("master", folder, versionname="latest")
    else:
        if version == "stable":
            refs = getlatest()
        else:
            refs = getrefs()
        if refs: 
            for ref in refs:
                buildref(ref, folder)

def getlatest():
    refs = []
    try:
        description = sh("git describe --tags")
        tag = description.split("-")[0]
        refs.append(tag)
    except:
        pass # in case no tags exist yet
    return refs

def getrefs():
    refs = []
    try:
        tags = sh("git show-ref --tags").splitlines()
        for line in tags:
            ref, tag = line.split(" ")
            refs.append(tag.replace("refs/tags/", ""))
    except:
        pass # in case no tags exist yet
    return refs

def buildref(ref, folder, versionname=None):
    print("Building project '%s' at version '%s'..." % (NAME, ref)) 
    sh("git checkout {}".format(ref))
    sourcedir = os.path.join(os.getcwd(), "source")
    builddir = os.path.join(folder, versionname or ref)
    if os.path.exists(builddir):
        shutil.rmtree(builddir)
    os.makedirs(builddir)
    sh("sphinx-build -a {} {}".format(sourcedir, builddir))

def main():
    parser = argparse.ArgumentParser(description='Build documentation.')
    parser.add_argument('--version',
                        help='Version to build',
                        choices=["all", "stable", "dev"],
                        default="dev")
    parser.add_argument('--output',
                        help='Output folder to save documentation')

    args = parser.parse_args()

    builddocs(args.version, args.output)
    sh("git checkout master")

if __name__ == "__main__":
    main()
