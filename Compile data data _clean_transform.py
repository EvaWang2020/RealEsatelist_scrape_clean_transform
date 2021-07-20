import json
import pandas as pd
import os.path
import glob

# you can customize your file location
path = "C://Documents/realestatelist_"
path1 = "totallist-1.csv"
file_path1 = path+path1

file_list_per_date = glob.glob(f'{path}*-1.txt')
print(file_list_per_date)

if os.path.isfile(file_path1):
    os.remove(file_path1)
else:
    pass


# create a function to find fhe element matching certain patterns 
def extact_property(pattern, list):
    filtered_list = [e for e in list if pattern in e]
    return filtered_list[-1] if len(filtered_list) >= 1 else None

rows = []

#find the start postion of certain string in the file path. It will be used to extract file date showing on file name 
l= path.find('realestatelist_')

for current_file in file_list_per_date:
    with open(current_file,) as f:
        # takes a file object and returns the json object.
        print(str(f))
        json_object = json.load(f)

        # take the lists from the jason file
        listings = json_object['listings']

        for item in listings:
            row = {
                'Price': item['Price'],
                # each list have several items
                'Bedroom_qty': extact_property('bd', item['Structure & size']),
                'Bathroom_qty': extact_property('ba', item['Structure & size']),
                'Floor_size': extact_property('sf', item['Structure & size']),
                'Land_size': extact_property('ft', item['Structure & size']),
                'Address': item['Address'],
                'City_region': item['City'][0] if len(item['City']) > 1 else None,
                'City': item['City'][-1] if len(item['City'])>=1 else None,
                'List_type': item['list_Type'],
                'Date':current_file[l+15:l+25],   # extract the date from current_file. Depending on your file path, the start number and ending numbers are different 
            }
            rows.append(row)

# Creates DataFrame object from dictionary by columns or by index allowing dtype specification.
df = pd.DataFrame.from_dict(rows)

# remove text from the columns and keep only values 
df['Bedroom_qty']= df.Bedroom_qty.str.split(' ').str[0]
df['Bathroom_qty']= df.Bathroom_qty.str.split(' ').str[0]
df['Floor_size']= df.Floor_size.str.split(' ').str[0]

# extract widith and depth of the land
df['Land_width']= df.Land_size.str.split('x').str[0]
df['Land_depth']= df.Land_size.str.split('x').str[1]
df['Land_depth']= df.Land_depth.str.split(' ').str[1]
df=df.drop(columns=['Land_size'], axis = 1)

# When there is no value for column 'bd', 'ba', 'size', it means that list is advertisment and could apear mutiple times the same day. We should remove them, but we will keep the only list with bedroom and bathroom quantity
df = df[df['Bedroom_qty'].notnull()]   # if you want to exclude list for land, use "df =df.dropna(subset=['Bathroom_qty','Bedroom_qty'], how='all')"
df = df.drop_duplicates()  

# drop the list with both empty empty land size and empty land width. It is likely a imcomplte list for land 
df =df.dropna(subset=['Floor_size','Land_width'], how='all')                           
# print(df)

df.to_csv(file_path1, mode='a', header=True,index=False)                                

