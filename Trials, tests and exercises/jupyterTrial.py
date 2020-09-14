#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gzip
import csv
from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt


# In[2]:


def dict_to_csv(dico):
    L = [] 
    for k,v in dico.items():
        L.append({'Month':k[0],'Year':k[1],'AlterCount':v})
    return L


# In[3]:


def add_values_to_dict(dico,key,val):
    if key in dico.keys():
        dico[key] = dico[key] + val
    else:
        dico[key] = val
    return dico


# In[4]:


def delta(recent, dico, start,end):
    for timestamp in range(start,end,30*24*3600):
        datetimet = datetime.fromtimestamp(timestamp)
        month_year = (datetimet.month,datetimet.year)
        if month_year in dico_time_ancient:
            recent -= dico[month_year]
    return recent


# In[5]:


def timestamp_add_one_year(timestamp):
    return timestamp + + 12*30*24*3600


# In[6]:


def timestamp_add_one_month(timestamp):
    return timestamp + 30*24*3600


# In[7]:


dico_time_ancient = dict()
dico_time = dict()
dico_alter = dict()


# In[8]:


filegz = gzip.open('sample_data/0a0a076ff04b3663aa821ff2a0b2c41a.csv.gz', 'rt')


# In[9]:


csvobj = csv.reader(filegz,delimiter = ',',quotechar="'")


# In[10]:


header = next(csvobj)
first_row = next(csvobj)
id_ego = first_row[0]
time_start = int(first_row[2])
time_end = time_start + 30*24*3600
recent = 0


# In[11]:


for row in csvobj:
    idr,timestamp = row[0],int(row[2])
    if idr not in dico_alter:
        dico_alter[idr] = timestamp
        recent = recent + 1
        datetime_timestamp = datetime.fromtimestamp(timestamp)
        month_year = (datetime_timestamp.month,datetime_timestamp.year)
        month_year_one_year = (datetime_timestamp.month,datetime_timestamp.year+1)
        dico_time_ancient = add_values_to_dict(dico_time_ancient,month_year_one_year,1)
        if timestamp > time_end:
            if month_year in dico_time_ancient:
                recent = delta(recent,dico_time_ancient,timestamp_add_one_year(time_start),timestamp_add_one_year(timestamp))
            dico_time[month_year] = recent
            time_end = timestamp_add_one_month(time_start)
        dico_time[month_year] = recent
        time_start = timestamp


# In[12]:


print(dico_time)


# In[13]:


print(dico_time_ancient)


# In[14]:


csv_file = id_ego + '_alter-count.csv'
csv_columns = ['Month','Year','AlterCount']
dict_data = dict_to_csv(dico_time)


# In[15]:


try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
        print("I/O error")


# In[16]:


dico_df = pd.DataFrame.from_dict(dict_data)


# In[17]:


a4_dims = (11.7, 8.27)
fig, ax = plt.subplots(figsize=a4_dims)
ax = sns.lineplot(x="Month", y="AlterCount",hue="Year",data=dico_df)

