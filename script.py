import os
from pathlib import Path
import re
import shutil
import subprocess
import vrchatapi
from vrchatapi.api import authentication_api,avatars_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
import atexit
import argparse
import sys
import json
from threading import Thread,Lock

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser()
parser.add_argument("-o","--output", type=str,help="output path for unpacking avatars", required=False, default="./Ripped")
parser.add_argument("-i","--input", type=str,help="path to cache of vrchat(Cache-WindowsPlayer)")
parser.add_argument("--nonaming", action="store_true",help="wether or not name avatars", required=False)
parser.add_argument("-u","--username", type=str,help="username of vrc account for avatar naming, if you dont want use this, use --nonaming",required=not '--nonaming' in sys.argv)
parser.add_argument("-p","--password", type=str,help="password of vrc account for avatar naming, if you dont want use this, use --nonaming",required=not '--nonaming' in sys.argv)
parser.add_argument("-v","--verbose", action="store_true",help="verbose the output", required=False)
parser.add_argument("-s","--size", type=int,help="maximum size of avatar in MB(default 60MB)", required=False, default=1000000)
parser.add_argument("-j","--j", type=int,help="how many threads to use(default=4)", required=False, default=4)
parser.add_argument("-mins","--minsize", type=int,help="mminimum size of avatar in MB(default 0MB)", required=False, default=0)
parser.add_argument("-asr","--assetripper", type=str,help="path to assetripper.exe", required=False, default="./AssetRipper/AssetRipper-Console.exe")
parser.add_argument("--nounpack", action="store_true", help="Prevent unpacking of assets", required=False)
args = parser.parse_args()

avatarIdWithName = []
pathes = []
valid = []
cnt =0
ctr =0 
lock = Lock()

pattern_a=re.compile(rb"avtr_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
pattern_w=re.compile(rb"wrld_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
missing_finalAviChar = re.compile(rb"avtr_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{11})")
def get_id(file):
    with open(file,"rb") as f:
        s=f.read()
        res=pattern_a.findall(s)
        missing = missing_finalAviChar.findall(s)
        if len(res)>=1:
            return "avtr_"+str(res[0])[2:-1:]
        else:
            try:
                return "wrld_"+str(pattern_w.findall(s)[0])[2:-1:]
            except:
                if len(missing) > 0:
                    print("Missing final avi character!")
                return None

def getCachePath(): #ищем путь к кешу и если не находи, то кидаем эксепшон
    path = os.getenv('APPDATA')
    path = path.removesuffix("\\Roaming")
    path+="\\LocalLow\\VRChat\\VRChat"
    try:
        os.listdir(path+"\\Cache-WindowsPlayer")
        Cachepath = path+"\\Cache-WindowsPlayer"
    except:
        try:
            f =open(path+"\\config.json","r")
            res= ''
            for i in f.read().splitlines():
                res+=i
            f.close()
            Cachepath =json.loads(res)["cache_directory"] +"\\Cache-WindowsPlayer"
        except (FileNotFoundError, KeyError):
            Cachepath = None
    if Cachepath == None:
        print("Script can't find VRChat Cache folder automatically! try using with '-i [path to Cache-Windows-Player]'")
        sys.exit()
    else:
        return Cachepath

def goodbye():                      #функция выхода, выходим из аккаунта vrchat (иначе плохо всё кончится)
    if not args.nonaming:
        # Logout
        try:
            api_instance = authentication_api.AuthenticationApi(api_client)
            api_instance.logout()
        except vrchatapi.ApiException as e:
            print("Exception when calling AuthenticationApi->logout: ", e.reason)

    print("CacheRipper Finished... Goodbye!")


def get_valid_filename(s):          #превращаем имена в нормальные
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def getname_a(id):                    #тут мы обращаемся к api и выделяем имя аватара
    # Instantiate instances of API classes
    api_instance = avatars_api.AvatarsApi(api_client)
    avatar_id = id # str | 
    try:
        api_response = api_instance.get_avatar(avatar_id)
        #print(api_response)
        a = str(api_response).split("\n")
        name = ''
        for i in a:
            if i.startswith(" 'name'"):
                name =i.split(":")[1][2:-2]
                break
        #print(name)
        avatarIdWithName.append([avatar_id, name])
        return name
    except vrchatapi.ApiException as e:
        #print(f"Exception when calling API: {e}")
        return None


def get_path(dir):          #ммм, рекурсия :3
    l = os.listdir(dir)
    for d in l:
        try:
            get_path(dir +'\\'+d)
        except NotADirectoryError:
            pathes.append(dir)
            return


def run_asr(tsk,lst):
    global ctr
    for o in  range(len(tsk)):
        
        dst= outputDir +f"\\{lst[tsk[o]]}"
        out= f'{outputDir}\\exported\\{lst[tsk[o]]}'
        r = subprocess.run([assetripperPath, dst,'-o',out],input='\n', encoding='ascii',stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        while lock.locked():
            pass #wait to unlock lock by other thread
        with lock:
            ctr+=1
        if ctr%args.j == 0 and ctr//args.j <= cnt:
            print(f"Unpacked: {ctr//args.j} files, {((ctr//args.j)*100/cnt):0.2f}%")


def exportIt():
    print("\nExtracting vrc files")

    directories = os.listdir(cacheDir) #рекурсивно ищем папки в кеше vrchat'а
    #print(directories)
    get_path(cacheDir)
    for i in reversed(pathes):
        if os.listdir(i) == []:
            pathes.remove(i)
    pathes.pop(-1)

    for p in pathes:                    #из всех файлов выбираем предположительно аватары
        for j in os.listdir(p):
            size =os.path.getsize(p+'\\'+j)
            if(size > (100+(args.minsize *1000000)) and size < args.size *1000000):
                valid.append(p+'\\'+j)
    #print(valid)

    print(f"found {len(valid)} files")

    # check if export path exists and make if it doesn't
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    for i in range(len(valid)):         #переименовываем файл аватара __data  в .vrca и копируем в папку для экспорта
        name=get_id(valid[i])
        if name == None:
            name=str(i)
        dst = outputDir +"\\"+name
        procent = (i+1) / len(valid)*100
        shutil.copy(valid[i], dst)
        print(f"exported:{procent:0.2f}% ({i+1} files)")

def unpackIt():
    print("\nUnpacking vrca files")
    global cnt
    thr=[]
    ld= os.listdir(outputDir)
    tasks=[[]]*args.j #create threads task list

    #split by threads:
    cnt=len(ld)-1
    for i in range(cnt):
        tasks[i%(args.j)].append(i)

    #create dirs
    try:
        os.mkdir(outputDir+f"\\exported\\{ld[i]}")
    except FileExistsError:
        pass
    except FileNotFoundError:
        os.mkdir(outputDir+"\\exported")
        os.mkdir(outputDir+f"\\exported\\{ld[i]}")

    #start threads
    for l in range(args.j):
        thr.append(Thread(target=run_asr,args=[tasks[l],ld]))
        thr[l].start()
    for x in range(args.j):
        thr[x].join()


def nameIt():
    print("\nNaming vrca files")
    for f in os.listdir(outputDir):
        #из распакованных папок берем avtr_id, через vrchat api запрашиваем имя аватара, если получаем ответ то переименовываем папку
        if str(f).startswith("avtr_"):
            avatar_name = getname_a(f)
            if(avatar_name != None):
                try:
                    print(f+" name: "+avatar_name)
                    os.replace(outputDir+"\\"+f, outputDir+"\\"+get_valid_filename(avatar_name))
                except PermissionError as e:
                    pass
                except FileExistsError as e:
                    pass


print("starting...(This Might take a while.....)\n")

#check for assetripper BEFORE Login
if args.input == None:
    cacheDir=getCachePath()+"\\"
else:  
    cacheDir=args.input+"\\"
outputDir =args.output
assetripperPath = args.assetripper
dontUnpackAssets = args.nounpack
asr = Path(assetripperPath)
if asr.exists() or dontUnpackAssets:
    pass
else:
    print("Cant find AssetRipper! Use '-asr [path to AssetRipper.exe]'")
    sys.exit()

#vrc login
if not args.nonaming:
    configuration = vrchatapi.Configuration(
        username = args.username,
        password = args.password,
    )
    
    #логинимся в аккаунт vrchat для обращения к api
    api_client = vrchatapi.ApiClient(configuration)
    api_instance = authentication_api.AuthenticationApi(api_client) 
    api_client.user_agent = "doingAThing/1.0 notreal@email.com"
    try:
        # Step 3. Calling getCurrentUser on Authentication API logs you in if the user isn't already logged in.
        current_user = api_instance.get_current_user()
    except ValueError as e:
        # Step 3.5. Calling verify2fa if the account has 2FA enabled
        try:
            api_instance.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("2FA Code: ")))
            current_user = api_instance.get_current_user()
        except vrchatapi.ApiException as e:
            print("Exception when calling API: ", e.reason)
            sys.exit()
    except UnauthorizedException as e:
        if e.status == 200:
            # Step 3.5. Calling verify2fa if the account has 2FA enabled
            try:
                api_instance.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
                current_user = api_instance.get_current_user()
            except vrchatapi.ApiException as e:
                print("Exception when calling API: ", e.reason)
                sys.exit()
        else:
            print("Exception when calling API: ", e.reason)
            sys.exit()
    except vrchatapi.ApiException as e:
        print("Exception when calling API: ", e.reason)
        sys.exit()

    #все, залогинились, идем дальше

#register logout at exit
atexit.register(goodbye)

exportIt()

if not args.nonaming:
    nameIt()

if not dontUnpackAssets:
    unpackIt()
else:
    print("--nounpack given, skipping unpacking...")

print()
