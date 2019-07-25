# -*- coding: UTF-8 -*-
import sys
import json
import csv
import copy

##
# Convert to string keeping encoding in mind...
##
def to_string(s):
    try:
        return str(s)
    except:
        #Change the encoding type if needed
        return s.encode('utf-8')


##
# This function converts an item like 
# {
#   "item_1":"value_11",
#   "item_2":"value_12",
#   "item_3":"value_13",
#   "item_4":["sub_value_14", "sub_value_15"],
#   "item_5":{
#       "sub_item_1":"sub_item_value_11",
#       "sub_item_2":["sub_item_value_12", "sub_item_value_13"]
#   }
# }
# To
# {
#   "node_item_1":"value_11",
#   "node_item_2":"value_12",
#   "node_item_3":"value_13",
#   "node_item_4_0":"sub_value_14", 
#   "node_item_4_1":"sub_value_15",
#   "node_item_5_sub_item_1":"sub_item_value_11",
#   "node_item_5_sub_item_2_0":"sub_item_value_12",
#   "node_item_5_sub_item_2_0":"sub_item_value_13"
# }
##

def reduce_item(value, key="Zens",):
    global reduced_item
    
    #Reduction Condition 1
    if type(value) is list:
        i=0
        for sub_item in value:
            reduce_item(sub_item, key+'_'+to_string(i))
            i=i+1

    #Reduction Condition 2
    elif type(value) is dict:
        sub_keys = value.keys()
        for sub_key in sub_keys:
            reduce_item(value[sub_key], key+'_'+to_string(sub_key))
    
    #Base Condition
    else:
        reduced_item[to_string(key)] = to_string(value)

def json_to_csv(json_data, csv_filename):

    processed_data = []
    header = []
    isset_header = False

    for item in json_data:
        reduced_item = [{}]
        exp_item("", item, reduced_item, [0])

        if not isset_header:
            isset_header = True
            for row in reduced_item:
                header += row.keys()

        processed_data.extend(reduced_item)

    header = list(set(header))
    header.sort()

    with open(csv_filename, 'w+') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)


# 用于将JSON的Object 转换成 CSV 比较容易生成的格式 : BY TIM
def exp_item(key, value, rows, indexes=[0]):
    index = indexes[0]
    if isinstance(value, list):
        if len(value) > 0:
            item = value[0]
            exp_item(key, item, rows, indexes)

            for item in value[1:]:
                new_row = copy.deepcopy(rows[index])
                indexes[0] += 1
                rows.append(new_row)
                exp_item(key, item, rows, indexes)
        

    elif isinstance(value, dict):
        for k, v in value.items():
            if key != "":
                exp_item(key+"_"+k, v, rows, indexes)
            else:
                exp_item(k, v, rows, indexes)
    else:
        rows[index].update({key:value})

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print ("\nUsage: python json_to_csv.py <node_name> <json_in_file_path> <csv_out_file_path>\n")
    else:
        #Reading arguments
        node = sys.argv[1]
        json_file_path = sys.argv[2]
        csv_file_path = sys.argv[3]

        fp = open(json_file_path, 'r')
        json_value = fp.read()
        raw_data = json.loads(json_value)
        fp.close()
        
        try:
            data_to_be_processed = raw_data[node]
        except:
            data_to_be_processed = raw_data

        processed_data = []
        header = []
        for item in data_to_be_processed:
            reduced_item = {}
            reduce_item(node, item)

            header += reduced_item.keys()

            processed_data.append(reduced_item)

        header = list(set(header))
        header.sort()

        with open(csv_file_path, 'w+') as f:
            writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in processed_data:
                writer.writerow(row)

        print ("Just completed writing csv file with %d columns" % len(header))