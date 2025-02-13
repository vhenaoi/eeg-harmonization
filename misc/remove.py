import os
import glob

'''
Code used to delete unwanted processed files

Uncomment lines 67 and 96 (os.remove(i[j])) only if you are sure they are the files to be deleted.

'''
def path_to_remove_without_visits(path,sub,name,ext):   
    '''
    Function created to return the path to be deleted in databases without visits

    Inputs:
        path: path where all the files of all the subjects are processed 
        sub: name of a subject folder
        name: ending of the desired file to be deleted
        ext: file extension to be deleted
    
    Output:
        icpowers_json_files: path to delete

    '''
    path_def = path+'\\'+sub+'\\eeg\\'+name+ext 
    if name in path_def:
        icpowers_json_files = glob.glob(path+'\\'+sub+'\\eeg\\*'+name+ext)

    return icpowers_json_files

def path_to_remove_visits(path,sub,v,name,ext):    
    '''
    function created to return the path to be deleted in databases with visits

    Inputs:
        path: path where all the files of all the subjects are processed 
        name: ending of the desired file to be deleted
        sub: name of a subject folder
        v: name of the visit folder
        ext: file extension to be deleted
    
    Output:
        icpowers_json_files: path to delete
    '''
    #path_def = path+'\\'+sub+'\\'+v+'\\eeg\\'+name+ext
    #if name in path_def:
    path=path+'/'+sub+'/'+v+'/eeg/'
    patron=os.path.join(path,f'*{name}{ext}')
    icpowers_json_files = glob.glob(patron)
    return icpowers_json_files

def remove_data_without_visits(path,name,ext):
    '''
    function created to remove the paths to be deleted in databases without visits
    Inputs:
        path: path where all the files of all the subjects are processed 
        name: ending of the desired file to be deleted
        ext: file extension to be deleted
    
    '''
    subjects = os.listdir(path)
    json_remove=[]
    for sub in subjects:
        suffix = "sub"
        if sub.endswith(suffix,0,3) == True:
            #print(path_to_remove_without_visits(path,sub,name,ext))
            json_remove.append(path_to_remove_without_visits(path,sub,name,ext))
    for i in json_remove:
        for j in range(0,2):
            try:
                print(i[j])
                os.remove(i[j])
            except:
                continue


def remove_data_visits(path,name,ext):
    '''
    function created to remove the paths to be deleted in databases with visits

    Inputs:
        path: path where all the files of all the subjects are processed 
        name: ending of the desired file to be deleted
        ext: file extension to be deleted
    
    Output:
        icpowers_json_files: path to delete
    '''
    subjects = os.listdir(path)
    json_remove=[]  
    for sub in subjects:
        suffix = "sub"
        if sub.endswith(suffix,0,3) == True:
            ses = os.listdir(path+'/'+sub)
            for v in ses:
                json_remove.append(path_to_remove_visits(path,sub,v,name,ext))
    for i in json_remove:
        for j in range(0,2):
            try:
                print(i[j])
                os.remove(i[j])
            except:
                continue
    print(json_remove)
def remove_condition(path,name,ext,task):
    '''
    function created to remove the paths to be deleted in databases with visits

    Inputs:
        path: path where all the files of all the subjects are processed 
        name: ending of the desired file to be deleted
        ext: file extension to be deleted
    
    Output:
        icpowers_json_files: path to delete
    '''
    subjects = os.listdir(path)
    json_remove=[]  
    for sub in subjects:
        suffix = "sub"
        if sub.endswith(suffix,0,3) == True:
            ses = os.listdir(path+'/'+sub)
            for v in ses:
                json_remove.append(path_to_remove_visits(path,sub,v,name,ext))
    for l in range(len(json_remove)):
        for n in range(len(json_remove[l])):
            try:       
                if type(json_remove[l][n].index(task)) == int:
                    print(json_remove[l][n])
                    os.remove(json_remove[l][n])
                else:
                    pass
            except:
                continue
    

#path = r'D:\TDG\filesSaved\BIOMARCADORES\derivatives\sovaharmony'
#path = r'/media/gruneco-server/ADATA HD650/BIOMARCADORES/derivatives/sovaharmony'
path=r'E:\BIOMARCADORES\derivatives\sovaharmony'
name = ['_powers','norm_eeg','powers_norm','sl_norm','band_norm','coherence_norm','entropy_norm','cross_frequency_norm','sl_band_norm']
ext = ['.json','.txt']

tasks=['OE','CE']
#sub-CTR001_ses-V0_task-CE_desc-[restCE]_space-ics[cresta]_norm-True_power
#metrics=['I]_norm-False_sl','I]_norm-False_crossfreq','I]_norm-False_cohfreq','I]_norm-False_entropy','I]_norm-False_power']
metrics=['norm-False_power_osc']
for e in ext:
    for t in tasks:
        for m in metrics:
            remove_data_visits(path,m,e)

#remove_data_without_visits(path,name[0],ext[1])
# remove_data_without_visits(path,name[0],ext[2])
# remove_data_without_visits(path,name[1],ext[0])
# remove_data_without_visits(path,name[1],ext[1])
# remove_data_without_visits(path,name[1],ext[2])
# remove_data_without_visits(path,name[2],ext[0])
# remove_data_without_visits(path,name[2],ext[1])
# remove_data_without_visits(path,name[2],ext[2])
# remove_data_without_visits(path,name[3],ext[0])
# remove_data_without_visits(path,name[3],ext[1])
# remove_data_without_visits(path,name[3],ext[2])
# remove_data_without_visits(path,name[4],ext[0])
# remove_data_without_visits(path,name[4],ext[1])
# remove_data_without_visits(path,name[4],ext[2])
# remove_data_without_visits(path,name[5],ext[0])
# remove_data_without_visits(path,name[5],ext[1])
# remove_data_without_visits(path,name[5],ext[2])
# remove_data_without_visits(path,name[6],ext[0])
# remove_data_without_visits(path,name[6],ext[1])
# remove_data_without_visits(path,name[6],ext[2])
# remove_data_without_visits(path,name[7],ext[0])
# remove_data_without_visits(path,name[7],ext[1])
# remove_data_without_visits(path,name[7],ext[2])
# remove_data_without_visits(path,name[8],ext[0])
# remove_data_without_visits(path,name[8],ext[1])
# remove_data_without_visits(path,name[8],ext[2])








