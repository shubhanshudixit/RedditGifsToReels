#   This script -
#   1. Takes the pickle file of GIF data
#   2. Create additional columns that segregate the clips based on their
#    2.a. Orientation
#    2.b. Color Quadrant
#    2.c. Duration
#    2.d Homoginuty -> # of distinct colors or more than 90% homo

#   Libraries
import pandas as pd
import statistics as stats

#   Variables
global col_thres
col_thres = 50
global dur_thres
dur_thres = 2
global dur_thres_1
dur_thres_1 = 5
global dur_thres_2
dur_thres_2 = 10
global hom_val_thres
hom_val_thres = 51
global hom_cols_thres
hom_cols_thres = 15

pickle_fname = 'cat_gif_list'



#   Functions
def col_mean(data):
    b = 1 if stats.mean([col[2] for col in data['Col']]) > col_thres else 0
    r = 1 if stats.mean([col[0] for col in data['Col']]) > col_thres else 0
    g = 1 if stats.mean([col[1] for col in data['Col']]) > col_thres else 0
    qud = str(r) + str(g) + str(b)
    return(qud)

def duraion_cat(data):
    dur_cat = 3
    if data['Duration'] < dur_thres :
        dur_cat = -1
    elif data['Duration'] < dur_thres_1 :
        dur_cat = 1
    elif data['Duration'] < dur_thres_2 :
        dur_cat = 2
    else:
        dur_cat = 3
    return (dur_cat)

def hom_cat(data):
    h_cat = 3
    if data['Homogenity'] < hom_val_thres :
        h_cat = 1
    elif data['Num_of_Distinct_Cols'] < hom_cols_thres :
        h_cat = 3
    else:
        h_cat = 2
    return (h_cat)

def col_avg(data):
    r = stats.mean([col[0] for col in data['Col']])
    g = stats.mean([col[1] for col in data['Col']])
    b = stats.mean([col[2] for col in data['Col']])
    return ((r,g,b))
#   Read Raw Pickle File
raw_data = pd.read_pickle("raw_pickle_1")
# Add the Extra Column
raw_data['Col_Qud'] = str(0)+str(0)+str(0)
raw_data['Dur_Cat'] = 3
raw_data['Hom_Cat'] = 2

# Update the raw data
for i in range(0,len(raw_data) ):
    raw_data.at[i,'Col_Qud'] = col_mean(raw_data.loc[i])
    raw_data.at[i,'Dur_Cat'] = duraion_cat(raw_data.loc[i])
    raw_data.at[i,'Hom_Cat'] = hom_cat(raw_data.loc[i])

raw_data.to_pickle(pickle_fname)

print(raw_data.iloc[9])