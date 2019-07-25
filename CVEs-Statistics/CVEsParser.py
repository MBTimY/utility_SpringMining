# -*- coding: UTF-8 -*
from zipfile import ZipFile
import os
import sys
import json
import re
import json_to_csv

def get_all_fille_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files: 
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                file_paths.append(file_path)
    return file_paths

def extract_zipfile(zip_name): 
    file_entries = {}
    try:
        with ZipFile(zip_name) as ZIP:
            for file_entity in ZIP.filelist:
                file_entries[file_entity.filename] = ZIP.read(file_entity)
    except Exception as e:
        print ( zip_name )
        raise e
    
    return file_entries

def extract_vendor_info(cve_descriptor):
    vendor_list = []
    if 'affects' in cve_descriptor.keys():
        for vendor in cve_descriptor['affects']['vendor']['vendor_data']:
            if 'product' in vendor.keys():
                vendor_list.append(vendor)
    return vendor_list

def extract_production_info(vendor_list):
    product_list = []
    framwork_pr = re.compile("spring", re.I)
    for vendor in vendor_list:
        product_data = vendor['product']['product_data']
        for product in product_data:
            if framwork_pr.search(product['product_name']) == None:
                continue
            product.pop("version", None) if 'version' in product.keys() else product
            product_list.append(product)
    
    return product_list


def handle_json_data(json_plain):
    try:
        CVEs_Discriptor = json.loads(json_plain)
    except Exception as e: 
        raise e
    CVEs_Collect = []
    for CVE_Discriptor in CVEs_Discriptor['CVE_Items']:
        CVE_Discriptor = CVE_Discriptor['cve']
        vendor_list = extract_vendor_info(CVE_Discriptor)
        product_list = extract_production_info(vendor_list)
        if len(product_list) > 0:
            CVE_Discriptor.pop("affects", None)
            CVE_Discriptor.pop("problemtype", None)
            CVE_Discriptor.pop("references", None)
            CVE_Discriptor['product_list'] = product_list
            CVEs_Collect.append(CVE_Discriptor)
    return CVEs_Collect

def main():
    CVEs_Directory = sys.argv[1]
    files = get_all_fille_paths(CVEs_Directory)
    CVEs_Collect = []
    for filename in files: 
        if not filename.endswith("zip"):
            continue
        decompress_list = extract_zipfile(filename)
        for filename, json_plain in decompress_list.items():
            CVEs = handle_json_data(json_plain)
            if len(CVEs) > 0:
                CVEs_Collect.extend(CVEs)

    json_to_csv.json_to_csv(CVEs_Collect, "SpringCVEs.csv")

if __name__ == "__main__":
    main()