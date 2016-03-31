import os
import shutil


def uploader():
    pass

def check(files, num):
    for file in files:
        if file.endswith("0000" + num + ".warc.gz"):
            return True
    return False

def warcnum(folder):
    count = 0
    for root, dirs, files in os.walk("./" + folder):
        for file in files:
            #print(file)
            if file.endswith(".warc.gz"):
                count += 1
        return count

def move_warcs():
    list = []
    done = True
    if not os.path.isdir('./ready'):
        os.makedirs('./ready')
    for folder in next(os.walk('.'))[1]:
        for root, dirs, files in os.walk("./" + folder):
            #if re.search(r'-[0-9a-z]{8}$', folder):
            #    writehtmllist(folder)
            if (check(files, "0") == False or check(files, "1") == True) and not folder == "ready":
                startnum = "0"
                firstnum = None
                moved = False
                while True:
                    if not os.path.isfile("./" + folder + "/" + folder + "-" + (5-len(startnum))*"0" + startnum + ".warc.gz"):
                        if firstnum > 0:
                            break
                    if os.path.isfile("./" + folder + "/" + folder + "-" + (5-len(startnum))*"0" + startnum + ".warc.gz"):
                        print 'hi'
                        if firstnum == None:
                            firstnum = int(startnum)
                        if not startnum == "0" and not firstnum == int(startnum):
                            print(os.path.join(root, folder + "-" + str((5-len(str(int(startnum)-1)))*"0") + str(int(startnum)-1) + ".warc.gz"))
                            moved = True
                            os.rename(os.path.join(root, folder + "-" + str((5-len(str(int(startnum)-1)))*"0") + str(int(startnum)-1) + ".warc.gz"), "./ready/" + folder + "-" + str((5-len(str(int(startnum)-1)))*"0") + str(int(startnum)-1) + ".warc.gz")
                    startnum = str(int(startnum) + 1)
                    if warcnum(folder) <= 1:
                        break
                    if warcnum(folder) == 2 and os.path.isfile("./" + folder + "/" + folder + "-meta.warc.gz"):
                        break
        if os.path.isfile("./" + folder + "/" + folder + "-meta.warc.gz") and not folder == "ready":
            for root, dirs, files in os.walk("./" + folder):
                for file in files:
                    if file.endswith(".warc.gz"):
                        list.append("./ready/" + file)
                        os.rename(os.path.join(root, file), "./ready/" + file)
                for file in files:
                    if file.endswith(".warc.gz") and not os.path.isfile("./ready/" + file):
                        print("./ready/" + file)
                        done = False
                if done == True:
                    shutil.rmtree("./" + folder)
    print("All finished WARCs have been moved.")
