"""
@autor: Valeria Cadavid Castro, Universidad de Antioquia, 
@autor: Verónica Henao Isaza, Universidad de Antioquia, 
@autor: Luisa María Zapata Saldarriaga, Universidad de Antioquia, luisazapatasaldarriaga@gmail.com

"""

import numpy as np
import json
import pandas as pd
import warnings
import collections
import seaborn as sns
import matplotlib.pyplot as plt
import os
import errno
import glob 
def load_txt(file):
  '''
  Function that reads txt files

  Parameters
  ----------
    file: extend .txt 

  Returns
  -------
    data: 
      Contains the information that was stored in the txt file
  '''
  with open(file, 'r') as f:
    data=json.load(f)
  return data

def load_feather(path):
    '''
    Function to upload files with feather format

    Parameters
    ----------
        path:str
            Directory where the file with the extension .feather

    Returns 
    -------
        data: dataframe
            Data in dataframe format
    '''
    data=pd.read_feather(os.path.join(path).replace("\\","/"))
    return data

def concat_df(path):
    path_df=glob.glob(path)
    data=[]
    for df in path_df:
        d=load_feather(df)
        
        data.append(d)
    data_concat=pd.concat((data))
    return data_concat

def _verify_epochs_axes(epochs_spaces_times,spaces_times_epochs,max_epochs=None):
    """
    """
    epochs,spaces,times = epochs_spaces_times.shape
    if max_epochs is None:
        max_epochs = epochs
    for e in range(np.max([epochs,max_epochs])):
        for c in range(spaces):
            assert np.all(epochs_spaces_times[e,c,:] == spaces_times_epochs[c,:,e])
    return True

def _verify_epoch_continuous(data,spaces_times,data_axes,max_epochs=None):
    epochs_idx = data_axes.index('epochs')
    spaces_idx = data_axes.index('spaces')
    times_idx = data_axes.index('times')
    epochs,spaces,times = data.shape[epochs_idx],data.shape[spaces_idx],data.shape[times_idx]
    if not epochs_idx in [0,2]:
        raise ValueError('Axes should be either epochs,spaces,times or spaces,times,epochs')
    if max_epochs is None:
        max_epochs = epochs
    for e in range(np.max([epochs,max_epochs])):
        for c in range(spaces):
            if epochs_idx==0:
                assert np.all(data[e,c,:] == spaces_times[c,e*times:(e+1)*times])
            elif epochs_idx==2:
                assert np.all(data[c,:,e] == spaces_times[c,e*times:(e+1)*times])
    return True



"Functions to save dataframes for graphics"

def dataframe_long_roi(data,type,columns,name,path):
    '''Function used to convert a dataframe to be used for graphing by ROIs'''
    #demographic data and neuropsychological test columns
    #data_dem=['participant_id', 'visit', 'group', 'condition', 'database','age', 'sex', 'education', 'MM_total', 'FAS_F', 'FAS_A', 'FAS_S']
    data_dem=['participant_id', 'visit', 'group', 'condition', 'database']
    columns_df=data_dem+[type, 'Band', 'ROI']
    data_new=pd.DataFrame(columns=columns_df)
    #Frequency bands
    bandas=['Delta','Theta','Alpha-1','Alpha-2','Beta1','Beta2','Beta3','Gamma']
    #ROIs 
    roi=['F', 'C','PO', 'T_']
    for i in columns:
        '''The column of interest is taken with its respective demographic data and added to the new dataframe'''
        data_x=data_dem.copy()
        data_x.append(i)
        d_sep=data.loc[:,data_x] 
        for j in bandas:
            if j in i:
                band=j
        for c in roi:
            if c in i:
                r=c
        d_sep['Band']=[band]*len(d_sep)
        d_sep['ROI']=[r]*len(d_sep)
        d_sep= d_sep.rename(columns={i:type})
        data_new=data_new.append(d_sep,ignore_index = True) #Uno el dataframe 
    data_new['ROI']=data_new['ROI'].replace({'T_':'T'}, regex=True)#Quito el _ y lo reemplazo con '' 
    try:
        path="{input_path}\data_long\ROI".format(input_path=path).replace('\\','/')
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    data_new.reset_index(drop=True).to_feather('{path}\data_long_{task}_{metric}_{name}_roi.feather'.format(path=path,name=data['database'].unique()[0],task=data_new['condition'].unique()[0],metric=type))
    print('Dataframe para graficos de {type} guardado: {name}'.format(type=type,name=name))

def dataframe_long_components(data,type,columns,name,path,spatial_matrix='54x10'):
    '''Function used to convert a wide dataframe into a long one to be used for graphing by IC'''
    #demographic data and neuropsychological test columns
    #data_dem=['participant_id', 'visit', 'group', 'condition', 'database','age', 'sex', 'education', 'MM_total', 'FAS_F', 'FAS_A', 'FAS_S']
    data_dem=['participant_id', 'visit', 'group', 'condition', 'database']
    columns_df=data_dem+[type, 'Band', 'Component']
    data_new=pd.DataFrame(columns=columns_df)
    #Frequency bands
    bandas=['Delta','Theta','Alpha-1','Alpha-2','Beta1','Beta2','Beta3','Gamma']
    #Components
    if spatial_matrix=='58x25':
        componentes =['C14', 'C15','C18', 'C20', 'C22','C23', 'C24', 'C25']
    elif spatial_matrix=='54x10':
        componentes =['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
    elif spatial_matrix=='cresta' or spatial_matrix=='openBCI' or spatial_matrix=='paper':
        componentes =['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    
    for i in columns:
        '''The column of interest is taken with its respective demographic data and added to the new dataframe'''
        data_x=data_dem.copy()
        data_x.append(i)
        d_sep=data.loc[:,data_x] 
        for j in bandas:
            if j in i:
                band=j
        for c in componentes:
            if c in i:
                componente=c
        d_sep['Band']=[band]*len(d_sep)
        d_sep['Component']=[componente]*len(d_sep)
        d_sep= d_sep.rename(columns={i:type})
        data_new=pd.concat((data_new,d_sep),ignore_index = True)
        #data_new=data_new.append(d_sep,ignore_index = True) #Uno el dataframe 
    try:
        path="{input_path}\data_long\IC".format(input_path=path).replace('\\','/')
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    data_new.reset_index(drop=True).to_feather('{path}\data_{task}_{metric}_long_{name}_{spatial_matrix}_components.feather'.format(path=path,name=data_new['database'].unique()[0],task=data_new['condition'].unique()[0],metric=type,spatial_matrix=spatial_matrix).replace('\\','/'))
    print('Dataframe para graficos de {type} guardado: {name}'.format(type=type,name=name))

def dataframe_long_cross_roi(data,type,columns,name,path):
    '''Function used to convert a dataframe to be used for graphing by ROIs'''
    #demographic data and neuropsychological test columns
    #data_dem=['participant_id', 'visit', 'group', 'condition', 'database','age', 'sex', 'education', 'MM_total', 'FAS_F', 'FAS_A', 'FAS_S']
    
    data_dem=['participant_id', 'visit', 'group', 'condition', 'database']
    columns_df=data_dem+[type, 'Band', 'ROI']
    data_new=pd.DataFrame(columns=columns_df)
    #Frequency bands 
    bandas=['_Delta','_Theta','_Alpha-1','_Alpha-2','_Beta1','_Beta2','_Beta3','_Gamma']
    m_bandas=['Mdelta','Mtheta','Malpha-1','Malpha-2','Mbeta1','Mbeta2','Mbeta3','Mgamma']
    #ROIs 
    roi=['F', 'C','PO', 'T_']
    for i in columns:
        '''The column of interest is taken with its respective demographic data and added to the new dataframe'''
        data_x=data_dem.copy()
        data_x.append(i)
        d_sep=data.loc[:,data_x] 
        for j in bandas:
            if j in i:
                band=j
        for m in m_bandas:
            if m in i:
                bandm=m
        for c in roi:
            if c in i:
                r=c
        d_sep['Band']=[band]*len(d_sep)
        d_sep['ROI']=[r]*len(d_sep)
        d_sep['M_Band']=[bandm]*len(d_sep)
        d_sep= d_sep.rename(columns={i:type})
        data_new=data_new.append(d_sep,ignore_index = True) #Uno el dataframe 
    data_new['ROI']=data_new['ROI'].replace({'T_':'T'}, regex=True)#Quito el _ y lo reemplazo con '' 
    data_new['Band']=data_new['Band'].replace({'_':''}, regex=True)#Quito el _ y lo reemplazo con ''
    try:
        path="{input_path}\data_long\ROI".format(input_path=path).replace('\\','/')
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    data_new.reset_index(drop=True).to_feather('{path}\data_{name}_{task}_long_{metric}_ROI.feather'.format(path=path,name=data['database'].unique()[0],task=data_new['condition'].unique()[0],metric=type))
    print('Dataframe para graficos de {type} guardado: {name}'.format(type=type,name=name))

def dataframe_long_cross_ic(data,type='Cross Frequency',columns=None,name=None,path=None,spatial_matrix='54x10'):
    '''Function used to convert a dataframe to be used for graphing.'''
    #demographic data and neuropsychological test columns
    #data_dem=['participant_id', 'visit', 'group', 'condition', 'database','age', 'sex', 'education', 'MM_total', 'FAS_F', 'FAS_A', 'FAS_S']
    data_dem=['participant_id', 'visit', 'group', 'condition', 'database']
    columns_df=data_dem+[type, 'Band','M_Band', 'Component']
    data_new=pd.DataFrame(columns=columns_df)
    #Frequency bands
    bandas=['_Delta','_Theta','_Alpha-1','_Alpha-2','_Beta1','_Beta2','_Beta3','_Gamma']
    m_bandas=['Mdelta','Mtheta','Malpha-1','Malpha-2','Mbeta1','Mbeta2','Mbeta3','Mgamma']
    if spatial_matrix=='58x25':
        componentes =['C14', 'C15','C18', 'C20', 'C22','C23', 'C24', 'C25']
    elif spatial_matrix=='54x10':
        componentes =['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
    elif spatial_matrix=='cresta' or spatial_matrix=='openBCI' or spatial_matrix=='paper':
        componentes =['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    for i in columns:
        '''The column of interest is taken with its respective demographic data and added to the new dataframe'''
        data_x=data_dem.copy()
        data_x.append(i)
        d_sep=data.loc[:,data_x] 
        for j in bandas:
            if j in i:
                band=j 
        for m in m_bandas:
            if m in i:
                bandm=m
        for c in componentes:
            if c in i:
                componente=c

        d_sep['Band']=[band]*len(d_sep)
        d_sep['M_Band']=[bandm]*len(d_sep)
        d_sep['Component']=[componente]*len(d_sep)
        d_sep= d_sep.rename(columns={i:type})
        data_new=data_new._append(d_sep,ignore_index = True) #Uno el dataframe 
    data_new['Band']=data_new['Band'].replace({'_':''}, regex=True)#Quito el _ y lo reemplazo con ''
    try:
        path="{input_path}\data_long\IC".format(input_path=path).replace('\\','/')
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    data_new.reset_index(drop=True).to_feather('{path}\data_{task}_{metric}_long_{name}_{spatial_matrix}_components.feather'.format(path=path,name=data_new['database'].unique()[0],task=data_new['condition'].unique()[0],metric=type,spatial_matrix=spatial_matrix).replace('\\','/'))
    print('Dataframe para graficos de {type} guardado: {name}'.format(type=type,name=name))

def dataframe_componentes_deseadas(data,columnas):
    """Function that returns a dataframe with the desired columns, only having data with the independent components of interest
    columnas=list of columns to be retained
    """
    columnas_deseadas=[*columnas,'C14', 'C15','C18', 'C20', 'C22','C23', 'C24', 'C25'] #columns of interest
    col_completas=list(data.columns)
    columnas=[]
    for i in range(len(columnas_deseadas)):
        for j in range(len(col_completas)):
            if columnas_deseadas[i] in col_completas[j]:
                columnas.append(col_completas[j])
    data_new=data.loc[:,columnas] #Dataframe with columns of interest
    return data_new


def removing_outliers(data,columns):
    '''
    Function used to return a dataframe without outliers, where it is verified that no more than 5$%$ of the data is lost per database.
    '''
    data['index'] = data.index #It was necessary to create a column labeled "index" to take the indexes in an easy way
    data_copy=data.copy()
    databases=data['database'].unique()
    for db in databases:
        datos_db=data[data['database']==db] 
        indices_db=[]
        for com in columns:
            Q1 = np.percentile(datos_db[com], 25, interpolation = 'midpoint')
            Q3 = np.percentile(datos_db[com], 75,interpolation = 'midpoint')
            IQR = Q3 - Q1 
            dataupper=datos_db[datos_db[com] >= (Q3+1.5*IQR)]#Valores atipicos superiores
            if dataupper.empty:
                upper=[]
            else:
                upper=dataupper.index.tolist() #lista de indices del dataframe que son valores atipicos
            datalower=datos_db[datos_db[com] <= (Q1-1.5*IQR)]#Valores atipicos inferiores
            if datalower.empty:
                lower=[]
            else:
                lower=datalower.index.tolist()#lista de indices del dataframe que son valores atipicos
            indices=upper+lower #union de upper y lower de indices del dataframe que son valores atipicos
            indices_db.extend(indices) #Se tiene una lista de indices por cada base de datos
    
        repeticiones=collections.Counter(indices_db) #Diccionario que contiene cuantas veces un indice(sujeto) tiene un dato atipico, en una banda de una componente
        bandera=True
        
        i=2
        while(bandera):#Mientras no se encuentre el porcentaje de perdida requerido
            i+=1 #se aumenta cada que se entra al while
            data_prueba=data.copy()#  copia de data frame para no borrar datos del dataframe original,se crea cada que se entra al while
            index_to_delete=list(dict(filter(lambda x: x[1] > i, repeticiones.items())).keys()) # se crea una lista de los indices cuyas repeticiones de datos atipicos es mayor a i
            data_prueba.drop(index_to_delete, inplace = True)#Se borran los indices del dataframe de prueba para saber el porcentaje de datos borrados
            porcentaje=100-data_prueba[data_prueba['database']==db].shape[0]*100/data[data['database']==db].shape[0]#porcentaje de datos borrados
            if porcentaje<=5:
                #Si el procentaje borrado por primera vez es menor o igual a 5, se borra del dataframe copia los indices que dan el resultado deseado
                data_copy.drop(index_to_delete, inplace = True)
                bandera=False #se cambia la bandera para que no entre mas al while
                #print(porcentaje)
    data_copy=data_copy.drop(columns='index')
    #Para observar un resumen de los datos antes y despues de eliminar sujetos con mayor cantidad de datos atipicos
    for db in databases:
        print('\nBase de datos '+db)
        print('Original')
        print(data[data['database']==db].shape)
        print('Despues de eliminar datos atipicos')
        print(data_copy[data_copy['database']==db].shape)
        print('Porcentaje que se elimino %',100-data_copy[data_copy['database']==db].shape[0]*100/data[data['database']==db].shape[0])
    data_copy=data_copy.reset_index(drop=True)
    return data_copy

#Amount of empty data from demographic data after merging with powers
def ver_datos_vacios(d_B):
    df=pd.DataFrame()
    databases=d_B['database'].unique()
    for i in databases:
        dx=d_B[d_B['database']==i][['age', 'sex', 'education', 'MM_total', 'FAS_F','FAS_S','FAS_A']].isnull().sum()
        df[i]=dx
        print('\n', i)
        print('Numero de sujetos:',len(d_B[d_B['database']==i]['participant_id'].unique()))
        print('Numero de datos:',len(d_B[d_B['database']==i]))
    print('\nCantidad de datos vacios')
    print(df)
    return None

def estadisticos_demograficos(data,name,path):
    """
    Function that exports tables of general description of age, gender and sex of the data.

    link de ayuda
    https://pandas.pydata.org/docs/user_guide/indexing.html
    https://kanoki.org/2022/07/25/pandas-select-slice-rows-columns-multiindex-dataframe/

    """
    
    # import dataframe_image as dfi
    # datos_estadisticos=data.groupby(['group']).describe(include='all')
    # table=datos_estadisticos.loc[:,[('age','count'),('age','mean'),('age','std'),('education','count'),('education','mean'),('education','std'),('sex','count'),('sex','top'),('sex','freq')]]
    # dfi.export(table,'{path}\Tablas_datos\Tabla_edad_escolaridad_sexo_todasBD_{name}.png'.format(path=path,name=name))
    # #Por cada base de datos
    # datos_estadisticos=data.groupby(['database','group']).describe(include='all')
    # table=datos_estadisticos.loc[:,[('age','count'),('age','mean'),('age','std'),('education','count'),('education','mean'),('education','std'),('sex','count'),('sex','top'),('sex','freq')]]
    # dfi.export(table, '{path}\Tablas_datos\Tabla_edad_escolaridad_sexo_separadoBD_{name}.png'.format(path=path,name=name))
    writer = pd.ExcelWriter('{path}\Tablas_datos\Tabla_edad_escolaridad_sexo_{name}.xlsx'.format(path=path,name=name))
    datos_estadisticos=data.groupby(['group']).describe(include='all')
    table=datos_estadisticos.loc[:,[('age','count'),('age','mean'),('age','std'),('education','count'),('education','mean'),('education','std'),('sex','count'),('sex','top'),('sex','freq')]]
    table.to_excel(writer,startrow=0)
    #Por cada base de datos
    datos_estadisticos=data.groupby(['database','group']).describe(include='all')
    table=datos_estadisticos.loc[:,[('age','count'),('age','mean'),('age','std'),('education','count'),('education','mean'),('education','std'),('sex','count'),('sex','top'),('sex','freq')]]
    table.to_excel(writer,startrow=11)
    writer.save()
    writer.close()   


#Listas de columnas
#columns_powers_ic=['power_C14_Delta',
#       'power_C14_Theta', 'power_C14_Alpha-1', 'power_C14_Alpha-2',
#       'power_C14_Beta1', 'power_C14_Beta2', 'power_C14_Beta3',
#       'power_C14_Gamma', 'power_C15_Delta', 'power_C15_Theta',
#       'power_C15_Alpha-1', 'power_C15_Alpha-2', 'power_C15_Beta1',
#       'power_C15_Beta2', 'power_C15_Beta3', 'power_C15_Gamma',
#       'power_C18_Delta', 'power_C18_Theta', 'power_C18_Alpha-1',
#       'power_C18_Alpha-2', 'power_C18_Beta1', 'power_C18_Beta2',
#       'power_C18_Beta3', 'power_C18_Gamma', 'power_C20_Delta',
#       'power_C20_Theta', 'power_C20_Alpha-1', 'power_C20_Alpha-2',
#       'power_C20_Beta1', 'power_C20_Beta2', 'power_C20_Beta3',
#       'power_C20_Gamma', 'power_C22_Delta', 'power_C22_Theta',
#       'power_C22_Alpha-1', 'power_C22_Alpha-2', 'power_C22_Beta1',
#       'power_C22_Beta2', 'power_C22_Beta3', 'power_C22_Gamma',
#       'power_C23_Delta', 'power_C23_Theta', 'power_C23_Alpha-1',
#       'power_C23_Alpha-2', 'power_C23_Beta1', 'power_C23_Beta2',
#       'power_C23_Beta3', 'power_C23_Gamma', 'power_C24_Delta',
#       'power_C24_Theta', 'power_C24_Alpha-1', 'power_C24_Alpha-2',
#       'power_C24_Beta1', 'power_C24_Beta2', 'power_C24_Beta3',
#       'power_C24_Gamma', 'power_C25_Delta', 'power_C25_Theta',
#       'power_C25_Alpha-1', 'power_C25_Alpha-2', 'power_C25_Beta1',
#       'power_C25_Beta2', 'power_C25_Beta3', 'power_C25_Gamma']


columns_powers_rois=['power_F_Delta','power_C_Delta', 'power_PO_Delta', 'power_T_Delta', 'power_F_Theta',
       'power_C_Theta', 'power_PO_Theta', 'power_T_Theta', 'power_F_Alpha-1',
       'power_C_Alpha-1', 'power_PO_Alpha-1', 'power_T_Alpha-1',
       'power_F_Alpha-2', 'power_C_Alpha-2', 'power_PO_Alpha-2',
       'power_T_Alpha-2', 'power_F_Beta1', 'power_C_Beta1', 'power_PO_Beta1',
       'power_T_Beta1', 'power_F_Beta2', 'power_C_Beta2', 'power_PO_Beta2',
       'power_T_Beta2', 'power_F_Beta3', 'power_C_Beta3', 'power_PO_Beta3',
       'power_T_Beta3', 'power_F_Gamma', 'power_C_Gamma', 'power_PO_Gamma',
       'power_T_Gamma']



#Sl columns Roi
columns_SL_roi=['sl_F_Delta', 'sl_C_Delta',
       'sl_PO_Delta', 'sl_T_Delta', 'sl_F_Theta', 'sl_C_Theta', 'sl_PO_Theta',
       'sl_T_Theta', 'sl_F_Alpha-1', 'sl_C_Alpha-1', 'sl_PO_Alpha-1',
       'sl_T_Alpha-1', 'sl_F_Alpha-2', 'sl_C_Alpha-2', 'sl_PO_Alpha-2',
       'sl_T_Alpha-2', 'sl_F_Beta1', 'sl_C_Beta1', 'sl_PO_Beta1', 'sl_T_Beta1',
       'sl_F_Beta2', 'sl_C_Beta2', 'sl_PO_Beta2', 'sl_T_Beta2', 'sl_F_Beta3',
       'sl_C_Beta3', 'sl_PO_Beta3', 'sl_T_Beta3', 'sl_F_Gamma', 'sl_C_Gamma',
       'sl_PO_Gamma', 'sl_T_Gamma']

#Coherence columns Roi
columns_coherence_roi=['cohfreq_F_Delta',
       'cohfreq_C_Delta', 'cohfreq_PO_Delta', 'cohfreq_T_Delta',
       'cohfreq_F_Theta', 'cohfreq_C_Theta', 'cohfreq_PO_Theta',
       'cohfreq_T_Theta', 'cohfreq_F_Alpha-1', 'cohfreq_C_Alpha-1',
       'cohfreq_PO_Alpha-1', 'cohfreq_T_Alpha-1', 'cohfreq_F_Alpha-2',
       'cohfreq_C_Alpha-2', 'cohfreq_PO_Alpha-2', 'cohfreq_T_Alpha-2',
       'cohfreq_F_Beta1', 'cohfreq_C_Beta1', 'cohfreq_PO_Beta1',
       'cohfreq_T_Beta1', 'cohfreq_F_Beta2', 'cohfreq_C_Beta2',
       'cohfreq_PO_Beta2', 'cohfreq_T_Beta2', 'cohfreq_F_Beta3',
       'cohfreq_C_Beta3', 'cohfreq_PO_Beta3', 'cohfreq_T_Beta3',
       'cohfreq_F_Gamma', 'cohfreq_C_Gamma', 'cohfreq_PO_Gamma',
       'cohfreq_T_Gamma']

#Entropy columns Roi  
columns_entropy_rois=['entropy_F_Delta',
       'entropy_C_Delta', 'entropy_PO_Delta', 'entropy_T_Delta',
       'entropy_F_Theta', 'entropy_C_Theta', 'entropy_PO_Theta',
       'entropy_T_Theta', 'entropy_F_Alpha-1', 'entropy_C_Alpha-1',
       'entropy_PO_Alpha-1', 'entropy_T_Alpha-1', 'entropy_F_Alpha-2',
       'entropy_C_Alpha-2', 'entropy_PO_Alpha-2', 'entropy_T_Alpha-2',
       'entropy_F_Beta1', 'entropy_C_Beta1', 'entropy_PO_Beta1',
       'entropy_T_Beta1', 'entropy_F_Beta2', 'entropy_C_Beta2',
       'entropy_PO_Beta2', 'entropy_T_Beta2', 'entropy_F_Beta3',
       'entropy_C_Beta3', 'entropy_PO_Beta3', 'entropy_T_Beta3',
       'entropy_F_Gamma', 'entropy_C_Gamma', 'entropy_PO_Gamma',
       'entropy_T_Gamma']

#columns_SL_ic=['sl_C14_Delta', 'sl_C14_Theta', 'sl_C14_Alpha-1',
#       'sl_C14_Alpha-2', 'sl_C14_Beta1', 'sl_C14_Beta2', 'sl_C14_Beta3',
#       'sl_C14_Gamma', 'sl_C15_Delta', 'sl_C15_Theta', 'sl_C15_Alpha-1',
#       'sl_C15_Alpha-2', 'sl_C15_Beta1', 'sl_C15_Beta2', 'sl_C15_Beta3',
#       'sl_C15_Gamma', 'sl_C18_Delta', 'sl_C18_Theta', 'sl_C18_Alpha-1',
#       'sl_C18_Alpha-2', 'sl_C18_Beta1', 'sl_C18_Beta2', 'sl_C18_Beta3',
#       'sl_C18_Gamma', 'sl_C20_Delta', 'sl_C20_Theta', 'sl_C20_Alpha-1',
#       'sl_C20_Alpha-2', 'sl_C20_Beta1', 'sl_C20_Beta2', 'sl_C20_Beta3',
#       'sl_C20_Gamma', 'sl_C22_Delta', 'sl_C22_Theta', 'sl_C22_Alpha-1',
#       'sl_C22_Alpha-2', 'sl_C22_Beta1', 'sl_C22_Beta2', 'sl_C22_Beta3',
#       'sl_C22_Gamma', 'sl_C23_Delta', 'sl_C23_Theta', 'sl_C23_Alpha-1',
#       'sl_C23_Alpha-2', 'sl_C23_Beta1', 'sl_C23_Beta2', 'sl_C23_Beta3',
#       'sl_C23_Gamma', 'sl_C24_Delta', 'sl_C24_Theta', 'sl_C24_Alpha-1',
#       'sl_C24_Alpha-2', 'sl_C24_Beta1', 'sl_C24_Beta2', 'sl_C24_Beta3',
#       'sl_C24_Gamma','sl_C25_Delta', 'sl_C25_Theta', 'sl_C25_Alpha-1',
#       'sl_C25_Alpha-2', 'sl_C25_Beta1', 'sl_C25_Beta2', 'sl_C25_Beta3',
#       'sl_C25_Gamma']
columns_SL_ic=['sl_C1_Delta', 'sl_C2_Delta', 'sl_C3_Delta', 'sl_C4_Delta',
       'sl_C5_Delta', 'sl_C6_Delta', 'sl_C7_Delta', 'sl_C8_Delta',
       'sl_C9_Delta', 'sl_C10_Delta', 'sl_C1_Theta', 'sl_C2_Theta',
       'sl_C3_Theta', 'sl_C4_Theta', 'sl_C5_Theta', 'sl_C6_Theta',
       'sl_C7_Theta', 'sl_C8_Theta', 'sl_C9_Theta', 'sl_C10_Theta',
       'sl_C1_Alpha-1', 'sl_C2_Alpha-1', 'sl_C3_Alpha-1', 'sl_C4_Alpha-1',
       'sl_C5_Alpha-1', 'sl_C6_Alpha-1', 'sl_C7_Alpha-1', 'sl_C8_Alpha-1',
       'sl_C9_Alpha-1', 'sl_C10_Alpha-1', 'sl_C1_Alpha-2', 'sl_C2_Alpha-2',
       'sl_C3_Alpha-2', 'sl_C4_Alpha-2', 'sl_C5_Alpha-2', 'sl_C6_Alpha-2',
       'sl_C7_Alpha-2', 'sl_C8_Alpha-2', 'sl_C9_Alpha-2', 'sl_C10_Alpha-2',
       'sl_C1_Beta1', 'sl_C2_Beta1', 'sl_C3_Beta1', 'sl_C4_Beta1',
       'sl_C5_Beta1', 'sl_C6_Beta1', 'sl_C7_Beta1', 'sl_C8_Beta1',
       'sl_C9_Beta1', 'sl_C10_Beta1', 'sl_C1_Beta2', 'sl_C2_Beta2',
       'sl_C3_Beta2', 'sl_C4_Beta2', 'sl_C5_Beta2', 'sl_C6_Beta2',
       'sl_C7_Beta2', 'sl_C8_Beta2', 'sl_C9_Beta2', 'sl_C10_Beta2',
       'sl_C1_Beta3', 'sl_C2_Beta3', 'sl_C3_Beta3', 'sl_C4_Beta3',
       'sl_C5_Beta3', 'sl_C6_Beta3', 'sl_C7_Beta3', 'sl_C8_Beta3',
       'sl_C9_Beta3', 'sl_C10_Beta3', 'sl_C1_Gamma', 'sl_C2_Gamma',
       'sl_C3_Gamma', 'sl_C4_Gamma', 'sl_C5_Gamma', 'sl_C6_Gamma',
       'sl_C7_Gamma', 'sl_C8_Gamma', 'sl_C9_Gamma', 'sl_C10_Gamma']
#columns_coherence_ic=['cohfreq_C14_Delta', 'cohfreq_C14_Theta',
#       'cohfreq_C14_Alpha-1', 'cohfreq_C14_Alpha-2', 'cohfreq_C14_Beta1',
#       'cohfreq_C14_Beta2', 'cohfreq_C14_Beta3', 'cohfreq_C14_Gamma',
#       'cohfreq_C15_Delta', 'cohfreq_C15_Theta', 'cohfreq_C15_Alpha-1',
#       'cohfreq_C15_Alpha-2', 'cohfreq_C15_Beta1', 'cohfreq_C15_Beta2',
#       'cohfreq_C15_Beta3', 'cohfreq_C15_Gamma', 'cohfreq_C18_Delta',
#       'cohfreq_C18_Theta', 'cohfreq_C18_Alpha-1', 'cohfreq_C18_Alpha-2',
#       'cohfreq_C18_Beta1', 'cohfreq_C18_Beta2', 'cohfreq_C18_Beta3',
#       'cohfreq_C18_Gamma', 'cohfreq_C20_Delta', 'cohfreq_C20_Theta',
#       'cohfreq_C20_Alpha-1', 'cohfreq_C20_Alpha-2', 'cohfreq_C20_Beta1',
#       'cohfreq_C20_Beta2', 'cohfreq_C20_Beta3', 'cohfreq_C20_Gamma',
#       'cohfreq_C22_Delta', 'cohfreq_C22_Theta', 'cohfreq_C22_Alpha-1',
#       'cohfreq_C22_Alpha-2', 'cohfreq_C22_Beta1', 'cohfreq_C22_Beta2',
#       'cohfreq_C22_Beta3', 'cohfreq_C22_Gamma', 'cohfreq_C23_Delta',
#       'cohfreq_C23_Theta', 'cohfreq_C23_Alpha-1', 'cohfreq_C23_Alpha-2',
#       'cohfreq_C23_Beta1', 'cohfreq_C23_Beta2', 'cohfreq_C23_Beta3',
#       'cohfreq_C23_Gamma', 'cohfreq_C24_Delta', 'cohfreq_C24_Theta',
#       'cohfreq_C24_Alpha-1', 'cohfreq_C24_Alpha-2', 'cohfreq_C24_Beta1',
#       'cohfreq_C24_Beta2', 'cohfreq_C24_Beta3', 'cohfreq_C24_Gamma',
#       'cohfreq_C25_Delta', 'cohfreq_C25_Theta',
#       'cohfreq_C25_Alpha-1', 'cohfreq_C25_Alpha-2', 'cohfreq_C25_Beta1',
#       'cohfreq_C25_Beta2', 'cohfreq_C25_Beta3', 'cohfreq_C25_Gamma']
columns_coherence_ic=['cohfreq_C1_Delta', 'cohfreq_C2_Delta', 'cohfreq_C3_Delta',
       'cohfreq_C4_Delta', 'cohfreq_C5_Delta', 'cohfreq_C6_Delta',
       'cohfreq_C7_Delta', 'cohfreq_C8_Delta', 'cohfreq_C9_Delta',
       'cohfreq_C10_Delta', 'cohfreq_C1_Theta', 'cohfreq_C2_Theta',
       'cohfreq_C3_Theta', 'cohfreq_C4_Theta', 'cohfreq_C5_Theta',
       'cohfreq_C6_Theta', 'cohfreq_C7_Theta', 'cohfreq_C8_Theta',
       'cohfreq_C9_Theta', 'cohfreq_C10_Theta', 'cohfreq_C1_Alpha-1',
       'cohfreq_C2_Alpha-1', 'cohfreq_C3_Alpha-1', 'cohfreq_C4_Alpha-1',
       'cohfreq_C5_Alpha-1', 'cohfreq_C6_Alpha-1', 'cohfreq_C7_Alpha-1',
       'cohfreq_C8_Alpha-1', 'cohfreq_C9_Alpha-1', 'cohfreq_C10_Alpha-1',
       'cohfreq_C1_Alpha-2', 'cohfreq_C2_Alpha-2', 'cohfreq_C3_Alpha-2',
       'cohfreq_C4_Alpha-2', 'cohfreq_C5_Alpha-2', 'cohfreq_C6_Alpha-2',
       'cohfreq_C7_Alpha-2', 'cohfreq_C8_Alpha-2', 'cohfreq_C9_Alpha-2',
       'cohfreq_C10_Alpha-2', 'cohfreq_C1_Beta1', 'cohfreq_C2_Beta1',
       'cohfreq_C3_Beta1', 'cohfreq_C4_Beta1', 'cohfreq_C5_Beta1',
       'cohfreq_C6_Beta1', 'cohfreq_C7_Beta1', 'cohfreq_C8_Beta1',
       'cohfreq_C9_Beta1', 'cohfreq_C10_Beta1', 'cohfreq_C1_Beta2',
       'cohfreq_C2_Beta2', 'cohfreq_C3_Beta2', 'cohfreq_C4_Beta2',
       'cohfreq_C5_Beta2', 'cohfreq_C6_Beta2', 'cohfreq_C7_Beta2',
       'cohfreq_C8_Beta2', 'cohfreq_C9_Beta2', 'cohfreq_C10_Beta2',
       'cohfreq_C1_Beta3', 'cohfreq_C2_Beta3', 'cohfreq_C3_Beta3',
       'cohfreq_C4_Beta3', 'cohfreq_C5_Beta3', 'cohfreq_C6_Beta3',
       'cohfreq_C7_Beta3', 'cohfreq_C8_Beta3', 'cohfreq_C9_Beta3',
       'cohfreq_C10_Beta3', 'cohfreq_C1_Gamma', 'cohfreq_C2_Gamma',
       'cohfreq_C3_Gamma', 'cohfreq_C4_Gamma', 'cohfreq_C5_Gamma',
       'cohfreq_C6_Gamma', 'cohfreq_C7_Gamma', 'cohfreq_C8_Gamma',
       'cohfreq_C9_Gamma', 'cohfreq_C10_Gamma']
#columns_entropy_ic=['entropy_C14_Delta', 'entropy_C14_Theta',
#       'entropy_C14_Alpha-1', 'entropy_C14_Alpha-2', 'entropy_C14_Beta1',
#       'entropy_C14_Beta2', 'entropy_C14_Beta3', 'entropy_C14_Gamma',
#       'entropy_C15_Delta', 'entropy_C15_Theta', 'entropy_C15_Alpha-1',
#       'entropy_C15_Alpha-2', 'entropy_C15_Beta1', 'entropy_C15_Beta2',
#       'entropy_C15_Beta3', 'entropy_C15_Gamma', 'entropy_C18_Delta',
#       'entropy_C18_Theta', 'entropy_C18_Alpha-1', 'entropy_C18_Alpha-2',
#       'entropy_C18_Beta1', 'entropy_C18_Beta2', 'entropy_C18_Beta3',
#       'entropy_C18_Gamma', 'entropy_C20_Delta', 'entropy_C20_Theta',
#       'entropy_C20_Alpha-1', 'entropy_C20_Alpha-2', 'entropy_C20_Beta1',
#       'entropy_C20_Beta2', 'entropy_C20_Beta3', 'entropy_C20_Gamma',
#       'entropy_C22_Delta', 'entropy_C22_Theta', 'entropy_C22_Alpha-1',
#       'entropy_C22_Alpha-2', 'entropy_C22_Beta1', 'entropy_C22_Beta2',
#       'entropy_C22_Beta3', 'entropy_C22_Gamma', 'entropy_C23_Delta',
#       'entropy_C23_Theta', 'entropy_C23_Alpha-1', 'entropy_C23_Alpha-2',
#       'entropy_C23_Beta1', 'entropy_C23_Beta2', 'entropy_C23_Beta3',
#       'entropy_C23_Gamma', 'entropy_C24_Delta', 'entropy_C24_Theta',
#       'entropy_C24_Alpha-1', 'entropy_C24_Alpha-2', 'entropy_C24_Beta1',
#       'entropy_C24_Beta2', 'entropy_C24_Beta3', 'entropy_C24_Gamma',
#       'entropy_C25_Delta', 'entropy_C25_Theta',
#       'entropy_C25_Alpha-1', 'entropy_C25_Alpha-2', 'entropy_C25_Beta1',
#       'entropy_C25_Beta2', 'entropy_C25_Beta3', 'entropy_C25_Gamma']
columns_entropy_ic=['entropy_C1_Delta', 'entropy_C2_Delta', 'entropy_C3_Delta',
       'entropy_C4_Delta', 'entropy_C5_Delta', 'entropy_C6_Delta',
       'entropy_C7_Delta', 'entropy_C8_Delta', 'entropy_C9_Delta',
       'entropy_C10_Delta', 'entropy_C1_Theta', 'entropy_C2_Theta',
       'entropy_C3_Theta', 'entropy_C4_Theta', 'entropy_C5_Theta',
       'entropy_C6_Theta', 'entropy_C7_Theta', 'entropy_C8_Theta',
       'entropy_C9_Theta', 'entropy_C10_Theta', 'entropy_C1_Alpha-1',
       'entropy_C2_Alpha-1', 'entropy_C3_Alpha-1', 'entropy_C4_Alpha-1',
       'entropy_C5_Alpha-1', 'entropy_C6_Alpha-1', 'entropy_C7_Alpha-1',
       'entropy_C8_Alpha-1', 'entropy_C9_Alpha-1', 'entropy_C10_Alpha-1',
       'entropy_C1_Alpha-2', 'entropy_C2_Alpha-2', 'entropy_C3_Alpha-2',
       'entropy_C4_Alpha-2', 'entropy_C5_Alpha-2', 'entropy_C6_Alpha-2',
       'entropy_C7_Alpha-2', 'entropy_C8_Alpha-2', 'entropy_C9_Alpha-2',
       'entropy_C10_Alpha-2', 'entropy_C1_Beta1', 'entropy_C2_Beta1',
       'entropy_C3_Beta1', 'entropy_C4_Beta1', 'entropy_C5_Beta1',
       'entropy_C6_Beta1', 'entropy_C7_Beta1', 'entropy_C8_Beta1',
       'entropy_C9_Beta1', 'entropy_C10_Beta1', 'entropy_C1_Beta2',
       'entropy_C2_Beta2', 'entropy_C3_Beta2', 'entropy_C4_Beta2',
       'entropy_C5_Beta2', 'entropy_C6_Beta2', 'entropy_C7_Beta2',
       'entropy_C8_Beta2', 'entropy_C9_Beta2', 'entropy_C10_Beta2',
       'entropy_C1_Beta3', 'entropy_C2_Beta3', 'entropy_C3_Beta3',
       'entropy_C4_Beta3', 'entropy_C5_Beta3', 'entropy_C6_Beta3',
       'entropy_C7_Beta3', 'entropy_C8_Beta3', 'entropy_C9_Beta3',
       'entropy_C10_Beta3', 'entropy_C1_Gamma', 'entropy_C2_Gamma',
       'entropy_C3_Gamma', 'entropy_C4_Gamma', 'entropy_C5_Gamma',
       'entropy_C6_Gamma', 'entropy_C7_Gamma', 'entropy_C8_Gamma',
       'entropy_C9_Gamma', 'entropy_C10_Gamma']
columns_cross_ic=['crossfreq_C1_Mdelta_Delta', 'crossfreq_C1_Mtheta_Delta',
        'crossfreq_C1_Malpha-1_Delta', 'crossfreq_C1_Malpha-2_Delta',
        'crossfreq_C1_Mbeta1_Delta', 'crossfreq_C1_Mbeta2_Delta', 'crossfreq_C1_Mbeta3_Delta', 
        'crossfreq_C1_Mgamma_Delta', 'crossfreq_C2_Mdelta_Delta', 'crossfreq_C2_Mtheta_Delta',
        'crossfreq_C2_Malpha-1_Delta', 'crossfreq_C2_Malpha-2_Delta', 'crossfreq_C2_Mbeta1_Delta', 
        'crossfreq_C2_Mbeta2_Delta', 'crossfreq_C2_Mbeta3_Delta', 'crossfreq_C2_Mgamma_Delta', 
        'crossfreq_C3_Mdelta_Delta', 'crossfreq_C3_Mtheta_Delta', 'crossfreq_C3_Malpha-1_Delta', 
        'crossfreq_C3_Malpha-2_Delta','crossfreq_C3_Mbeta1_Delta', 'crossfreq_C3_Mbeta2_Delta', 
        'crossfreq_C3_Mbeta3_Delta', 'crossfreq_C3_Mgamma_Delta', 'crossfreq_C4_Mdelta_Delta', 
        'crossfreq_C4_Mtheta_Delta', 'crossfreq_C4_Malpha-1_Delta', 'crossfreq_C4_Malpha-2_Delta', 
        'crossfreq_C4_Mbeta1_Delta', 'crossfreq_C4_Mbeta2_Delta','crossfreq_C4_Mbeta3_Delta', 
        'crossfreq_C4_Mgamma_Delta', 'crossfreq_C5_Mdelta_Delta', 'crossfreq_C5_Mtheta_Delta', 
        'crossfreq_C5_Malpha-1_Delta', 'crossfreq_C5_Malpha-2_Delta', 'crossfreq_C5_Mbeta1_Delta', 
        'crossfreq_C5_Mbeta2_Delta', 'crossfreq_C5_Mbeta3_Delta', 'crossfreq_C5_Mgamma_Delta',
        'crossfreq_C6_Mdelta_Delta', 'crossfreq_C6_Mtheta_Delta', 'crossfreq_C6_Malpha-1_Delta', 
        'crossfreq_C6_Malpha-2_Delta', 'crossfreq_C6_Mbeta1_Delta', 'crossfreq_C6_Mbeta2_Delta', 
        'crossfreq_C6_Mbeta3_Delta', 'crossfreq_C6_Mgamma_Delta', 'crossfreq_C7_Mdelta_Delta', 
        'crossfreq_C7_Mtheta_Delta','crossfreq_C7_Malpha-1_Delta', 'crossfreq_C7_Malpha-2_Delta',
        'crossfreq_C7_Mbeta1_Delta', 'crossfreq_C7_Mbeta2_Delta', 'crossfreq_C7_Mbeta3_Delta',
        'crossfreq_C7_Mgamma_Delta', 'crossfreq_C8_Mdelta_Delta', 'crossfreq_C8_Mtheta_Delta',
        'crossfreq_C8_Malpha-1_Delta', 'crossfreq_C8_Malpha-2_Delta','crossfreq_C8_Mbeta1_Delta',
        'crossfreq_C8_Mbeta2_Delta', 'crossfreq_C8_Mbeta3_Delta', 'crossfreq_C8_Mgamma_Delta',
        'crossfreq_C9_Mdelta_Delta', 'crossfreq_C9_Mtheta_Delta', 'crossfreq_C9_Malpha-1_Delta',
        'crossfreq_C9_Malpha-2_Delta', 'crossfreq_C9_Mbeta1_Delta', 'crossfreq_C9_Mbeta2_Delta',
        'crossfreq_C9_Mbeta3_Delta', 'crossfreq_C9_Mgamma_Delta', 'crossfreq_C10_Mdelta_Delta',
        'crossfreq_C10_Mtheta_Delta', 'crossfreq_C10_Malpha-1_Delta', 'crossfreq_C10_Malpha-2_Delta',
        'crossfreq_C10_Mbeta1_Delta', 'crossfreq_C10_Mbeta2_Delta', 'crossfreq_C10_Mbeta3_Delta',
        'crossfreq_C10_Mgamma_Delta','crossfreq_C1_Mdelta_Theta', 'crossfreq_C1_Mtheta_Theta', 
        'crossfreq_C1_Malpha-1_Theta', 'crossfreq_C1_Malpha-2_Theta', 'crossfreq_C1_Mbeta1_Theta',
        'crossfreq_C1_Mbeta2_Theta', 'crossfreq_C1_Mbeta3_Theta', 'crossfreq_C1_Mgamma_Theta', 
        'crossfreq_C2_Mdelta_Theta', 'crossfreq_C2_Mtheta_Theta','crossfreq_C2_Malpha-1_Theta', 
        'crossfreq_C2_Malpha-2_Theta', 'crossfreq_C2_Mbeta1_Theta', 'crossfreq_C2_Mbeta2_Theta', 
        'crossfreq_C2_Mbeta3_Theta', 'crossfreq_C2_Mgamma_Theta', 'crossfreq_C3_Mdelta_Theta', 
        'crossfreq_C3_Mtheta_Theta', 'crossfreq_C3_Malpha-1_Theta', 'crossfreq_C3_Malpha-2_Theta',
        'crossfreq_C3_Mbeta1_Theta', 'crossfreq_C3_Mbeta2_Theta', 'crossfreq_C3_Mbeta3_Theta', 
        'crossfreq_C3_Mgamma_Theta', 'crossfreq_C4_Mdelta_Theta', 'crossfreq_C4_Mtheta_Theta', 
        'crossfreq_C4_Malpha-1_Theta', 'crossfreq_C4_Malpha-2_Theta', 'crossfreq_C4_Mbeta1_Theta',
        'crossfreq_C4_Mbeta2_Theta','crossfreq_C4_Mbeta3_Theta', 'crossfreq_C4_Mgamma_Theta', 
        'crossfreq_C5_Mdelta_Theta', 'crossfreq_C5_Mtheta_Theta', 'crossfreq_C5_Malpha-1_Theta',
        'crossfreq_C5_Malpha-2_Theta', 'crossfreq_C5_Mbeta1_Theta', 'crossfreq_C5_Mbeta2_Theta',
        'crossfreq_C5_Mbeta3_Theta', 'crossfreq_C5_Mgamma_Theta','crossfreq_C6_Mdelta_Theta', 
        'crossfreq_C6_Mtheta_Theta', 'crossfreq_C6_Malpha-1_Theta', 'crossfreq_C6_Malpha-2_Theta',
        'crossfreq_C6_Mbeta1_Theta', 'crossfreq_C6_Mbeta2_Theta', 'crossfreq_C6_Mbeta3_Theta',
        'crossfreq_C6_Mgamma_Theta', 'crossfreq_C7_Mdelta_Theta', 'crossfreq_C7_Mtheta_Theta',
        'crossfreq_C7_Malpha-1_Theta', 'crossfreq_C7_Malpha-2_Theta', 'crossfreq_C7_Mbeta1_Theta',
        'crossfreq_C7_Mbeta2_Theta', 'crossfreq_C7_Mbeta3_Theta', 'crossfreq_C7_Mgamma_Theta', 
        'crossfreq_C8_Mdelta_Theta', 'crossfreq_C8_Mtheta_Theta', 'crossfreq_C8_Malpha-1_Theta',
        'crossfreq_C8_Malpha-2_Theta','crossfreq_C8_Mbeta1_Theta', 'crossfreq_C8_Mbeta2_Theta',
        'crossfreq_C8_Mbeta3_Theta', 'crossfreq_C8_Mgamma_Theta', 'crossfreq_C9_Mdelta_Theta',
        'crossfreq_C9_Mtheta_Theta', 'crossfreq_C9_Malpha-1_Theta', 'crossfreq_C9_Malpha-2_Theta',
        'crossfreq_C9_Mbeta1_Theta', 'crossfreq_C9_Mbeta2_Theta','crossfreq_C9_Mbeta3_Theta', 
        'crossfreq_C9_Mgamma_Theta', 'crossfreq_C10_Mdelta_Theta', 'crossfreq_C10_Mtheta_Theta',
        'crossfreq_C10_Malpha-1_Theta', 'crossfreq_C10_Malpha-2_Theta', 'crossfreq_C10_Mbeta1_Theta',
        'crossfreq_C10_Mbeta2_Theta', 'crossfreq_C10_Mbeta3_Theta', 'crossfreq_C10_Mgamma_Theta',
        'crossfreq_C1_Mdelta_Alpha-1', 'crossfreq_C1_Mtheta_Alpha-1', 'crossfreq_C1_Malpha-1_Alpha-1',
        'crossfreq_C1_Malpha-2_Alpha-1', 'crossfreq_C1_Mbeta1_Alpha-1', 'crossfreq_C1_Mbeta2_Alpha-1',
        'crossfreq_C1_Mbeta3_Alpha-1', 'crossfreq_C1_Mgamma_Alpha-1', 'crossfreq_C2_Mdelta_Alpha-1',
        'crossfreq_C2_Mtheta_Alpha-1','crossfreq_C2_Malpha-1_Alpha-1', 'crossfreq_C2_Malpha-2_Alpha-1',
        'crossfreq_C2_Mbeta1_Alpha-1', 'crossfreq_C2_Mbeta2_Alpha-1', 'crossfreq_C2_Mbeta3_Alpha-1',
        'crossfreq_C2_Mgamma_Alpha-1', 'crossfreq_C3_Mdelta_Alpha-1', 'crossfreq_C3_Mtheta_Alpha-1',
        'crossfreq_C3_Malpha-1_Alpha-1', 'crossfreq_C3_Malpha-2_Alpha-1','crossfreq_C3_Mbeta1_Alpha-1',
        'crossfreq_C3_Mbeta2_Alpha-1', 'crossfreq_C3_Mbeta3_Alpha-1', 'crossfreq_C3_Mgamma_Alpha-1', 
        'crossfreq_C4_Mdelta_Alpha-1', 'crossfreq_C4_Mtheta_Alpha-1', 'crossfreq_C4_Malpha-1_Alpha-1', 
        'crossfreq_C4_Malpha-2_Alpha-1', 'crossfreq_C4_Mbeta1_Alpha-1', 'crossfreq_C4_Mbeta2_Alpha-1',
        'crossfreq_C4_Mbeta3_Alpha-1', 'crossfreq_C4_Mgamma_Alpha-1', 'crossfreq_C5_Mdelta_Alpha-1',
        'crossfreq_C5_Mtheta_Alpha-1', 'crossfreq_C5_Malpha-1_Alpha-1', 'crossfreq_C5_Malpha-2_Alpha-1', 
        'crossfreq_C5_Mbeta1_Alpha-1', 'crossfreq_C5_Mbeta2_Alpha-1', 'crossfreq_C5_Mbeta3_Alpha-1', 
        'crossfreq_C5_Mgamma_Alpha-1','crossfreq_C6_Mdelta_Alpha-1', 'crossfreq_C6_Mtheta_Alpha-1', 
        'crossfreq_C6_Malpha-1_Alpha-1', 'crossfreq_C6_Malpha-2_Alpha-1', 'crossfreq_C6_Mbeta1_Alpha-1',
        'crossfreq_C6_Mbeta2_Alpha-1', 'crossfreq_C6_Mbeta3_Alpha-1', 'crossfreq_C6_Mgamma_Alpha-1', 
        'crossfreq_C7_Mdelta_Alpha-1', 'crossfreq_C7_Mtheta_Alpha-1','crossfreq_C7_Malpha-1_Alpha-1',
        'crossfreq_C7_Malpha-2_Alpha-1', 'crossfreq_C7_Mbeta1_Alpha-1', 'crossfreq_C7_Mbeta2_Alpha-1', 
        'crossfreq_C7_Mbeta3_Alpha-1', 'crossfreq_C7_Mgamma_Alpha-1', 'crossfreq_C8_Mdelta_Alpha-1', 
        'crossfreq_C8_Mtheta_Alpha-1', 'crossfreq_C8_Malpha-1_Alpha-1', 'crossfreq_C8_Malpha-2_Alpha-1',
        'crossfreq_C8_Mbeta1_Alpha-1', 'crossfreq_C8_Mbeta2_Alpha-1', 'crossfreq_C8_Mbeta3_Alpha-1', 
        'crossfreq_C8_Mgamma_Alpha-1', 'crossfreq_C9_Mdelta_Alpha-1', 'crossfreq_C9_Mtheta_Alpha-1', 
        'crossfreq_C9_Malpha-1_Alpha-1', 'crossfreq_C9_Malpha-2_Alpha-1', 'crossfreq_C9_Mbeta1_Alpha-1',
        'crossfreq_C9_Mbeta2_Alpha-1','crossfreq_C9_Mbeta3_Alpha-1', 'crossfreq_C9_Mgamma_Alpha-1', 
        'crossfreq_C10_Mdelta_Alpha-1', 'crossfreq_C10_Mtheta_Alpha-1', 'crossfreq_C10_Malpha-1_Alpha-1',
        'crossfreq_C10_Malpha-2_Alpha-1', 'crossfreq_C10_Mbeta1_Alpha-1', 'crossfreq_C10_Mbeta2_Alpha-1',
        'crossfreq_C10_Mbeta3_Alpha-1', 'crossfreq_C10_Mgamma_Alpha-1','crossfreq_C1_Mdelta_Alpha-2',
        'crossfreq_C1_Mtheta_Alpha-2', 'crossfreq_C1_Malpha-1_Alpha-2', 'crossfreq_C1_Malpha-2_Alpha-2',
        'crossfreq_C1_Mbeta1_Alpha-2', 'crossfreq_C1_Mbeta2_Alpha-2', 'crossfreq_C1_Mbeta3_Alpha-2', 
        'crossfreq_C1_Mgamma_Alpha-2', 'crossfreq_C2_Mdelta_Alpha-2', 'crossfreq_C2_Mtheta_Alpha-2',
        'crossfreq_C2_Malpha-1_Alpha-2', 'crossfreq_C2_Malpha-2_Alpha-2', 'crossfreq_C2_Mbeta1_Alpha-2',
        'crossfreq_C2_Mbeta2_Alpha-2', 'crossfreq_C2_Mbeta3_Alpha-2', 'crossfreq_C2_Mgamma_Alpha-2', 
        'crossfreq_C3_Mdelta_Alpha-2', 'crossfreq_C3_Mtheta_Alpha-2', 'crossfreq_C3_Malpha-1_Alpha-2', 
        'crossfreq_C3_Malpha-2_Alpha-2','crossfreq_C3_Mbeta1_Alpha-2', 'crossfreq_C3_Mbeta2_Alpha-2', 
        'crossfreq_C3_Mbeta3_Alpha-2', 'crossfreq_C3_Mgamma_Alpha-2', 'crossfreq_C4_Mdelta_Alpha-2', 
        'crossfreq_C4_Mtheta_Alpha-2', 'crossfreq_C4_Malpha-1_Alpha-2', 'crossfreq_C4_Malpha-2_Alpha-2',
        'crossfreq_C4_Mbeta1_Alpha-2', 'crossfreq_C4_Mbeta2_Alpha-2','crossfreq_C4_Mbeta3_Alpha-2', 
        'crossfreq_C4_Mgamma_Alpha-2', 'crossfreq_C5_Mdelta_Alpha-2', 'crossfreq_C5_Mtheta_Alpha-2', 
        'crossfreq_C5_Malpha-1_Alpha-2', 'crossfreq_C5_Malpha-2_Alpha-2', 'crossfreq_C5_Mbeta1_Alpha-2', 
        'crossfreq_C5_Mbeta2_Alpha-2', 'crossfreq_C5_Mbeta3_Alpha-2', 'crossfreq_C5_Mgamma_Alpha-2',
        'crossfreq_C6_Mdelta_Alpha-2', 'crossfreq_C6_Mtheta_Alpha-2', 'crossfreq_C6_Malpha-1_Alpha-2', 
        'crossfreq_C6_Malpha-2_Alpha-2', 'crossfreq_C6_Mbeta1_Alpha-2', 'crossfreq_C6_Mbeta2_Alpha-2', 
        'crossfreq_C6_Mbeta3_Alpha-2', 'crossfreq_C6_Mgamma_Alpha-2', 'crossfreq_C7_Mdelta_Alpha-2', 
        'crossfreq_C7_Mtheta_Alpha-2','crossfreq_C7_Malpha-1_Alpha-2', 'crossfreq_C7_Malpha-2_Alpha-2', 
        'crossfreq_C7_Mbeta1_Alpha-2', 'crossfreq_C7_Mbeta2_Alpha-2', 'crossfreq_C7_Mbeta3_Alpha-2', 
        'crossfreq_C7_Mgamma_Alpha-2', 'crossfreq_C8_Mdelta_Alpha-2', 'crossfreq_C8_Mtheta_Alpha-2', 
        'crossfreq_C8_Malpha-1_Alpha-2', 'crossfreq_C8_Malpha-2_Alpha-2','crossfreq_C8_Mbeta1_Alpha-2',
        'crossfreq_C8_Mbeta2_Alpha-2', 'crossfreq_C8_Mbeta3_Alpha-2', 'crossfreq_C8_Mgamma_Alpha-2', 
        'crossfreq_C9_Mdelta_Alpha-2', 'crossfreq_C9_Mtheta_Alpha-2', 'crossfreq_C9_Malpha-1_Alpha-2', 
        'crossfreq_C9_Malpha-2_Alpha-2', 'crossfreq_C9_Mbeta1_Alpha-2', 'crossfreq_C9_Mbeta2_Alpha-2',
        'crossfreq_C9_Mbeta3_Alpha-2', 'crossfreq_C9_Mgamma_Alpha-2', 'crossfreq_C10_Mdelta_Alpha-2', 
        'crossfreq_C10_Mtheta_Alpha-2', 'crossfreq_C10_Malpha-1_Alpha-2', 'crossfreq_C10_Malpha-2_Alpha-2',
        'crossfreq_C10_Mbeta1_Alpha-2', 'crossfreq_C10_Mbeta2_Alpha-2', 'crossfreq_C10_Mbeta3_Alpha-2',
        'crossfreq_C10_Mgamma_Alpha-2','crossfreq_C1_Mdelta_Beta1', 'crossfreq_C1_Mtheta_Beta1', 
        'crossfreq_C1_Malpha-1_Beta1', 'crossfreq_C1_Malpha-2_Beta1', 'crossfreq_C1_Mbeta1_Beta1', 
        'crossfreq_C1_Mbeta2_Beta1', 'crossfreq_C1_Mbeta3_Beta1', 'crossfreq_C1_Mgamma_Beta1', 
        'crossfreq_C2_Mdelta_Beta1', 'crossfreq_C2_Mtheta_Beta1','crossfreq_C2_Malpha-1_Beta1', 
        'crossfreq_C2_Malpha-2_Beta1', 'crossfreq_C2_Mbeta1_Beta1', 'crossfreq_C2_Mbeta2_Beta1', 
        'crossfreq_C2_Mbeta3_Beta1', 'crossfreq_C2_Mgamma_Beta1', 'crossfreq_C3_Mdelta_Beta1', 
        'crossfreq_C3_Mtheta_Beta1', 'crossfreq_C3_Malpha-1_Beta1', 'crossfreq_C3_Malpha-2_Beta1',
        'crossfreq_C3_Mbeta1_Beta1', 'crossfreq_C3_Mbeta2_Beta1', 'crossfreq_C3_Mbeta3_Beta1', 
        'crossfreq_C3_Mgamma_Beta1', 'crossfreq_C4_Mdelta_Beta1', 'crossfreq_C4_Mtheta_Beta1', 
        'crossfreq_C4_Malpha-1_Beta1', 'crossfreq_C4_Malpha-2_Beta1', 'crossfreq_C4_Mbeta1_Beta1', 
        'crossfreq_C4_Mbeta2_Beta1','crossfreq_C4_Mbeta3_Beta1', 'crossfreq_C4_Mgamma_Beta1', 
        'crossfreq_C5_Mdelta_Beta1', 'crossfreq_C5_Mtheta_Beta1', 'crossfreq_C5_Malpha-1_Beta1', 
        'crossfreq_C5_Malpha-2_Beta1', 'crossfreq_C5_Mbeta1_Beta1', 'crossfreq_C5_Mbeta2_Beta1', 
        'crossfreq_C5_Mbeta3_Beta1', 'crossfreq_C5_Mgamma_Beta1','crossfreq_C6_Mdelta_Beta1', 
        'crossfreq_C6_Mtheta_Beta1', 'crossfreq_C6_Malpha-1_Beta1', 'crossfreq_C6_Malpha-2_Beta1', 
        'crossfreq_C6_Mbeta1_Beta1', 'crossfreq_C6_Mbeta2_Beta1', 'crossfreq_C6_Mbeta3_Beta1', 
        'crossfreq_C6_Mgamma_Beta1', 'crossfreq_C7_Mdelta_Beta1', 'crossfreq_C7_Mtheta_Beta1',
        'crossfreq_C7_Malpha-1_Beta1', 'crossfreq_C7_Malpha-2_Beta1', 'crossfreq_C7_Mbeta1_Beta1',
        'crossfreq_C7_Mbeta2_Beta1', 'crossfreq_C7_Mbeta3_Beta1', 'crossfreq_C7_Mgamma_Beta1', 
        'crossfreq_C8_Mdelta_Beta1', 'crossfreq_C8_Mtheta_Beta1', 'crossfreq_C8_Malpha-1_Beta1', 
        'crossfreq_C8_Malpha-2_Beta1','crossfreq_C8_Mbeta1_Beta1', 'crossfreq_C8_Mbeta2_Beta1', 
        'crossfreq_C8_Mbeta3_Beta1', 'crossfreq_C8_Mgamma_Beta1', 'crossfreq_C9_Mdelta_Beta1', 
        'crossfreq_C9_Mtheta_Beta1', 'crossfreq_C9_Malpha-1_Beta1', 'crossfreq_C9_Malpha-2_Beta1', 
        'crossfreq_C9_Mbeta1_Beta1', 'crossfreq_C9_Mbeta2_Beta1','crossfreq_C9_Mbeta3_Beta1',
        'crossfreq_C9_Mgamma_Beta1', 'crossfreq_C10_Mdelta_Beta1', 'crossfreq_C10_Mtheta_Beta1', 
        'crossfreq_C10_Malpha-1_Beta1', 'crossfreq_C10_Malpha-2_Beta1', 'crossfreq_C10_Mbeta1_Beta1', 
        'crossfreq_C10_Mbeta2_Beta1', 'crossfreq_C10_Mbeta3_Beta1', 'crossfreq_C10_Mgamma_Beta1',
        'crossfreq_C1_Mdelta_Beta2', 'crossfreq_C1_Mtheta_Beta2', 'crossfreq_C1_Malpha-1_Beta2', 
        'crossfreq_C1_Malpha-2_Beta2', 'crossfreq_C1_Mbeta1_Beta2', 'crossfreq_C1_Mbeta2_Beta2',
        'crossfreq_C1_Mbeta3_Beta2', 'crossfreq_C1_Mgamma_Beta2', 'crossfreq_C2_Mdelta_Beta2', 
        'crossfreq_C2_Mtheta_Beta2','crossfreq_C2_Malpha-1_Beta2', 'crossfreq_C2_Malpha-2_Beta2',
        'crossfreq_C2_Mbeta1_Beta2', 'crossfreq_C2_Mbeta2_Beta2', 'crossfreq_C2_Mbeta3_Beta2', 
        'crossfreq_C2_Mgamma_Beta2', 'crossfreq_C3_Mdelta_Beta2', 'crossfreq_C3_Mtheta_Beta2',
        'crossfreq_C3_Malpha-1_Beta2', 'crossfreq_C3_Malpha-2_Beta2','crossfreq_C3_Mbeta1_Beta2', 
        'crossfreq_C3_Mbeta2_Beta2', 'crossfreq_C3_Mbeta3_Beta2', 'crossfreq_C3_Mgamma_Beta2',
        'crossfreq_C4_Mdelta_Beta2', 'crossfreq_C4_Mtheta_Beta2', 'crossfreq_C4_Malpha-1_Beta2', 
        'crossfreq_C4_Malpha-2_Beta2', 'crossfreq_C4_Mbeta1_Beta2', 'crossfreq_C4_Mbeta2_Beta2',
        'crossfreq_C4_Mbeta3_Beta2', 'crossfreq_C4_Mgamma_Beta2', 'crossfreq_C5_Mdelta_Beta2', 
        'crossfreq_C5_Mtheta_Beta2', 'crossfreq_C5_Malpha-1_Beta2', 'crossfreq_C5_Malpha-2_Beta2', 
        'crossfreq_C5_Mbeta1_Beta2', 'crossfreq_C5_Mbeta2_Beta2', 'crossfreq_C5_Mbeta3_Beta2', 
        'crossfreq_C5_Mgamma_Beta2','crossfreq_C6_Mdelta_Beta2', 'crossfreq_C6_Mtheta_Beta2',
        'crossfreq_C6_Malpha-1_Beta2', 'crossfreq_C6_Malpha-2_Beta2', 'crossfreq_C6_Mbeta1_Beta2', 
        'crossfreq_C6_Mbeta2_Beta2', 'crossfreq_C6_Mbeta3_Beta2', 'crossfreq_C6_Mgamma_Beta2', 
        'crossfreq_C7_Mdelta_Beta2', 'crossfreq_C7_Mtheta_Beta2','crossfreq_C7_Malpha-1_Beta2', 
        'crossfreq_C7_Malpha-2_Beta2', 'crossfreq_C7_Mbeta1_Beta2', 'crossfreq_C7_Mbeta2_Beta2',
        'crossfreq_C7_Mbeta3_Beta2', 'crossfreq_C7_Mgamma_Beta2', 'crossfreq_C8_Mdelta_Beta2',
        'crossfreq_C8_Mtheta_Beta2', 'crossfreq_C8_Malpha-1_Beta2', 'crossfreq_C8_Malpha-2_Beta2',
        'crossfreq_C8_Mbeta1_Beta2', 'crossfreq_C8_Mbeta2_Beta2', 'crossfreq_C8_Mbeta3_Beta2', 
        'crossfreq_C8_Mgamma_Beta2', 'crossfreq_C9_Mdelta_Beta2', 'crossfreq_C9_Mtheta_Beta2', 
        'crossfreq_C9_Malpha-1_Beta2', 'crossfreq_C9_Malpha-2_Beta2', 'crossfreq_C9_Mbeta1_Beta2',
        'crossfreq_C9_Mbeta2_Beta2','crossfreq_C9_Mbeta3_Beta2', 'crossfreq_C9_Mgamma_Beta2', 
        'crossfreq_C10_Mdelta_Beta2', 'crossfreq_C10_Mtheta_Beta2', 'crossfreq_C10_Malpha-1_Beta2',
        'crossfreq_C10_Malpha-2_Beta2', 'crossfreq_C10_Mbeta1_Beta2', 'crossfreq_C10_Mbeta2_Beta2', 
        'crossfreq_C10_Mbeta3_Beta2', 'crossfreq_C10_Mgamma_Beta2','crossfreq_C1_Mdelta_Beta3', 
        'crossfreq_C1_Mtheta_Beta3', 'crossfreq_C1_Malpha-1_Beta3', 'crossfreq_C1_Malpha-2_Beta3', 
        'crossfreq_C1_Mbeta1_Beta3', 'crossfreq_C1_Mbeta2_Beta3', 'crossfreq_C1_Mbeta3_Beta3', 
        'crossfreq_C1_Mgamma_Beta3', 'crossfreq_C2_Mdelta_Beta3', 'crossfreq_C2_Mtheta_Beta3',
        'crossfreq_C2_Malpha-1_Beta3', 'crossfreq_C2_Malpha-2_Beta3', 'crossfreq_C2_Mbeta1_Beta3',
        'crossfreq_C2_Mbeta2_Beta3', 'crossfreq_C2_Mbeta3_Beta3', 'crossfreq_C2_Mgamma_Beta3', 
        'crossfreq_C3_Mdelta_Beta3', 'crossfreq_C3_Mtheta_Beta3', 'crossfreq_C3_Malpha-1_Beta3', 
        'crossfreq_C3_Malpha-2_Beta3','crossfreq_C3_Mbeta1_Beta3', 'crossfreq_C3_Mbeta2_Beta3', 
        'crossfreq_C3_Mbeta3_Beta3', 'crossfreq_C3_Mgamma_Beta3', 'crossfreq_C4_Mdelta_Beta3', 
        'crossfreq_C4_Mtheta_Beta3', 'crossfreq_C4_Malpha-1_Beta3', 'crossfreq_C4_Malpha-2_Beta3',
        'crossfreq_C4_Mbeta1_Beta3', 'crossfreq_C4_Mbeta2_Beta3','crossfreq_C4_Mbeta3_Beta3', 
        'crossfreq_C4_Mgamma_Beta3', 'crossfreq_C5_Mdelta_Beta3', 'crossfreq_C5_Mtheta_Beta3',
        'crossfreq_C5_Malpha-1_Beta3', 'crossfreq_C5_Malpha-2_Beta3', 'crossfreq_C5_Mbeta1_Beta3', 
        'crossfreq_C5_Mbeta2_Beta3', 'crossfreq_C5_Mbeta3_Beta3', 'crossfreq_C5_Mgamma_Beta3',
        'crossfreq_C6_Mdelta_Beta3', 'crossfreq_C6_Mtheta_Beta3', 'crossfreq_C6_Malpha-1_Beta3',
        'crossfreq_C6_Malpha-2_Beta3', 'crossfreq_C6_Mbeta1_Beta3', 'crossfreq_C6_Mbeta2_Beta3',
        'crossfreq_C6_Mbeta3_Beta3', 'crossfreq_C6_Mgamma_Beta3', 'crossfreq_C7_Mdelta_Beta3',
        'crossfreq_C7_Mtheta_Beta3','crossfreq_C7_Malpha-1_Beta3', 'crossfreq_C7_Malpha-2_Beta3',
        'crossfreq_C7_Mbeta1_Beta3', 'crossfreq_C7_Mbeta2_Beta3', 'crossfreq_C7_Mbeta3_Beta3', 
        'crossfreq_C7_Mgamma_Beta3', 'crossfreq_C8_Mdelta_Beta3', 'crossfreq_C8_Mtheta_Beta3', 
        'crossfreq_C8_Malpha-1_Beta3', 'crossfreq_C8_Malpha-2_Beta3','crossfreq_C8_Mbeta1_Beta3',
        'crossfreq_C8_Mbeta2_Beta3', 'crossfreq_C8_Mbeta3_Beta3', 'crossfreq_C8_Mgamma_Beta3', 
        'crossfreq_C9_Mdelta_Beta3', 'crossfreq_C9_Mtheta_Beta3', 'crossfreq_C9_Malpha-1_Beta3',
        'crossfreq_C9_Malpha-2_Beta3', 'crossfreq_C9_Mbeta1_Beta3', 'crossfreq_C9_Mbeta2_Beta3',
        'crossfreq_C9_Mbeta3_Beta3', 'crossfreq_C9_Mgamma_Beta3', 'crossfreq_C10_Mdelta_Beta3',
        'crossfreq_C10_Mtheta_Beta3', 'crossfreq_C10_Malpha-1_Beta3', 'crossfreq_C10_Malpha-2_Beta3',
        'crossfreq_C10_Mbeta1_Beta3', 'crossfreq_C10_Mbeta2_Beta3', 'crossfreq_C10_Mbeta3_Beta3', 
        'crossfreq_C10_Mgamma_Beta3','crossfreq_C1_Mdelta_Gamma', 'crossfreq_C1_Mtheta_Gamma', 
        'crossfreq_C1_Malpha-1_Gamma', 'crossfreq_C1_Malpha-2_Gamma', 'crossfreq_C1_Mbeta1_Gamma',
        'crossfreq_C1_Mbeta2_Gamma', 'crossfreq_C1_Mbeta3_Gamma', 'crossfreq_C1_Mgamma_Gamma',
        'crossfreq_C2_Mdelta_Gamma', 'crossfreq_C2_Mtheta_Gamma','crossfreq_C2_Malpha-1_Gamma',
        'crossfreq_C2_Malpha-2_Gamma', 'crossfreq_C2_Mbeta1_Gamma', 'crossfreq_C2_Mbeta2_Gamma',
        'crossfreq_C2_Mbeta3_Gamma', 'crossfreq_C2_Mgamma_Gamma', 'crossfreq_C3_Mdelta_Gamma',
        'crossfreq_C3_Mtheta_Gamma', 'crossfreq_C3_Malpha-1_Gamma', 'crossfreq_C3_Malpha-2_Gamma',
        'crossfreq_C3_Mbeta1_Gamma', 'crossfreq_C3_Mbeta2_Gamma', 'crossfreq_C3_Mbeta3_Gamma',
        'crossfreq_C3_Mgamma_Gamma', 'crossfreq_C4_Mdelta_Gamma', 'crossfreq_C4_Mtheta_Gamma',
        'crossfreq_C4_Malpha-1_Gamma', 'crossfreq_C4_Malpha-2_Gamma', 'crossfreq_C4_Mbeta1_Gamma',
        'crossfreq_C4_Mbeta2_Gamma','crossfreq_C4_Mbeta3_Gamma', 'crossfreq_C4_Mgamma_Gamma',
        'crossfreq_C5_Mdelta_Gamma', 'crossfreq_C5_Mtheta_Gamma', 'crossfreq_C5_Malpha-1_Gamma', 
        'crossfreq_C5_Malpha-2_Gamma', 'crossfreq_C5_Mbeta1_Gamma', 'crossfreq_C5_Mbeta2_Gamma', 
        'crossfreq_C5_Mbeta3_Gamma', 'crossfreq_C5_Mgamma_Gamma','crossfreq_C6_Mdelta_Gamma', 
        'crossfreq_C6_Mtheta_Gamma', 'crossfreq_C6_Malpha-1_Gamma', 'crossfreq_C6_Malpha-2_Gamma',
        'crossfreq_C6_Mbeta1_Gamma', 'crossfreq_C6_Mbeta2_Gamma', 'crossfreq_C6_Mbeta3_Gamma',
        'crossfreq_C6_Mgamma_Gamma', 'crossfreq_C7_Mdelta_Gamma', 'crossfreq_C7_Mtheta_Gamma', 
        'crossfreq_C7_Malpha-1_Gamma', 'crossfreq_C7_Malpha-2_Gamma', 'crossfreq_C7_Mbeta1_Gamma', 
        'crossfreq_C7_Mbeta2_Gamma', 'crossfreq_C7_Mbeta3_Gamma', 'crossfreq_C7_Mgamma_Gamma', 
        'crossfreq_C8_Mdelta_Gamma', 'crossfreq_C8_Mtheta_Gamma', 'crossfreq_C8_Malpha-1_Gamma', 
        'crossfreq_C8_Malpha-2_Gamma','crossfreq_C8_Mbeta1_Gamma', 'crossfreq_C8_Mbeta2_Gamma', 
        'crossfreq_C8_Mbeta3_Gamma', 'crossfreq_C8_Mgamma_Gamma', 'crossfreq_C9_Mdelta_Gamma', 
        'crossfreq_C9_Mtheta_Gamma', 'crossfreq_C9_Malpha-1_Gamma', 'crossfreq_C9_Malpha-2_Gamma',
        'crossfreq_C9_Mbeta1_Gamma', 'crossfreq_C9_Mbeta2_Gamma', 'crossfreq_C9_Mbeta3_Gamma', 
        'crossfreq_C9_Mgamma_Gamma', 'crossfreq_C10_Mdelta_Gamma', 'crossfreq_C10_Mtheta_Gamma', 
        'crossfreq_C10_Malpha-1_Gamma', 'crossfreq_C10_Malpha-2_Gamma', 'crossfreq_C10_Mbeta1_Gamma',
        'crossfreq_C10_Mbeta2_Gamma', 'crossfreq_C10_Mbeta3_Gamma', 'crossfreq_C10_Mgamma_Gamma']

'''manejo de pandas: https://joserzapata.github.io/courses/python-ciencia-datos/pandas/'''

