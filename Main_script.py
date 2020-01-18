
# coding: utf-8

# In[1]:


import os
import re
import numpy as np
import json
import time


# In[2]:


def GEOM( x,y, workpass):
    import numpy  as np
    import sys, os
    import time
    import script_pat
    pathg = os.path.join(workpass, r'x='+str(x)+'y='+str(y)+'geom.py')
    DTF=os.path.join(workpass, r'x='+str(x)+'y='+str(y)+'.DTF')
    print('создание script_geom...')
   
    with open(pathg, 'w') as fg:
        textg = script_pat.pat.format(str(x), str(y), pathg[0:-3],pathg[0:-7])
        fg.write(textg)
    
    print(pathg)
    print('_________________________________________________________________________________________________________')
    ###############################################################################################################
    os.system('CFD-GEOM -script '+str(pathg))
    while(not os.path.exists(str(pathg[0:-7])+'.DTF')):
        print ("*")
        time.sleep(1)
    print('GEOM_COMPLETE')
    time.sleep(2)
    print('_________________________________________________________________________________________________________')
    ###############################################################################################################


# In[3]:


def ACE(x,y, p, workpass):
    import os
    import time
    import script_pat
    print('создание script_ace')
    
    patha = os.path.join(workpass, r'x='+str(x)+'y='+str(y)+'ace.py')
    with open(patha,'w') as fa:
    
        texta=script_pat.ace_pat.format(patha[0:-6],p)
        fa.write(texta)
    
    print(patha)
    print('_________________________________________________________________________________________________________')
    ###############################################################################################################
    print("waiting...\n")
    os.system('CFD-ACE-GUI -script '+patha)
    # ждём начала процедуры запуска
    while( not os.path.exists(str(patha[0:-6])+ '.out')):
        print('*')
        time.sleep(1)
    time.sleep(5) # ещё ждём немного, пока солвер запустится
    # ждём завершения процесса солвера
    while(os.path.exists(str(patha[0:-6])+'.RUN')):
        time.sleep(30)
    print('ACE_COMPLATE')
    old_file = str(patha[0:-6])+'.DTF'
    new_file = str(patha[0:-6])+'_p='+str(p)+'.DTF' #Переименование файла для отслеживания значения давления
    os.rename(old_file,new_file)
    print('file_rename')
    time.sleep(3)
    
    print('_________________________________________________________________________________________________________')


# In[4]:

def VIEW(x,y,p,workpass):
    import os
    import time
    print('создание script_view')
    
    pathv = os.path.join(workpass, r'x='+str(x)+'y='+str(y)+'view.py')
    
   
    q='''
k=1.4
a=Mach
b=a*U*RHO*2*3.1415*Y
fs=U*RHO*2*3.1415*Y
c=linteg(b)/linteg(fs)
l=sqrt(((k+1)/2*c[1]*c[1])/(1+((k-1)/(2))*c[1]*c[1]))
q=l[1]*((k+1)/2)^(1/(k-1))*(1-((k-1)/2)*c[1]*c[1])^(1/(k-1))
    '''
    Mach='''
a=(Mach)*2*3.1415*Y
ymin=min(Y)
ymax=max(Y)
b=linteg(a)/(3.1415*(ymax*ymax-ymin*ymin))
    '''
    P_tot='''
a=(P_tot)*2*3.1415*Y
ymin=min(Y)
ymax=max(Y)
b=linteg(a)/(3.1415*(ymax*ymax-ymin*ymin))
    '''
    Vmag='''
    a=(VelocityMagnitude)*2*3.1415*Y
ymin=min(Y)
ymax=max(Y)
b=linteg(a)/(3.1415*(ymax*ymax-ymin*ymin))
    '''
    RHO='''
    a=(RHO)*2*3.1415*Y
ymin=min(Y)
ymax=max(Y)
b=linteg(a)/(3.1415*(ymax*ymax-ymin*ymin))
    '''
    textv='''from cfdview import *
from cfdview_basic import *
ImportDTF(r"'''+pathv[0:-7]+'_p='+str(p)+'''.DTF'''+'''",DTF_SIMPLIFYING)
surf=[GetObjectsByType("Surface")[1],GetObjectsByType("Surface")[2]]
SetColorAttribute(surf,'U')
SetSurfaceRendering(surf, SURFACE_RENDERING_SMOOTH)
cut=CreateXSlice(surf)
SetValue(cut,2.4999)
cut.setName('A')
SetExpression(cut,'''+'\'\'\''+q+'\'\'\''+''')
ForceUpdate()
q = GetExpressionResult(cut)[0]
SetExpression(cut,'''+'\'\'\''+P_tot+'\'\'\''+''')
ForceUpdate()
P_tot = GetExpressionResult(cut)[0]
SetExpression(cut,'''+'\'\'\''+Mach+'\'\'\''+''')
ForceUpdate()
Mach = GetExpressionResult(cut)[0]
SetExpression(cut,'''+'\'\'\''+Vmag+'\'\'\''+''')
ForceUpdate()
Vmag = GetExpressionResult(cut)[0]
SetExpression(cut,'''+'\'\'\''+RHO+'\'\'\''+''')
ForceUpdate()
RHO = GetExpressionResult(cut)[0]
i = open(r"'''+str(pathv[0:-7])+'''_result.txt", 'w')
i.write(str(q)'''+'+'+r''''\n'+str(P_tot)'''+'+'+r''''\n'+str(Mach)'''+'+'+r''''\n'+str(Vmag)'''+'+'+r''''\n'+str(RHO))
i.close()
quit()
    '''
    with open(pathv, 'w') as fv:
        fv.write(textv)
    
    print(pathv)
    print('_________________________________________________________________________________________________________')
    ###############################################################################################################
    cmd='CFD-VIEW -script '+pathv
    os.system(cmd)
    rez=str(pathv[0:-7])+'_result.txt'
    while(not os.path.exists(rez)):
        time.sleep(1)
    print(rez)
    
    result = {
        'q': 0.0,
        'P_tot': 0.0,
        'Mach': 0.0,
        'Vmag': 0.0,
        'RHO':0.0
    }
    with open(rez, 'r') as rez:
        result['q']=float(rez.readline()[:-2])
        result['P_tot']=float(rez.readline()[:-2])
        result['Mach']=float(rez.readline()[:-2])
        result['Vmag']=float(rez.readline()[:-2])
        result['RHO']=float(rez.readline())
    print('VIEW_COMPLETE')
    print('_________________________________________________________________________________________________________')
    return result
    ###############################################################################################################


# In[5]:


def FORCE(x,y,workpass):
    pathforce = os.path.join(workpass, r'x='+str(x)+'y='+str(y)+'.FMSUM')
    testforce=os.path.exists(pathforce)
    farray = []
    state=0
    FX=[]
    FY=[]
    FXsum=[]
    FYsum=[]
    s=0
    result = {'WALLDOWN':#Внутренние стенки ВЗУ
             {'FX':[],'FY':[]},
             'WALLUP':#Внешние стенки ВЗУ
             {'FX':[],'FY':[]},
             'WALLCENT': #Стенка на кромке ВЗУ
             {'FX':[],'FY':[]},
             'WALLIN': #Донная стенка
             {'FX':[],'FY':[]},
             'SUM': #Донная стенка
             {'FX':[],'FY':[]}}
    if(testforce):
        with open(pathforce, "r") as ins:
            for line in ins: #Разделение файла с силами
                a=re.split(r'\s+', line) #Разделение по 'tab'
                try: 
                    if a[1]=='WALLDOWN':
                        FX=float(a[3])
                        FY=float(a[4])
                        result['WALLDOWN']['FX'].append(FX)
                        result['WALLDOWN']['FY'].append(FY)
                    elif a[1]=='WALLUP':
                        FX=float(a[3])
                        FY=float(a[4])
                        result['WALLUP']['FX'].append(FX)
                        result['WALLUP']['FY'].append(FY)
                    elif a[1]=='WALLCENT':
                        FX=float(a[3])
                        FY=float(a[4])
                        result['WALLCENT']['FX'].append(FX)
                        result['WALLCENT']['FY'].append(FY)
                    elif a[1]=='WALLIN':
                        FX=float(a[3])
                        FY=float(a[4])
                        result['WALLIN']['FX'].append(FX)
                        result['WALLIN']['FY'].append(FY)
                    elif a[1]=='Proc':
                        FX=float(a[4])
                        FY=float(a[5])
                        result['SUM']['FX'].append(FX)
                        result['SUM']['FY'].append(FY)
                except Exception:
                    pass                
    return result


# In[6]:


def step(x,y,workpass):
    p = 30e3
    result={}
    try:
        os.makedirs(workpass)
    except FileExistsError:
        pass
    GEOM(x,y,workpass)
    ACE(x,y,p,workpass)
    view = VIEW(x,y,p,workpass)
    q = view['q']
    pn = 0.0
    qn=0.0
    if q<0.8:
        pn = p - 2500 
    else:
        pn = p + 2500
    GEOM(x,y,workpass)
    ACE(x,y,pn,workpass)
    view = VIEW(x,y,pn,workpass)
    qn = view['q']
    k = (p-pn)/(q-qn)
    b = p - k*q
    p = 0.8*k + b
    GEOM(x,y,workpass)
    ACE(x,y,p,workpass)
    view = VIEW(x,y,p,workpass)
    result['FORCE'] = FORCE(x,y, workpass)
    result['view'] = view
    result['A'] = x
    result['B'] = y
    result['CX']=result['FORCE']['SUM']['FX'][-1]/(1/2*view['RHO']*view['Vmag']**2)
    result['KQ']=view['P_tot']/40297.7421875-0.5*(result['CX']/0.04050686760090751)
    return result


# In[7]:


def generate_grid(x,y,step):
    len_A =  -0.01 - -0.117
    len_B = 0.02499 - -0.07
        
    xi = np.array([
        x - len_A*step, x, x + len_A*step
    ])
    
    yi = np.array([
        y - len_B*step, y, y + len_B*step
    ])
    
    XX, YY = np.meshgrid(xi, yi)
   
    return XX.flatten(), YY.flatten()


# In[8]:


def find_best(cases):
    i_max = 0
    for index, case in enumerate(cases):
        if cases[index]['KQ'] > cases[i_max]['KQ']:
            i_max = index
            
    return i_max
            


# In[9]:


def write_blank_json(path):
    res = []
    with open(path, 'w') as file: 
        json.dump(res, file)


# In[10]:


odz_A = np.array([-0.117, -0.01])
odz_B = np.array([-0.07, 0.02499])


# In[11]:



def step_1(x):
    return step(*x)

# In[12]:


from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


# In[13]:


def optimize():
    odz_A = np.array([-0.117, -0.01])
    odz_B = np.array([-0.07, 0.02499])  
    work_dir = r'F:/optymize'
    common_json = r'F:/optymize/optimize.json'
    
    write_blank_json(common_json)
       
    delta = 0.2
    A0, B0 = (odz_A[0]-odz_A[-1])/2, (odz_B[0]-odz_B[-1])/2
    ai, bi = generate_grid(A0, B0, delta)
    i=0
    pool = ThreadPool(9)
    while delta > 1e-5:
        
        
        args = []
        for x,y in zip(ai,bi):
            if odz_A[0] <= x <= odz_A[1] and odz_B[0] <= y <= odz_B[1]:
                i+=1
                step_dir = os.path.join(work_dir, f'step_{i}')
                args.append([x,y,step_dir])
        
        
        steps = pool.map(step_1, args)
        print(steps)
        best_case = find_best(steps)
        
        if best_case == 5:
            delta = delta*0.6
        else:
            delta = delta*0.95
            
        A,B = steps[best_case]['A'], steps[best_case]['B']
        ai, bi = generate_grid(A, B, delta)
        
        with open(common_json, 'r') as file:
            js = json.load(file)
        #for case in steps:
           #     js.append(case)
        js.append(steps[best_case])
        with open(common_json, 'w') as file:
            json.dump(js, file)
    

    
    js.append(result)
    



# In[91]:

optimize()

with open(r'Q:/optymize/optimize.json', 'r') as file:
   js = json.load(file)


# In[92]:


print(js[-1])
