import re

## name of input and output file
input_config_file = 'production_global.conf'
output_config_file = 'newconfig.conf'

## List VDOMs you wish to remove from the config
vdomtorm = ['VDOM1', 'VDOM3']









with open(input_config_file, encoding='utf-8') as f:
    stage = 0
    newconfig = ""
    intconfig = ""
    keepint = 0
    buffer = 0
    for line in f:
        if stage == 0:
            if line[:11] == "config vdom":
                newconfig += line
                stage = 1
            else:
                newconfig += line

        ### stage 1 - remove vdom creation
        if stage == 1:
            if line[:13] == "config global":
                stage = 2
            else:
                vdomsearch = re.search("edit (.*)", line)
                if vdomsearch:
                    if vdomsearch.group(1) not in vdomtorm:
                        newconfig += line
                        newconfig += "next\n"

        ### stage 2 - remove interfaces
        if stage == 2:
            if line[:23] == "config system interface":
                stage = "2-2"
                newconfig += line
            else:
                newconfig += line
        if stage == "2-2":
            intfsearch = re.search("^\s\s\s\sedit \"(.*)\"", line)
            if intfsearch:
                if keepint == 1:
                    newconfig += intconfig
                intconfig = line
                keepint = 0
            elif line[:3] == "end":
                stage = 3
                newconfig += line
            else:
                vdomsearch = re.search("set vdom \"(.*)\"", line)
                if vdomsearch:
                    if vdomsearch.group(1) not in vdomtorm:
                        keepint = 1
                intconfig += line

        ### stage 3 - remove vdom properties
        if stage == 3:
            if line[:27] == "config system vdom-property":
                stage = "3-2"
                keepvdom = 1
            else:
                newconfig += line
        if stage == "3-2":
            if line[:3] == "end":
                stage = 4
                newconfig += line
            else:
                vdomsearch = re.search("^\s\s\s\sedit \"(.*)\"", line)
                if vdomsearch:
                    if vdomsearch.group(1) not in vdomtorm:
                        keepvdom = 1
                        newconfig += line
                    else:
                        keepvdom = 0
                else:
                    if keepvdom == 1:
                        newconfig += line

        ### stage 4 - remove VDOM configs
        if stage == 4:
            if line[:11] == "config vdom":
                buffer = 1

            elif buffer == 0:
                newconfig += line
            elif buffer == 1:
                vdomsearch = re.search("edit (.*)", line)
                if vdomsearch:
                    if vdomsearch.group(1) not in vdomtorm:
                        newconfig += "config vdom\n"
                        newconfig += line
                        buffer = 0
                    else:
                        buffer = 2

f = open(output_config_file, "w", encoding='utf-8')
f.write(newconfig)
f.close()
